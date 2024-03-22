#!/bin/bash

cd /home/ubuntu/pongpongBack/WebService

source /home/ubuntu/pongpongBack/myprojectvenv/bin/activate
source /home/ubuntu/.env

echo "Stopping any existing Daphne servers..."
pkill -f 'daphne'
rm -f nohup.out

sleep 2

echo "Starting Daphne server..."
nohup daphne -e ssl:8000:privateKey=/home/ubuntu/pongpongBack/myprojectenv/lib/python3.10/site-packages/sslserver/certs/development.key:certKey=/home/ubuntu/pongpongBack/myprojectenv/lib/python3.10/site-packages/sslserver/certs/development.crt WebService.asgi:application &

echo "Daphne has been started in the background."