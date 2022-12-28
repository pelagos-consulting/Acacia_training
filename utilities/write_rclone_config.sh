#!/bin/bash

source ${HOME}/acacia_credentials.txt

mkdir -p ${HOME}/.config/rclone

tee rclone.conf << EOF
[acacia-mine]
type = s3
provider = Ceph
endpoint = https://projects.pawsey.org.au
access_key_id = $AccessID
secret_access_key = $SecretKey
chunk_size = 1G
EOF

echo "Rclone config file written to ./rclone.conf."
echo "Move ./rclone.conf to ${HOME}/.config/rclone/rclone.conf to complete the configuration."
