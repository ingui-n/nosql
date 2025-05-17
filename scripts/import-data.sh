#!/bin/bash

mongosh -u "$ROOT_USERNAME" -p "$ROOT_PASSWORD" --authenticationDatabase --eval "
db = db.getSiblingDB(process.env.DATABASE_NAME);
console.log('Addresses collection size:', db.addresses.countDocuments());
console.log('Departures collection size:', db.departures.countDocuments());
console.log('Sent_units collection size:', db.sent_units.countDocuments());
"

read -n 1 -rp "Do you really want to import the data? (y/n): " answer
echo ""
if [[ "$answer" != [Yy] ]]; then
    exit 0
fi

echo "Importing addresses..."
mongoimport --uri "mongodb://$ROOT_USERNAME:$ROOT_PASSWORD@localhost:27017/$DATABASE_NAME?authSource=admin" \
--collection addresses --file /init-data/addresses.json --jsonArray

echo "Importing departures..."
mongoimport --uri "mongodb://$ROOT_USERNAME:$ROOT_PASSWORD@localhost:27017/$DATABASE_NAME?authSource=admin" \
--collection departures --file /init-data/departures.json --jsonArray

echo "Importing sent_units..."
mongoimport --uri "mongodb://$ROOT_USERNAME:$ROOT_PASSWORD@localhost:27017/$DATABASE_NAME?authSource=admin" \
--collection sent_units --file /init-data/units.json --jsonArray
