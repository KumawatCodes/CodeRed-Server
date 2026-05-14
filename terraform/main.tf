provider "aws" {
  region = var.region
}

resource "aws_security_group" "codered_sg" {
  name        = "codered-sg"
  description = "Allow HTTP and API traffic"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "codered_server" {
  ami                    = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2 us-east-1
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.codered_sg.id]

  tags = {
    Name    = "codered-server"
    Project = "CodeRed"
  }
}
