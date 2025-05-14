#!/bin/bash
set -e

# Start MongoDB in the background
mongod --configsvr --replSet "$REPLICA_SERVER_CONFIG_NAME" --port 27017 --bind_ip_all --keyFile /etc/mongo-keyfile/keyfile &

# Store the PID of MongoDB
MONGO_PID=$!

# Give MongoDB some time to start initially
sleep 5

# Function to check if MongoDB is ready locally
check_mongo_ready() {
  host=$1
  mongosh --host "$host" --eval "db.adminCommand('ping')" --quiet
  return $?
}

# Wait for all shard servers to be ready
wait_for_mongo() {
  echo "Waiting for MongoDB instances to start..."

  # First wait for local instance
  until check_mongo_ready 127.0.0.1; do
    echo "Waiting for local MongoDB to start..."
    # Check if MongoDB process is still running
    if ! kill -0 $MONGO_PID 2>/dev/null; then
      echo "MongoDB process died unexpectedly. Check logs for errors."
      exit 1
    fi
    sleep 2
  done
  echo "Local MongoDB is ready!"

  IFS=',' read -ra CONFIG_SERVERS_ARRAY <<< "$CONFIG_SERVERS"

  for CONFIG_SERVER in "${CONFIG_SERVERS_ARRAY[@]}"; do
    attempt=0
    max_attempts=30
    until check_mongo_ready "$CONFIG_SERVER" || [ $attempt -ge $max_attempts ]; do
      echo "Waiting for $CONFIG_SERVER to be ready... (attempt $((attempt + 1))/$max_attempts)"
      attempt=$((attempt+1))
      sleep 2
    done

    if [ $attempt -ge $max_attempts ]; then
      echo "Timed out waiting for $CONFIG_SERVER. Continuing anyway..."
    else
      echo "$CONFIG_SERVER is ready!"
    fi
  done

  echo "All MongoDB instances are ready or timed out!"
}

# Initialize replica set
init_shard() {
  echo "Initializing config server replica set..."

  # Adding more diagnostic output
  echo "Current MongoDB status:"
  mongosh --eval "db.adminCommand('ping')" || echo "Failed to ping MongoDB"

  # Try to initialize replica set with retries
  local max_attempts=5
  local attempt=0
  local success=false

  while [ $attempt -lt $max_attempts ] && [ "$success" = "false" ]; do
    ((attempt++))
    echo "Attempt $attempt of $max_attempts to initialize config server replica set"

    if mongosh --eval "
      const hosts = '${CONFIG_SERVERS}'.split(',');
      const replica = '${REPLICA_SERVER_CONFIG_NAME}';
      const members = hosts.map((host, index) => ({
        _id: index,
        host: host + ':27017',
        priority: index === 0 ? 1 : 0.5
      }));
      disableTelemetry();
      rs.initiate({
        _id: replica,
        configsvr: true,
        version: 1,
        members
      }, {force: true});
    " 2>/dev/null; then
      echo "Successfully initialized config server replica set"
      success=true
    else
      echo "Failed to initialize config server replica set, retrying in 5 seconds..."
      sleep 5
    fi
  done

  if [ "$success" = "false" ]; then
    echo "Failed to initialize config server replica set after $max_attempts attempts"
    echo "Continuing anyway, as the replica set might have been initialized by another node"
  fi

  echo "Config server replica set initialization completed."
}

# Main execution
echo "Starting MongoDB Shard entrypoint script..."
wait_for_mongo
init_shard

# Keep the script running to maintain the container
echo "Initialization completed, keeping container running with MongoDB process..."
wait $MONGO_PID
