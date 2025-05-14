#!/bin/bash
set -e

# Wait for the config server replica set to elect a primary
echo "Waiting for config server replica set to elect a primary..."
until mongosh --host "${REPLICA_SERVER_CONFIG_NAME}"/"${CONFIG_SERVERS//,/:27017,}:27017" --eval 'rs.status().members.some(m => m.stateStr === "PRIMARY")' | grep -q 'true'; do
  sleep 5
done

# Wait for each shard's replica set to elect a primary
IFS=',' read -ra SHARD_ARRAY <<< "$REPLICA_SERVER_NAMES"
shard_iteration=0

# Loop through each shard
for SHARD_NAME in "${SHARD_ARRAY[@]}"; do
  # Extract the shard number from the replica set name (e.g., "rs-shard-01" -> "01")
  SHARD_NUM=${SHARD_NAME##*-}

  # Construct the variable name for the shard nodes
  SHARD_VAR="CONFIG_SVR_${SHARD_NUM}_NODES"
  NODES=${!SHARD_VAR}

  rs_index=$(printf "%02d" "$shard_iteration")
  replica_var="REPLICA_SERVER_SHARD_${rs_index}_NAME"
  replica_name=${!replica_var}

  echo "Waiting for $SHARD_NAME to elect a PRIMARY..."
  until mongosh --host "$replica_name/${NODES//,/:27017,}:27017" --eval 'rs.status().members.some(m => m.stateStr === "PRIMARY")' | grep -q 'true'; do
    sleep 5
  done
  ((shard_iteration++))
done

# Start mongos in the background
echo "Starting mongos..."
mongos --port 27017 --configdb "${REPLICA_SERVER_CONFIG_NAME}"/"${CONFIG_SERVERS//,/:27017,}:27017" --bind_ip_all --keyFile /etc/mongo-keyfile/keyfile &

# Wait for mongos to become available
echo "Waiting for mongos to start..."
until mongosh --port 27017 --eval 'db.adminCommand({ping: 1})' &> /dev/null; do
  sleep 5
done

# Add the shards using the provided commands
echo "Adding shards..."
shard_iteration=0

for SHARD_NAME in "${SHARD_ARRAY[@]}"; do
  # Extract the shard number from the replica set name (e.g., "rs-shard-01" -> "01")
  SHARD_NUM=${SHARD_NAME##*-}

  # Construct the variable name for the shard nodes
  SHARD_VAR="CONFIG_SVR_${SHARD_NUM}_NODES"
  NODES=${!SHARD_VAR}

  rs_index=$(printf "%02d" "$shard_iteration")
  replica_var="REPLICA_SERVER_SHARD_${rs_index}_NAME"
  replica_name=${!replica_var}

  IFS=',' read -ra NODES_ARRAY <<< "$NODES"

  for NODE in "${NODES_ARRAY[@]}"; do
    mongosh --port 27017 --eval "sh.addShard('$replica_name/$NODE:27017')"
  done
  ((shard_iteration++))
done

# Keep the mongos process running in the foreground
wait
