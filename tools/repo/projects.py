from __future__ import annotations

import pathlib
import re
import shutil
from configparser import ConfigParser
from itertools import chain
from pathlib import Path
from shlex import quote
from typing import Dict, Iterator, List, Optional, Union

from loguru import logger
from stdlib_list import stdlib_list
from tomlkit import dumps, parse

from .datatypes import Dependency, Pyproject, RepoConfig
from .errors import DirectoryNotFoundError, PackageNotFoundError, PyprojectNotFoundError
from .utils import current_directory, run


class Project:
    """An object representation of a python project managed using Poetry."""

    def __init__(self, root: Union[Path, str]) -> None:
        """Create a new instance of Project from given root directory.

        Arguments:
            * root: The root path of the project. Can be a string or a `pathlib.Path` object.

        Raises:
            * DirectoryNotFoundError: When project directory does not exist.
            * PyprojectNotFoundError: When a pyproject.toml cannot be found in project root directory.
            * ValidationError: When a pyproject.toml is not valid.
        """
        # Store the canonical path ('.' and '..' are resolved and variables are expanded)
        self.root = Path(root).resolve().absolute()
        # Ensure path exists
        if not self.root.exists():
            raise DirectoryNotFoundError(f"Directory {self.root} does not exist")
        self.pyproject_file = self.root / "pyproject.toml"
        # Ensure pyproject.toml (we don't use try/catch to avoid long traceback)
        if not self.pyproject_file.exists():
            raise PyprojectNotFoundError(f"File {self.pyproject_file} does not exist")
        # We can now read without try/catch
        self.pyproject_content = self.pyproject_file.read_text()
        # If file content is not valid, a ValidationError is
        self._pyproject = parse(self.pyproject_content)
        self.pyproject = Pyproject(**self._pyproject["tool"]["poetry"])

    def __repr__(self) -> str:
        return f"Project(name={self.pyproject.name}, root={self.root})"

    @property
    def src(self) -> List[str]:
        sources = []
        if not self.pyproject.packages:
            default = self.root / self.pyproject.name.replace("-", "_")
            if default.exists():
                return [str(default.resolve())]
            else:
                return []
        for pkg in self.pyproject.packages:
            if isinstance(pkg, str):
                default = Path(self.root / pkg)
                if default.exists():
                    sources.append(default)
                else:
                    default = Path(self.root / "src" / pkg)
                    if default.exists():
                        sources.append(default)
                continue
            if pkg.from_:
                root = self.root / pkg.from_
            else:
                root = self.root
            default = root / pkg.include
            if default.exists():
                sources.append(default)
        return [str(source.resolve()) for source in sources]

    @property
    def private_dependencies(self) -> List[Project]:
        """Private dependencies are dependencies that cannot be fetched from external repositories.

        Nested private dependencies are not handled.
        """
        dependencies = []
        # Path are resolved when creating a Project instance
        # In order to successfully resolve path of private dependencies
        # we must be located in the root directory of the project.
        with current_directory(self.root):
            # Private dependencies are dependencies
            for dependency in self.pyproject.dependencies:
                # That are also declared as development dependencies
                if dependency in self.pyproject.dev_dependencies:
                    # We can safely ignore type because if .path attribute does not exist we catch the AttributeError.
                    dep: Dependency = self.pyproject.dev_dependencies[dependency]  # type: ignore
                    # And that have a "path" attribute
                    try:
                        path = dep.path
                    except AttributeError:
                        continue
                    # If the path attribute does exist, then this is a private dependency
                    if path:
                        dependencies.append(Project(path))
        return dependencies

    @property
    def wheels(self) -> Iterator[Path]:
        return self.root.glob("dist/*.whl")

    @property
    def sdists(self) -> Iterator[Path]:
        return self.root.glob("dist/*.tar.gz")

    @property
    def dist_files(self) -> Iterator[Path]:
        return chain(self.wheels, self.sdists)

    @classmethod
    def from_pyproject(cls, pyproject: Union[Path, str]) -> Project:
        """Create a new instance of Project from `pyproject.toml` location.

        Arguments:
            * pyproject: The path to `pyproject.toml` file. Can be a string or a `pathlib.Path` object.

        Raises:
            * PyprojectNotFoundError: When a pyproject.toml cannot be found in project root directory.
            * ValidationError: When a pyproject.toml is not valid.
        """
        return cls(Path(pyproject).parent)

    def install(self, extras: List[str] = [], skip: List[str] = []) -> None:
        """Install package using `poetry install`."""
        if self.pyproject.name in skip:
            return
        with current_directory(self.root):
            logger.debug(f"Installing project {self.pyproject.name}")
            extras_opts = " ".join(["-E " + quote(extra) for extra in extras])
            run(f"poetry install {extras_opts}")

    def build(self, format: Optional[str] = None) -> None:
        """Build package using `poetry build`."""
        with current_directory(self.root):
            format_opt = f"--format {format}" if format else ""
            logger.debug(f"Building package {self.pyproject.name}")
            run(f"poetry build {format_opt}")

    def test(
        self, markers: List[str] = [], exprs: List[str] = [], add_src: List[str] = []
    ) -> None:
        """Run tests using `pytest`."""
        marker_opts = " ".join((f"-m {quote(marker)}" for marker in markers))
        expr_opts = " ".join((f"-m {quote(expr)}" for expr in exprs))
        cov_opts = " ".join((f"--cov {quote(src)}" for src in set(self.src + add_src)))
        with current_directory(self.root):
            cmd = f"pytest {cov_opts} {expr_opts} {marker_opts}"
            logger.debug(f"Testing package {self.pyproject.name} with command: {cmd}")
            run(cmd)

    def lint(self) -> None:
        """Lint package and tests using `flake8`."""
        with current_directory(self.root):
            logger.debug(f"Linting package {self.pyproject.name}")
            run(f"flake8 {' '.join(self.src)} tests/")

    def format(self) -> None:
        """Format package and tests using `isort` and `black`."""
        with current_directory(self.root):
            logger.debug(f"Formatting package {self.pyproject.name}")
            run(f"black {' '.join(self.src)} tests/")
            run(f"isort {' '.join(self.src)} tests/")

    def bump(self, version: str, local_prefix: Optional[str] = None) -> None:
        """Bump package version using `poetry version`."""
        with current_directory(self.root):
            logger.debug(f"Bumping package {self.pyproject.name} to version {version}")
            self.set_version(version)
            if local_prefix:
                pattern = rf'({local_prefix}-\w*)\s?=\s?(.?)"\^?(.*)"(.*)'
                regexp = re.compile(pattern, re.MULTILINE)
                self.pyproject_content = regexp.sub(
                    f'\\1 = \\2"^{version}"\\4', self.pyproject_content
                )
                self.pyproject_file.write_text(self.pyproject_content)
            run("poetry lock --no-update")

    def clean(self) -> None:
        """Clean a package dist directory."""
        dist = self.root / "dist"
        shutil.rmtree(dist, ignore_errors=True)

    def update(self) -> None:
        """Update package dependencies using `poetry udpate`."""
        with current_directory(self.root):
            logger.debug(f"Updating package {self.pyproject.name}")
            run("poetry update")

    def typecheck(self) -> None:
        """Run `mypy` against package source."""
        logger.debug(f"Typechecking package {self.pyproject.name}")
        sources = " ".join(self.src)
        run(f"mypy {sources}")

    def export_requirements(
        self, requirements: Union[str, Path] = "requirements.txt", mode: str = ">"
    ) -> None:
        """Export dependencies into a requirements file."""
        # Just to be sure...
        if mode not in (">>", ">"):
            mode = ">"
        with current_directory(self.root):
            run(f"poetry export --without-hashes {mode} {requirements}")

    def export(self, clean: bool = True) -> None:
        """Export packages and its dependencies to directory."""
        logger.debug(f"Exporting package {self.pyproject.name} and its dependencies")
        if clean:
            self.clean()
        export = self.root / "export"
        requirements = export / "requirements.txt"
        shutil.rmtree(export, ignore_errors=True)
        export.mkdir(parents=True, exist_ok=True)
        self.build()
        for wheel in self.wheels:
            shutil.move(str(wheel), export / wheel.name)
        shutil.rmtree(self.root / "dist")
        self.export_requirements(requirements)
        for dependency in self.private_dependencies:
            dependency.build()
            for wheel in dependency.wheels:
                shutil.move(str(wheel), export / wheel.name)
            dependency.export_requirements(requirements, mode=">>")
        _requirements = requirements.read_text()
        requirements.write_text(
            "\n".join(
                [
                    requirement
                    for requirement in _requirements.split("\n")
                    if "@" not in requirement
                ]
            )
        )
        with current_directory(export):
            run(f"pip download -r {requirements}")
            requirements.unlink()
        dist = Path("dist")
        dist.mkdir(exist_ok=True, parents=True)
        out = dist / f"{self.pyproject.name}-{self.pyproject.version}"
        shutil.make_archive(
            str(out),
            format="zip",
            root_dir=export,
        )
        shutil.rmtree(export)

    def set_version(self, value: str) -> None:
        self._pyproject["tool"]["poetry"]["version"] = value
        self.pyproject = Pyproject.construct(**self._pyproject["tool"]["poetry"])
        self.pyproject_content = dumps(self._pyproject)
        self.pyproject_file.write_text(self.pyproject_content)

    def set_authors(self, values: List[str]) -> None:
        self._pyproject["tool"]["poetry"]["authors"] = [
            value.lower() for value in values
        ]
        self.pyproject = Pyproject.construct(**self._pyproject["tool"]["poetry"])
        self.pyproject_content = dumps(self._pyproject)
        self.pyproject_file.write_text(self.pyproject_content)

    def set_include_packages(self, values: List[str]) -> None:
        self._pyproject["tool"]["poetry"]["packages"] = [
            {"include": value} for value in values
        ]
        self.pyproject = Pyproject.construct(**self._pyproject["tool"]["poetry"])
        self.pyproject_content = dumps(self._pyproject)
        self.pyproject_file.write_text(self.pyproject_content)


