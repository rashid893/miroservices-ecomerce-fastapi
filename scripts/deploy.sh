#!/bin/bash

cd /home/ubuntu/miroservices-ecomerce-fastapi || exit

# Ensure latest code
git pull origin master

# Stop old containers
docker compose down

# Rebuild & run
docker compose up --build -d
