variable "vpc" {
  type = string
  description = "VPC ID for cluster"
  default = "vpc-a71a06cf"
}

variable "subnets" {
  type = list(string)
  description = "List of subnets attached to VPC"
  default = [
    "subnet-08363260",
    "subnet-3582f04f",
    "subnet-f2cd68be"]
}