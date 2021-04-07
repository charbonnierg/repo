#!/usr/bin/env bash

set -eu

ROOT=$(realpath $(dirname $(dirname $(echo "$0"))))
PYTHON="${PYTHON:-"python3"}"

cd $ROOT

# Create virtual environment if it does not exist yet
if [ ! -d ".venv/" ]; then
  echo -e "Creating virtual environment in $ROOT/.venv directory"
  $PYTHON -m venv .venv
fi

# Activate virtual environment
echo -e "Activating virtual environment"
. .venv/bin/activate
