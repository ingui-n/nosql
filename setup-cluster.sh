#!/bin/bash

echo "Setup config servers..."
docker-compose exec nosql-config-01 bash -c 'mongosh /scripts/init-config-server.js'

echo "Setup shards..."
docker-compose exec nosql-shard-01-node-01 bash -c 'mongosh /scripts/init-shard-01.js'
docker-compose exec nosql-shard-02-node-01 bash -c 'mongosh /scripts/init-shard-02.js'
docker-compose exec nosql-shard-03-node-01 bash -c 'mongosh /scripts/init-shard-03.js'

echo "Setup router..."
docker-compose exec nosql-router-01 bash -c 'mongosh -u $ROOT_USERNAME -p $ROOT_PASSWORD --authenticationDatabase admin /scripts/init-router.js'
