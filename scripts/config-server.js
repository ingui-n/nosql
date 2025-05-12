const hosts = "${CONFIG_SERVERS}".split(",");
const replica = "${REPLICA_SERVER_CONFIG_NAME}";

const members = hosts.map((host, index) => ({
  _id: index,
  host: `${host}:27017`,
  priority: index === 0 ? 1 : 0.5
}));

rs.initiate({
  _id: replica,
  configsvr: true,
  version: 1,
  members
}, {force: true});
