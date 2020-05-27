variable "ami_id" {
  type        = string
  description = "ID of Amazon Machine Image"
  default     = "ami-0f7919c33c90f5b58"
}

variable "instance_type" {
  type        = string
  description = "Instance type"
  default     = "t3.medium"
}

variable "availability_zone" {
  type        = string
  description = "Availability zone for instance"
  default     = "us-east-2c"
}

variable "security_groups" {
  type        = list(string)
  description = "List of security groups for instance"
  default = [
    "sg-06ddfa8684cb6197b",
    "sg-0db432ff9749de98b",
    "sg-5d707a33",
    "sg-0db432ff9749de98b"]
}
