#!/usr/bin/env bash

set -x

ruff check src
mypy src

black src --check
