disableTelemetry();

console.log('init-router:', 'Adding shards to router...');

sh.addShard("rs-shard-01/nosql-shard-01-node-01:27017");
sh.addShard("rs-shard-01/nosql-shard-01-node-02:27017");
sh.addShard("rs-shard-01/nosql-shard-01-node-03:27017");

sh.addShard("rs-shard-02/nosql-shard-02-node-01:27017");
sh.addShard("rs-shard-02/nosql-shard-02-node-02:27017");
sh.addShard("rs-shard-02/nosql-shard-02-node-03:27017");

sh.addShard("rs-shard-03/nosql-shard-03-node-01:27017");
sh.addShard("rs-shard-03/nosql-shard-03-node-02:27017");
sh.addShard("rs-shard-03/nosql-shard-03-node-03:27017");

console.log('init-router:', `Enable sharding for database ${process.env.DATABASE_NAME}...`);
sh.enableSharding(process.env.DATABASE_NAME);

console.log('init-router:', `Adding data structure...`);
// todo
// Setup shardingKey for collection `MyCollection`**
// db.adminCommand({shardCollection: "MyDatabase.MyCollection", key: {oemNumber: "hashed", zipCode: 1, supplierId: 1}})
