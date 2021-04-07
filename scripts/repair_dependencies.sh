#!/usr/bin/env bash

set -eu

. "$(dirname $0)/env.sh"

find . -name 'poetry.lock' -delete

repo install
