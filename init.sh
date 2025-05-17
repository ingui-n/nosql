#!/bin/bash

# Init keyfile
chmod +x init-keyfile.sh
sudo ./init-keyfile.sh

# Start docker compose
docker-compose up -d

# Setup cluster
chmod +x init-cluster.sh
./init-cluster.sh
