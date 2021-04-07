#!/usr/bin/env bash

set -e

find . \( -name '__pycache__' -or -name '*.pyc' -or -name 'dist' \) -exec rm -rf {} +
