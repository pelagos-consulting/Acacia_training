#!/bin/bash

source ${HOME}/acacia_credentials.txt

mkdir -p ${HOME}/.mc

tee config.json << EOF
{
	"version": "10",
	"aliases": {
		"acacia-mine": {
			"url": "https://projects.pawsey.org.au",
			"accessKey": "$AccessID",
			"secretKey": "$SecretKey",
			"api": "s3v4",
			"path": "auto"
		},
		"local": {
			"url": "http://localhost:9000",
			"accessKey": "",
			"secretKey": "",
			"api": "S3v4",
			"path": "auto"
		}
	}
}
EOF

echo "MC config file written to ./config.json"
echo "Move ./config.json to ~/.mc/config.json to complete the configuration."
