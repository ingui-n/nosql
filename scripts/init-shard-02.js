const config = {
  "_id": "rs-shard-02",
  "version": 1,
  "members": [
    {
      "_id": 0,
      "host": "nosql-shard-02-node-01:27017",
      "priority": 1
    },
    {
      "_id": 1,
      "host": "nosql-shard-02-node-02:27017",
      "priority": 0.5
    },
    {
      "_id": 2,
      "host": "nosql-shard-02-node-03:27017",
      "priority": 0.5
    }
  ]
};

disableTelemetry();

try {
  rs.status().ok;
} catch (e) {
  try {
    console.log('init-shard-02:', 'Initializing replica set');
    rs.initiate(config, {force: true});
    console.log('init-shard-02:', 'Successfully initialized replica set');
  } catch (e) {
    console.log('init-shard-02:', 'Replica was already initialized.', e.message);
  }
}

try {
  const user = process.env.ROOT_USERNAME;
  const pwd = process.env.ROOT_PASSWORD;

  if (!user || !pwd) {
    throw new Error('Missing credentials');
  }

  console.log('init-shard-02:', 'Creating admin user...');

  new Promise((resolve, reject) => {
    const attempt = () => {
      if (db.isMaster().ismaster) {
        try {
          db.getSiblingDB('admin').createUser({user, pwd, roles: [{role: 'root', db: 'admin'}]});
          console.log('init-shard-02:', 'Successfully created admin user');
          resolve('Admin user created successfully');
        } catch (e) {
          console.error('init-shard-02:', 'Error creating admin user:', e.message);
          reject(e);
        }
      } else {
        console.log('init-shard-02:', 'Waiting for config server to be ready (3s)...');
        setTimeout(attempt, 3000);
      }
    };

    attempt();
  }).catch();
} catch (e) {
  console.error('init-shard-02:', 'Error when creating admin credentials:', e.message);
}
