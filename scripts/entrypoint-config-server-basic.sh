#!/bin/bash
set -e

mongod --port 27017 --configsvr --replSet "$REPLICA_SERVER_CONFIG_NAME" --keyFile /etc/mongo-keyfile/keyfile &

wait
