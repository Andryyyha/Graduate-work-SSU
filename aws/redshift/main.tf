provider "aws" {
  region = var.region
}

resource "aws_redshift_cluster" "metrics" {
  cluster_identifier = var.cluster_name
  node_type          = var.node_type
  database_name      = var.db_name
  master_username    = var.db_master_username
  master_password    = var.db_master_password
  cluster_type       = var.cluster_mode
}