#!/bin/bash
#set -e

set -a
source .env
set +a

envsubst < scripts/config-server-01.js | node