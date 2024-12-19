#!/usr/bin/env bash

set -x

ruff format src

ruff check src --select I --fix

black  --skip-string-normalization src
