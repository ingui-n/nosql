#!/bin/bash

mkdir -p keyfile

# Generates random base64 key to keyfile/keyfile
openssl rand -base64 756 > keyfile/keyfile
chmod 600 keyfile/keyfile
chown 999:999 keyfile/keyfile

chmod +x scripts/*.sh
