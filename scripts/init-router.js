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


console.log('init-router:', `Adding data structure...`);
db = db.getSiblingDB(process.env.DATABASE_NAME);

console.log('init-router:', `Enable sharding for database ${process.env.DATABASE_NAME}...`);
sh.enableSharding(process.env.DATABASE_NAME);

db.createCollection("departures", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["departure_id", "reportedDateTime", "stateId", "typeId", "subTypeId"],
      properties: {
        departure_id: {bsonType: "int"},
        reportedDateTime: {bsonType: "date"},
        startDateTime: {bsonType: ["date", "null"]},
        stateId: {bsonType: "int"},
        typeId: {bsonType: "int"},
        subTypeId: {bsonType: "int"},
        description: {bsonType: ["string", "null"]},
        region_url: {bsonType: ["string", "null"]}
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

db.createCollection("addresses", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["departure_id"],
      properties: {
        departure_id: {bsonType: "int"},
        region: {
          bsonType: "object",
          properties: {
            id: {bsonType: ["int", "null"]},
            name: {bsonType: ["string", "null"]}
          }
        },
        district: {
          bsonType: "object",
          properties: {
            id: {bsonType: ["int", "null"]},
            name: {bsonType: ["string", "null"]}
          }
        },
        municipality: {bsonType: ["string", "null"]},
        municipalityPart: {bsonType: ["string", "null"]},
        municipalityWithExtendedCompetence: {bsonType: ["string", "null"]},
        street: {bsonType: ["string", "null"]},
        gis1: {bsonType: "string"},
        gis2: {bsonType: "string"},
        zoc: {bsonType: "bool"},
        road: {bsonType: ["string", "null"]}
      }
    }
  }
});

db.createCollection("sent_units", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["departure_id"],
      properties: {
        departure_id: {bsonType: "int"},
        type: {bsonType: ["string", "null"]},
        unit: {bsonType: ["string", "null"]},
        count: {bsonType: ["int", "null"]},
        currentCount: {bsonType: ["int", "null"]},
        callDateTime: {bsonType: ["date", "null"]}
      }
    }
  }
});

console.log('init-router:', `Creating indexes...`);
db.departures.createIndex({"departure_id": 1}, {unique: true});
db.addresses.createIndex({"departure_id": 1});
db.sent_units.createIndex({"departure_id": 1});

console.log('init-router:', `Creating indexes...`);
sh.shardCollection(process.env.DATABASE_NAME + ".departures", {"departure_id": "hashed"});
sh.shardCollection(process.env.DATABASE_NAME + ".addresses", {"departure_id": "hashed"});
sh.shardCollection(process.env.DATABASE_NAME + ".sent_units", {"departure_id": "hashed"});

console.log('init-router:', `Shard status:`);
console.log(sh.status());
