#!/bin/bash

cd /home/ubuntu/pongpongBack/WebService

source /home/ubuntu/pongpongBack/myprojectenv/bin/activate
source /home/ubuntu/.env

echo "Stopping any existing Daphne servers..."
pkill -f 'daphne'
rm -f nohup.out

sleep 2

echo "Starting Daphne server..."
nohup daphne WebService.asgi:application &
echo "Daphne has been started in the background."