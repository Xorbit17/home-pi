#!/bin/bash

# How many seconds to wait between runs
INTERVAL=30

while true; do
    python manage.py job_tick
    sleep $INTERVAL
done
