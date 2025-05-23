const config = {
  "_id": "rs-config-server",
  "configsvr": true,
  "version": 1,
  "members": [
    {
      "_id": 0,
      "host": "nosql-config-01:27017",
      "priority": 1
    },
    {
      "_id": 1,
      "host": "nosql-config-02:27017",
      "priority": 0.5
    },
    {
      "_id": 2,
      "host": "nosql-config-03:27017",
      "priority": 0.5
    }
  ]
};

disableTelemetry();

try {
  rs.status().ok;
} catch (e) {
  try {
    console.log('init-config-server:', 'Initializing replica set');
    rs.initiate(config, {force: true});
    console.log('init-config-server:', 'Successfully initialized replica set');
  } catch (e) {
    console.log('init-config-server:', 'Replica was already initialized.', e.message);
  }
}

try {
  const user = process.env.ROOT_USERNAME;
  const pwd = process.env.ROOT_PASSWORD;

  if (!user || !pwd) {
    throw new Error('Missing credentials');
  }

  console.log('init-config-server:', 'Creating admin user...');

  new Promise((resolve, reject) => {
    const attempt = () => {
      if (db.isMaster().ismaster) {
        try {
          db.getSiblingDB('admin').createUser({user, pwd, roles: [{role: 'root', db: 'admin'}]});
          console.log('init-config-server:', 'Successfully created admin user');
          resolve('Admin user created successfully');
        } catch (e) {
          console.error('init-config-server:', 'Error creating admin user:', e.message);
          reject(e);
        }
      } else {
        console.log('init-config-server:', 'Waiting for config server to be ready (3s)...');
        setTimeout(attempt, 3000);
      }
    };

    attempt();
  }).catch();
} catch (e) {
  console.error('init-config-server:', 'Error when creating admin credentials:', e.message);
}
