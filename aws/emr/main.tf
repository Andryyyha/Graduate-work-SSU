provider "aws" {
  region = var.region
}

module "data_and_other" {
  source  = "cloudposse/s3-log-storage/aws"
  version = "0.9.0"
  name    = "data-and-other"
  stage   = "prod"
}

data "local_file"  "configuration_json" {
  filename = file("./emr_bootstrap.json")
}

module "prod_etl_cluster" {
  source                               = "cloudposse/emr-cluster/aws"
  version                              = "0.5.0"
  name                                 = "ETL prod"
  region                               = var.region
  vpc_id                               = var.vpc_id
  subnet_id                            = var.subnet_id
  subnet_type                          = "private"
  applications                         = ["Spark"]
  configurations_json                  = data.local_file.configuration_json.content
  core_instance_group_instance_type    = var.core_instance_type
  core_instance_group_ebs_size         = var.core_instance_ebs_size
  core_instance_group_ebs_type         = var.core_instance_ebs_type
  core_instance_group_instance_count   = var.core_instance_count
  master_instance_group_instance_type  = var.master_instance_type
  master_instance_group_ebs_size       = var.master_instance_ebs_size
  master_instance_group_ebs_type       = var.master_instance_ebs_type
  master_instance_group_instance_count = var.master_instance_count
  log_uri                              = format("s3n://%s", module.data_and_other.bucket_id)
  key_name                             = var.key_name
}