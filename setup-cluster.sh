#!/bin/bash

read -n 1 -rp "Do you want to wait 10 seconds for primary elections? (y/n): " answer
echo ""
if [[ "$answer" == [Yy] ]]; then
    echo "Waiting for electing primaries (10s)..."
    sleep 10
fi

echo "Setup config servers..."
docker-compose exec nosql-config-01 bash -c "mongosh /scripts/init-config-server.js"

echo "Setup shards..."
docker-compose exec nosql-shard-01-node-01 bash -c "mongosh /scripts/init-shard-01.js"
docker-compose exec nosql-shard-02-node-01 bash -c "mongosh /scripts/init-shard-02.js"
docker-compose exec nosql-shard-03-node-01 bash -c "mongosh /scripts/init-shard-03.js"

echo "Setup router..."
docker-compose exec nosql-router-01 bash -c "mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin /scripts/init-router.js"
