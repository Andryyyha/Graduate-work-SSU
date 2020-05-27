variable "region" {
  type        = string
  description = "Default AWS region to run cluster"
  default     = "us-east-2"
}

variable "vpc_id" {
  type        = string
  description = "VPC id for security group"
  default     = "vpc-a71a06cf"
}

variable "subnet_id" {
  type        = string
  description = "Subnet id where to run cluster"
  default     = "subnet-08363260"
}

variable "core_instance_type" {
  type        = string
  description = "Instance type for Core instance group"
  default     = "m4.large"
}

variable "core_instance_count" {
  type        = number
  description = "Number of Core instances launched in cluster"
  default     = 1
}

variable "core_instance_ebs_size" {
  type        = number
  description = "Size of Elastic Block Storage for each core instance"
  default     = 32
}

variable "core_instance_ebs_type" {
  type        = string
  description = "EBS volume type for core instances"
  default     = "gp2"
}

variable "master_instance_type" {
  type        = string
  description = "Instance type for Master instance group"
  default     = "m4.large"
}

variable "master_instance_count" {
  type        = number
  description = "Number of Master instances launched in cluster"
  default     = 1
}

variable "master_instance_ebs_size" {
  type        = number
  description = "Size of Elastic Block Storage for each master instance"
  default     = 32
}

variable "master_instance_ebs_type" {
  type        = string
  description = "EBS volume type for master instance"
  default     = "gp2"
}

variable "key_name" {
  type        = string
  description = "Name of registered SSH key"
  default     = "my-key.pem"
}