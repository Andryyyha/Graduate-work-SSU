#!/usr/bin/env bash
terraform plan
if [[ $? -ne 0 ]]; then
    terraform init
    terraform plan
    terraform apply -auto-approve
    cp ./kueconfig* ~/.kube/config
    kubectl create namespace -n airflow
    bash ./volumes/create_all.sh
fi