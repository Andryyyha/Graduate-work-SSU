#!/usr/bin/env bash
kubectl apply -f dags/ -n airflow
kubectl applt -f logs/ -n airflow

echo CREATED VOLUMES
kubectl get pv -n airflow

echo CREATED CLAIMS
kubectl get pvc -n airflow