#!/bin/bash
# CurioShelf launcher script

# Default to Qt UI, but allow command line arguments to be passed through
poetry run python main.py "$@"
