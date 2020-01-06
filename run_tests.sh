#!/bin/sh
set -e
mypy .
PYTHONPATH=. robot atest/
