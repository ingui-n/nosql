#!/bin/bash
set -e

mongod --shardsvr --replSet shard1 --port 27018 --bind_ip_all --keyFile /etc/mongo-keyfile/keyfile
