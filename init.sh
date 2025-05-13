#!/bin/bash

mkdir -p keyfile

# Generates random base64 key to keyfile/keyfile
openssl rand -base64 756 > keyfile/keyfile
chmod 600 keyfile/keyfile

# Add permissions to execute scripts
chmod +x scripts/*.sh
