#!/usr/bin/env bash

set -eu

. $(dirname "$0")/env.sh

# Install root package
echo -e "Installing monorepo using poetry install"
poetry install
# Install all packages
echo -e "Installing all packages"
repo install
# Install pre-commit hooks
echo -e "Installing pre-commit hooks"
pre-commit install 
# Install pre-commit commit-msg hooks
pre-commit install --hook-type commit-msg
# Install jupyter kernel
python -m ipykernel install --user --name python-samples --display-name "python-samples ($(python --version))"
