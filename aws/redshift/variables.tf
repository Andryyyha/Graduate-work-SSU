variable "region" {
  type        = string
  description = "Default AWS region"
  default     = "us-east-2"
}

variable "cluster_name" {
  type        = string
  description = "Redshift cluster name"
  default     = "metrics"
}

variable "db_name" {
  type        = string
  description = "Name of database for metrics"
  default     = "metrics"
}

variable "db_master_username" {
  type        = string
  description = "Master username"
  default     = "metrics"
}

variable "db_master_password" {
  type        = string
  description = "Master password"
  default     = "Airflow2020"
}

variable "node_type" {
  type        = string
  description = "Node type for cluster"
  default     = "dc2.large"
}

variable "cluster_mode" {
  type        = string
  description = "Cluster deployment type"
  default     = "single-node"
}