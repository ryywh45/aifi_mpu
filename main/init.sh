#!/bin/bash

# Run this script under the "main" directory
# Using "source init.sh"

CURR_DIR=$(pwd)

echo "export PYTHONPATH="$CURR_DIR:$PYTHONPATH"" >> ~/.bashrc
echo "Added "export PYTHONPATH=$CURR_DIR:$PYTHONPATH" to ~/.bashrc"
source ~/.bashrc