#!/bin/bash
set -e

mongod --port 27017 --shardsvr --replSet "$REPLICA_SERVER_SHARD_01_NAME" --bind_ip_all --keyFile /etc/mongo-keyfile/keyfile &

wait
