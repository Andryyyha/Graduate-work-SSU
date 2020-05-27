variable "instance_class" {
  type = string
  description = "Instance type for RDS"
  default = "db.t2.micro"
}

variable "allocated_storage" {
  type = string
  description = "Storage size in GiB"
  default = "10"
}

variable "availability_zone" {
  type = string
  description = "Availability zone for instance"
  default = "us-east-2c"
}

variable "db_name" {
  type = string
  description = "Name of Airflow metadata database"
  default = "airflow"
}

variable "db_username" {
  type = string
  description = "Name of root user"
  default = "airflow"
}

variable "db_password" {
  type = string
  description = "Root user password"
  default = "Airflow2020"
}