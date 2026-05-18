provider "aws" {
  region = var.region
}

# Security group - allows API and SSH access
resource "aws_security_group" "codered_sg" {
  name        = "codered-sg"
  description = "Allow HTTP and API traffic for CodeRed"

  # FastAPI backend
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Prometheus
  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Grafana
  ingress {
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "codered-sg"
    Project = "CodeRed"
  }
}

# EC2 instance - t2.micro is free tier eligible
resource "aws_instance" "codered_server" {
  ami                    = "ami-0f58b397bc5c1f2e8"  # Amazon Linux 2 ap-south-1
  instance_type          = var.instance_type
  key_name               = "codered-key"
  vpc_security_group_ids = [aws_security_group.codered_sg.id]

  # User data - runs on first boot, installs Docker and starts CodeRed
  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io git curl
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu

    # Install docker-compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Clone and run CodeRed
    cd /home/ubuntu
    git clone https://github.com/KumawatCodes/CodeRed-Server.git
    cd CodeRed-Server
    docker-compose up -d
  EOF

  tags = {
    Name    = "codered-server"
    Project = "CodeRed"
    Free    = "tier"
  }
}

# Output the public IP after creation
output "ec2_public_ip" {
  value       = aws_instance.codered_server.public_ip
  description = "Public IP of CodeRed EC2 instance"
}

output "api_url" {
  value       = "http://${aws_instance.codered_server.public_ip}:8000/docs"
  description = "CodeRed API URL"
}
