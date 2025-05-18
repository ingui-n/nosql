#!/bin/bash

# Init keyfile
chmod +x init-keyfile.sh
sudo ./init-keyfile.sh

# Start docker compose
docker-compose up -d

echo "Waiting 5 seconds..."
sleep 5

# Setup cluster
chmod +x init-cluster.sh
./init-cluster.sh

# Init and import data
chmod +x init-data.sh
./init-data.sh
