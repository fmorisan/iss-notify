#!/bin/sh
PYTHONPATH=$PYTHONPATH:.
python schema.py
python server.py &
huey_consumer -w 4 tasks.huey
