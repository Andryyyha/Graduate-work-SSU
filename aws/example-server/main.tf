provider "aws" {
  region = "us-east-2"
}

resource "aws_instance" "example_server" {
  ami = var.ami_id
  instance_type = var.instance_type
  availability_zone = var.availability_zone
  vpc_security_group_ids = var.security_groups
  key_name = "my-key.pem"
  root_block_device {
    volume_type = "gp2"
    volume_size = 20
  }
  tags = {
    Name = var.server_name
  }
}