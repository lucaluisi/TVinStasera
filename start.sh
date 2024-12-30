#!/bin/bash

python -u /usr/src/app/bot.py &

cron -f &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?