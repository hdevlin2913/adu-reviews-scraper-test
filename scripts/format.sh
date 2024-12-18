#!/usr/bin/env bash

set -x

ruff format scraper

ruff check scraper --select I --fix

black  --skip-string-normalization scraper
