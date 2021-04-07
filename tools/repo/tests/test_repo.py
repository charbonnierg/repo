from repo import Project


def test_repo_name(project_repo: Project):
    assert project_repo.pyproject.name == "quara-repo"
