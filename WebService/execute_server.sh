#!/bin/bash

cd /home/ubuntu/pongpongBack/WebService

source /home/ubuntu/pongpongBack/myprojectenv/bin/activate
source /home/ubuntu/.env

echo "Stopping any existing Daphne servers..."
pkill -f 'daphne'
rm -f nohup.out

sleep 2

echo "Starting Daphne server..."
nohup daphne -e ssl:8000:privateKey=/etc/letsencrypt/live/pongpongback.duckdns.org/fullchain.pem:certKey=/etc/letsencrypt/live/pongpongback.duckdns.org/privkey.pem WebService.asgi:application &

echo "Daphne has been started in the background."