class Monorepo(Project):
    def __init__(self, root: Union[Path, str]) -> None:
        super().__init__(root)
        self._projects: List[Project] = [
            Project.from_pyproject(path)
            for path in chain(
                self.root.glob("libraries/**/pyproject.toml"),
                self.root.glob("plugins/**/pyproject.toml"),
                self.root.glob("applications/**/pyproject.toml"),
            )
        ]
        self.config = self.parse_config_from_setupcfg(self.root / "setup.cfg")

    @staticmethod
    def parse_config_from_setupcfg(path: pathlib.Path) -> RepoConfig:
        if path.exists():
            setupcfg_parser = ConfigParser()
            setupcfg_parser.read_string(path.read_text())
            setupcfg_config = {
                s: dict(setupcfg_parser.items(s)) for s in setupcfg_parser.sections()
            }
            if setupcfg_config.get("tool:repo"):
                return RepoConfig(**setupcfg_config["tool:repo"])
        return RepoConfig()

    @property
    def project_names(self) -> List[str]:
        return [project.pyproject.name for project in self._projects]

    @property
    def projects(self) -> Dict[str, Project]:
        return {project.pyproject.name: project for project in self._projects}

    def get_packages(self, packages: Optional[List[str]] = None) -> List[Project]:
        """Get a subset of packages from name."""
        if not packages:
            return self._projects
        unknown = [name for name in packages if name not in self.project_names]
        if len(unknown) > 1:
            raise PackageNotFoundError(f"Cannot find packages: {', '.join(unknown)}")
        elif unknown:
            raise PackageNotFoundError(f"Cannot find package {unknown[0]}")
        return [self.projects[package] for package in packages]

    def install_packages(
        self, packages: List[str] = [], extras: List[str] = [], skip: List[str] = []
    ) -> None:
        projects = self.get_packages(packages)
        for project in projects:
            for dep in project.private_dependencies:
                if dep not in skip:
                    self.install_packages([dep.pyproject.name], [], skip)
                    skip.append(dep.pyproject.name)
                    skip.extend(
                        [
                            nested_dep.pyproject.name
                            for nested_dep in dep.private_dependencies
                        ]
                    )
            if project not in skip:
                project.install(extras=extras, skip=skip)
                skip.append(project.pyproject.name)
        if not packages:
            self.install()

    def build_packages(
        self, packages: List[str] = [], format: Optional[str] = None
    ) -> None:
        projects = self.get_packages(packages)
        out = self.root / "dist"
        out.mkdir(exist_ok=True)
        for project in projects:
            project.build(format=format)
            for _file in project.dist_files:
                shutil.move(str(_file), out / _file.name)
        if not packages:
            self.build()

    def clean_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            project.clean()
        if not packages:
            self.clean()

    def test_packages(
        self, packages: List[str] = [], markers: List[str] = [], exprs: List[str] = []
    ) -> None:
        if not packages:
            all_sources = []
            for package in self.get_packages():
                all_sources += package.src
        else:
            for project in self.get_packages(packages):
                project.test(markers=markers, exprs=exprs)

    def bump_packages(self, version: str) -> None:
        for project in self.get_packages():
            project.bump(version, self.config.prefix)
        self.bump(version)

    def lint_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            project.lint()
        if not packages:
            self.lint()

    def typecheck_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            project.typecheck()
        if not packages:
            self.typecheck()

    def format_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            project.format()
        if not packages:
            self.format()

    def update_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            project.update()
        if not packages:
            self.update()

    def new_library(self, name: str) -> None:
        self._new_project(name, "libraries")

    def new_plugin(self, name: str) -> None:
        self._new_project(name, "plugins")

    def new_app(self, name: str) -> None:
        self._new_project(name, "applications")

    def _new_project(self, name: str, folder: str) -> None:
        # Create project directory
        project_root = self.root / folder / name
        project_root.mkdir(parents=True, exist_ok=False)
        # Create pyproject.toml
        with current_directory(project_root):
            run(f"poetry init -n --name {quote(name)}")
        # Bootstrap test directory
        project_tests = project_root / "tests"
        project_tests.mkdir(exist_ok=False, parents=False)
        conftest = project_tests / "conftest.py"
        conftest.touch()
        # Bootstrap source directory
        sources_dir = name.replace(f"{self.config.prefix}-", "").replace("-", "_")
        if sources_dir in stdlib_list():
            logger.warning(
                f"Generated module with name {sources_dir}. "
                f"The {sources_dir} module already exists in the standard library."
            )
        # Declare variable type
        to_include: Optional[str]
        if self.config.prefix:
            project_sources = (
                project_root / self.config.prefix.replace("-", "_") / sources_dir
            )
            to_include = self.config.prefix.replace("-", "_")
        else:
            project_sources = project_root / sources_dir
            to_include = None
        project_sources.mkdir(parents=True, exist_ok=False)
        init_file = project_sources / "__init__.py"
        init_file.touch()
        # Create project instance
        project = Project(project_root)
        # Update project version
        project.set_version(self.pyproject.version)
        # Update project authors
        project.set_authors(self.pyproject.authors)
        # Update project packages
        if to_include:
            project.set_include_packages([to_include])

    def lint(self) -> None:
        """Lint package and tests using `flake8`."""
        with current_directory(self.root):
            logger.debug(f"Linting package {self.pyproject.name}")
            run("flake8 tools")

    def format(self) -> None:
        """Format package and tests using `isort` and `black`."""
        with current_directory(self.root):
            logger.debug(f"Formatting package {self.pyproject.name}")
            run("black tools")
            run("isort tools")
