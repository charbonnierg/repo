from pathlib import Path

import pytest
from repo import Project


@pytest.fixture
def project_repo() -> Project:
    return Project(Path(__file__).parent.parent.parent.parent)
