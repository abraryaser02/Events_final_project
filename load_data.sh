#!/bin/sh

echo 'loading data'

time python3 load_data.py --db=postgresql://postgres:postgres@localhost:5435/backend_dev --user_rows=1000000 --event_rows=1000000

echo 'finished loading'