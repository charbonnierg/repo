# Samples Python Monorepo

This repository holds all Python software development related to the samples project.

It contains several python packages, which can be built and distributed independently from each other.

## Prerequisites

Test

This repository leverages [`poetry`](https://python-poetry.org/docs/basic-usage/), a python dependency management tool in order to install and build all packages.

Make sure you have [`poetry`](https://python-poetry.org/docs/) installed before going further.

> Note: You can install poetry following the [official documentation](https://python-poetry.org/docs/#installation).

To make sure that you're ready, open a terminal, and type the command:

```bash
poetry --version
```

> Warning: Never install `poetry` using `pip` as it will break your environment !

Once you've got `poetry` installed, make sure it is configured to **NOT** create virtual environments:

```bash
poetry config virtualenvs.create false
```

## Installing all packages

A convenience script can be used to install all dependencies in one go:

```bash
# Clone the repo
git clone https://github.com/charbonnierg/samples.git
# Go into the root directory of the repo
cd samples
# Create your virtual environment
./scripts/boootstrap.sh
```

The development package comes with a Command Line Application that is useful to develop other librairies or applications.

Run the `repo` command to learm more about its features:

```bash
repo --help
```

### Installing the packages for development

In order to install all packages, run the following command:

```bash
repo install
```

### Running the tests

Tests are ran using `pytest` using the following command:

```bash
repo test
```

> Note: You can optionnally specify pytest markers: `repo test -m "databases"` or `repo test -m "not databases"` for example.

### Linting the code

Code is linted using `flake8` using the following command:

```bash
repo lint
```

### Formatting the code

Code is formatted using `black` using the following command:

```bash
repo format
```

### Adding a new package

In order to add a new package, the following files must be present:

- `pyproject.toml`: Each package must have a valid poetry configuration file named `pyproject.toml`.
- `tests/`: Each package must have a test directory, even if empty. (Use `.gitkeep` files if you need!)

Take a look at existing packages to create a new one and open an issue on Azure Devops if you encounter any problem.

Once you created your files, simple run `repo install` to install your newly created package.
