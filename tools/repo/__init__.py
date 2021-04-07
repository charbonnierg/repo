"""
The repo package can be used from the command line using the `repo` command.

Example usage:

```bash
repo --help
# Or
python -m repo --help
```

It can also be used from Python using the `Project` and `PyProject` classes.

Example usage:

```python
from repo import Project

project = Project("path-to-directory")

# Build the project (optionnally specify format, by defaults "sidst" and "wheel" are used)
project.build(format="wheel")

# Install the project
project.install(extras=[])

# Lint the project
project.lint()

# Format the project
project.format()

# Run mypy against the project sources
project.typecheck()

# Test the project
project.test()

# Bump the project version
project.bump("new_version")
```
"""
from .projects import Project, Pyproject

__all__ = ["Project", "Pyproject"]
