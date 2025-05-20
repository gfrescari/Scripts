#!/bin/bash

while true
do
    current_time=$(date +%H:%M)

    if [ "$current_time" == "13:00" ]; then
        echo "Hello World"
        # Sleep for 61 seconds to avoid printing multiple times within the same minute
        sleep 61
    else
        # Sleep for 30 seconds before checking the time again
        sleep 30
    fi
done
