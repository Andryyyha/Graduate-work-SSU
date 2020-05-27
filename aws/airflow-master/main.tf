provider "aws" {
  region = "us-east-2"
}

resource "aws_security_group_rule" "db" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 5432
  protocol          = "tcp"
  security_group_id = var.security_groups[2]
  to_port           = 5432
  type              = "ingress"
}

resource "aws_security_group_rule" "webserver" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 8080
  protocol          = "tcp"
  security_group_id = var.security_groups[2]
  to_port           = 8080
  type              = "ingress"
}

resource "aws_security_group_rule" "nfs" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 2049
  protocol          = "tcp"
  security_group_id = var.security_groups[2]
  to_port           = 2049
  type              = "ingress"
}

resource "aws_instance" "airflow_master" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  availability_zone           = var.availability_zone
  key_name                    = "my-key.pem"
  vpc_security_group_ids      = var.security_groups
  associate_public_ip_address = true
  root_block_device {
    volume_type = "gp2"
    volume_size = 30
  }
  timeouts {
    create = "5m"
  }

  provisioner "local-exec" {
    command = <<EOT
    bash wait.sh ${aws_instance.airflow_master.public_ip}
    EOT
  }

  provisioner "local-exec" {
    command = <<EOT
    ansible-playbook \
    -i ${aws_instance.airflow_master.public_ip}, \
    install_packages.yaml \
    --key-file ~/Documents/my-key.pem
    EOT
  }
}
