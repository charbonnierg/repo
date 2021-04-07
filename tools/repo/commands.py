import shutil

from repo.projects import Monorepo

from .utils import current_directory, run


def export_packages(repo: Monorepo) -> None:
    """Export packages using poetry and pip for offline usage."""
    requirements = repo.root / "export.requirements"
    export_directory = repo.root / "dist"
    shutil.rmtree(export_directory, ignore_errors=True)
    export_directory.mkdir(exist_ok=True)
    for package in repo.get_packages():
        with current_directory(package.root):
            shutil.rmtree(package.root / "dist", ignore_errors=True)
            package.build()
            wheels = package.root.glob("dist/*.whl")
            for wheel in wheels:
                shutil.move(str(wheel), export_directory / wheel.name)
            shutil.rmtree(package.root / "dist")
            run(f"poetry export >> {requirements}")
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
    with current_directory(export_directory):
        run(f"pip download -r {requirements}")
    requirements.unlink()
    out_name = repo.pyproject.name + "-" + repo.pyproject.version
    shutil.make_archive(out_name, format="zip", root_dir=export_directory)
    out_file = repo.root / "dist" / (out_name + ".zip")
    shutil.move(out_name + ".zip", str(out_file))
