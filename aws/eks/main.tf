provider "aws" {
  region = "us-east-2"
}

data "aws_eks_cluster" "cluster" {
  name = module.airflow-cluster.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.airflow-cluster.cluster_id
}

resource "aws_security_group" "rds_nfs" {
  name_prefix = "rds_nfs"
  vpc_id = var.vpc
}

resource "aws_security_group_rule" "nfs" {
  from_port = 2049
  protocol = "tcp"
  security_group_id = aws_security_group.rds_nfs.id
  to_port = 2049
  type = "ingress"
  cidr_blocks = [
    "0.0.0.0/0"]
}

resource "aws_security_group_rule" "rds" {
  from_port = 5432
  protocol = "tcp"
  security_group_id = aws_security_group.rds_nfs.id
  to_port = 5432
  type = "ingress"
  cidr_blocks = ["0.0.0.0/0"]
}

module "airflow-cluster" {
  source = "terraform-aws-modules/eks/aws"
  cluster_name = "airflow-cluster"
  cluster_version = "1.16"
  subnets = var.subnets
  vpc_id = var.vpc

  worker_groups = [
    {
      name = "airflow-workers"
      instance_type = "t3.medium"
      asg_desired_capacity = 1
      autoscaling_enabled = true
      additional_security_group_ids = [aws_security_group.rds_nfs.id]
    }
  ]
}