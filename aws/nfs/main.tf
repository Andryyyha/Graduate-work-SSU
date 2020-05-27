provider "aws" {
  region = "us-east-2"
}

resource "aws_efs_file_system" "shared_logs" {
  creation_token = "airflow-shared-logs"
  tags = {
    Name = "airflow-shared-logs"
  }
}

resource "aws_efs_file_system" "shared-dags" {
  creation_token = "airflow-sahred-dags"
  tags = {
    Name = "airflow-sahred-dags"
  }
}