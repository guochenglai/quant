#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Run the Python script in the background using nohup
# stdout and stderr will be redirected to output.log
echo "Starting the quantitative trading system..."
nohup python3 main.py > output.log 2>&1 &

echo "Quantitative trading system started in the background."
echo "Output is being logged to output.log"
