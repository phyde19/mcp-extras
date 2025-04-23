#!/bin/bash

venv_path="$(pwd)/.venv"

# create venv if doesn't exist
if [[ ! -d "$venv_path" ]]; then
    echo "creating new venv at $venv_path"
    python -m venv .venv
else
    echo "venv found at $venv_path"
fi

# activate venv if inactive
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "activating venv at $venv_path"
    source "$venv_path/bin/activate"
else
    echo "venv already activated"
    echo "run 'deactivate' to deactivate"
fi
