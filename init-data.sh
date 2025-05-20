#!/bin/bash

# Create virtual environment if missing
#if [ ! -d "venv" ]; then
#    echo "Creating virtual environment..."
#    python3 -m venv venv
#fi

# Activate and install requirements
#source venv/bin/activate
#pip install -r init-data/requirements.txt

# Init data
#python3 init-data/init-data.py

echo "Importing data to mongo..."
docker-compose exec nosql-router-01 bash -c '/scripts/import-data.sh'
