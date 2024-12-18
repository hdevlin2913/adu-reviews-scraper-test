#!/usr/bin/env bash

set -x

ruff check scraper
mypy scraper

black scraper --check
