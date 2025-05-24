#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

PID_FILE="server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Server is already running with PID $PID."
        echo "Please use stop_server.sh to stop it first."
        exit 1
    else
        echo "Found stale PID file. Removing it."
        rm "$PID_FILE"
    fi
fi

# Run the Python script in the background using nohup
# stdout and stderr will be redirected to output.log
echo "Starting the quantitative trading system..."
nohup python3 main.py > output.log 2>&1 &
PROC_ID=$!

echo "$PROC_ID" > "$PID_FILE"

echo "Quantitative trading system started in the background with PID $PROC_ID."
echo "Output is being logged to output.log"
echo "PID stored in $PID_FILE"
