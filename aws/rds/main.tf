provider "aws" {
  region = "us-east-2"
}

resource "aws_db_instance" "airflow-metadata" {
  identifier          = "airflow-metadata"
  instance_class      = var.instance_class
  allocated_storage   = var.allocated_storage
  availability_zone   = var.availability_zone
  publicly_accessible = true
  storage_type        = "gp2"
  engine              = "postgres"
  engine_version      = "11"
  name                = var.db_name
  username            = var.db_username
  password            = var.db_password
}
