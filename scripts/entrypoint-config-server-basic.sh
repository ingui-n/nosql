#!/bin/bash
set -e

mongod --port 27017 --shardsvr --replSet "$SHARD_01_NAME" --keyFile /etc/mongo-keyfile/keyfile &

wait
