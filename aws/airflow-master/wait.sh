#!/usr/bin/env bash

until [ $(ssh -i "~/Documents/my-key.pem" ec2-user@$1 -o "StrictHostKeyChecking no" 'whoami') ]; do
    sleep 10
done