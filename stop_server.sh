#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

PID_FILE="server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if [ -z "$PID" ]; then
        echo "PID file $PID_FILE is empty. Removing it."
        rm "$PID_FILE"
        echo "Please check manually if the process 'python3 main.py' is running."
        exit 1
    fi

    echo "Attempting to stop server with PID $PID..."
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID"
        sleep 2 # Wait for graceful shutdown

        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Server did not stop gracefully. Forcefully stopping PID $PID..."
            kill -9 "$PID"
            sleep 1
        fi

        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Failed to stop process with PID $PID. Please check manually."
        else
            echo "Server with PID $PID stopped."
        fi
        rm "$PID_FILE"
    else
        echo "Process with PID $PID not found. It might have already stopped or the PID file is stale."
        rm "$PID_FILE"
    fi
else
    echo "PID file ($PID_FILE) not found."
    echo "Attempting to find and stop 'python3 main.py' process by name..."
    # pgrep returns 0 if process(es) found, 1 otherwise
    if pgrep -f "python3 main.py" > /dev/null; then
        pkill -f "python3 main.py"
        # Check if pkill was successful
        sleep 1
        if pgrep -f "python3 main.py" > /dev/null; then
            echo "Failed to stop all 'python3 main.py' processes. Please check manually."
        else
            echo "Successfully stopped 'python3 main.py' process(es) found by name."
        fi
    else
        echo "No 'python3 main.py' process found running."
    fi
fi
