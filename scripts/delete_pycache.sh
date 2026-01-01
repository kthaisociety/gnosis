#!/bin/bash
# Recursively deletes all pycache from where you run this
find . -type d -name "__pycache__" -exec rm -r {} +
