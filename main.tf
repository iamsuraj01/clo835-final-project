terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# VPC Resources
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name      = "clo835-final-project-vpc"
    Terraform = "true"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "clo835-main-igw"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name      = "Public Subnet 1"
    Terraform = "true"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name      = "Public Subnet 2"
    Terraform = "true"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "clo835-public-rt"
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "allow_web" {
  name        = "allow_web_traffic"
  description = "Allow inbound web traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Custom TCP"
    from_port   = 8081
    to_port     = 8083
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_web_traffic"
  }
}

# Key Pair
resource "aws_key_pair" "clo835_key_pair" {
  key_name   = "clo835_key_pair"
  public_key = file("~/.ssh/clo835_key.pub")
}

# Optional EC2 Instance (if needed)
resource "aws_instance" "app_server" {
  ami                    = "ami-0cff7528ff583bf9a"
  instance_type          = "t2.medium"
  key_name               = aws_key_pair.clo835_key_pair.key_name
  vpc_security_group_ids = [aws_security_group.allow_web.id]
  subnet_id              = aws_subnet.public_1.id

  tags = {
    Name = "CLO835-Final-Project-EC2"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo amazon-linux-extras install docker -y
              sudo service docker start
              sudo usermod -a -G docker ec2-user
              sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              sudo chmod +x /usr/local/bin/docker-compose
              EOF
}

# ECR Repositories
resource "aws_ecr_repository" "webapp" {
  name                 = "clo835-final-project-webapp"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "Webapp Repository"
  }
}

resource "aws_ecr_repository" "mysql" {
  name                 = "clo835-final-project-mysql"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "MySQL Repository"
  }
}

# S3 Bucket for Background Images
resource "aws_s3_bucket" "background_images" {
  bucket = "clo835-final-project-background-images-${random_string.bucket_suffix.result}"

  lifecycle {
    prevent_destroy = false
  }

  tags = {
    Name = "Background Images Bucket"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}


# Outputs
output "instance_public_ip" {
  value = aws_instance.app_server.public_ip
}

output "webapp_ecr_repository_url" {
  value = aws_ecr_repository.webapp.repository_url
}

output "mysql_ecr_repository_url" {
  value = aws_ecr_repository.mysql.repository_url
}

output "s3_bucket_name" {
  value = aws_s3_bucket.background_images.id
}