#!/bin/bash

# How many seconds to wait between runs
INTERVAL=10

while true; do
    python manage.py job_tick
    sleep $INTERVAL
done
