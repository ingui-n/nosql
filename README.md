# NOSQL

_More like no sequel_

## Overview

MongoDB cluster with key file authentification.

## Run

1. Clone this repository to download the full code

```shell
git clone https://github.com/ingui-n/nosql
```

2. Edit `.env` file if you want to change for example credentials or mongo version
3. Run the init file that will generate the keyfile, run docker-compose, init cluster and import data

```shell
chmod +x init.sh && sudo ./init.sh
```

## Simulace výpadku uzlu/nodu

Zastavení kontejneru např. `nosql-shard-01-node-01`

```shell
docker stop nosql-shard-01-node-01
```

Připojení se do jednoho z uzlů shardu

```shell
docker-compose exec nosql-shard-01-node-02 bash
```

Přihlášení do `mongosh`

```shell
mongosh -u root -p pass --authenticationDatabase admin
```

Zobrazení statusu replika setu

```javascript
rs.status()
```

Spuštění uzlu 

```shell
docker start nosql-shard-01-node-01
```

## Notes

Departures across all the regions are `185 452` and counting. (16-5-2025)
