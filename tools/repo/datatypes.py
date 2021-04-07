from typing import Dict, List, Optional, Union

from pydantic import BaseModel, BaseSettings, Field, validator


class BuildSystem(BaseModel):
    """Pyproject files always contain a "[build-system]" section.

    References:
      * <https://python-poetry.org/docs/pyproject/#poetry-and-pep-517>
    """

    requires: List[str]
    build_backend: str = Field(..., alias="build-backend")


class Package(BaseModel):
    """A package can be declared as a dictionnary.

    References:
      *  <https://python-poetry.org/docs/pyproject/#packages>
    """

    include: str
    format: Optional[str] = None
    from_: Optional[str] = Field(default=None, alias="from")


class Dependency(BaseModel):
    """A dependency found in a pyproject.toml file.

    Dependencies can be found in:
      - `[tool.poetry.dependencies]`
      - `[tool.poetry.dev-dependencies]`

    Note: A dependency can also be declared as a string.

    References:
      * <https://python-poetry.org/docs/pyproject/#dependencies-and-dev-dependencies>
    """

    version: Optional[str] = None
    path: Optional[str] = None
    optional: Optional[bool] = None
    git: Optional[str] = None
    branch: Optional[str] = None
    extras: Optional[List[str]] = None
    python: Optional[str] = None
    markers: Optional[str] = None


class Pyproject(BaseModel):
    """A complete pyproject.toml file.

    References:
        * [The pyproject.toml file](https://python-poetry.org/docs/pyproject/)
        * [Poetry pyproject.toml file](https://github.com/python-poetry/poetry/blob/master/pyproject.toml)
    """

    # Docs: <https://python-poetry.org/docs/pyproject/#name>
    name: str
    # Docs: <https://python-poetry.org/docs/pyproject/#version>
    version: str
    # Docs: <https://python-poetry.org/docs/pyproject/#description>
    description: Optional[str] = None
    # Docs: <https://python-poetry.org/docs/pyproject/#license>
    license: Optional[str] = None
    # Docs: <https://python-poetry.org/docs/pyproject/#authors>
    authors: List[str] = []
    # Docs: <https://python-poetry.org/docs/pyproject/#maintainers>
    maintainers: List[str] = []
    # Docs: <https://python-poetry.org/docs/pyproject/#readme>
    readme: Optional[str] = None
    # Docs: <https://python-poetry.org/docs/pyproject/#homepage>
    homepage: Optional[str] = None
    # Docs: <https://python-poetry.org/docs/pyproject/#repository>
    repository: Optional[str] = None
    # Docs: <https://python-poetry.org/docs/pyproject/#documentation>
    documentation: Optional[str] = None
    # Docs: <https://python-poetry.org/docs/pyproject/#keywords>
    keywords: List[str] = []
    # Docs: <https://python-poetry.org/docs/pyproject/#classifiers>
    classifiers: List[str] = []
    # Docs: <https://python-poetry.org/docs/pyproject/#packages>
    packages: List[Union[str, Package]] = []
    # Docs: <https://python-poetry.org/docs/pyproject/#include-and-exclude>
    include: List[str] = []
    exclude: List[str] = []
    # Docs: <https://python-poetry.org/docs/pyproject/#dependencies-and-dev-dependencies>
    dependencies: Dict[str, Union[str, Dependency]]
    dev_dependencies: Dict[str, Union[str, Dependency]] = Field(
        {}, alias="dev-dependencies"
    )
    # Docs: <https://python-poetry.org/docs/pyproject/#scripts>
    scripts: Dict[str, str] = {}
    # Docs: <https://python-poetry.org/docs/pyproject/#extras>
    extras: Dict[str, List[str]] = {}
    # Docs: <https://python-poetry.org/docs/pyproject/#plugins>
    plugins: Dict[str, Dict[str, str]] = {}
    # Docs: <https://python-poetry.org/docs/pyproject/#urls>
    urls: Dict[str, str] = {}
    # Docs: <https://python-poetry.org/docs/pyproject/#poetry-and-pep-517>
    build_system: Optional[BuildSystem] = Field(None, alias="build-system")


class RepoConfig(BaseSettings):
    prefix: Optional[str] = None

    class Config:
        env_prefix = "repo_"
        case_sensitive = False

    @validator("prefix", pre=True)
    def set_none_when_empty(cls, v):  # type: ignore
        return v or None
