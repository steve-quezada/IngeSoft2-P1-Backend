# Infraestructura AWS
# Aplicación web de 3 capas: Frontend React + Backend Flask + PostgreSQL RDS

# VPC - Red virtual principal (10.0.0.0/16)
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "${var.app_name}-vpc"
  }
}

# Subnets - 3 públicas y 2 privadas en múltiples AZs

# Subnet Pública 1 - Frontend (us-east-1a)
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_public_cidr_1
  map_public_ip_on_launch = true
  availability_zone       = var.public_subnet_az_1

  tags = {
    Name = "${var.app_name}-subnet-front"
  }
}

# Subnet Pública 2 - Backend (us-east-1b)
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_public_cidr_2
  map_public_ip_on_launch = true
  availability_zone       = var.public_subnet_az_2

  tags = {
    Name = "${var.app_name}-subnet-back"
  }
}

# Subnet Pública 3 - ALB (us-east-1c, requerida para alta disponibilidad)
resource "aws_subnet" "public_3" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_public_cidr_3
  map_public_ip_on_launch = true
  availability_zone       = var.public_subnet_az_3

  tags = {
    Name = "${var.app_name}-subnet-alb"
  }
}

# Subnet Privada 1 - RDS principal (us-east-1d)
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.subnet_private_cidr
  availability_zone = var.private_subnet_az_4

  tags = {
    Name = "${var.app_name}-subnet-db"
  }
}

# Subnet Privada 2 - RDS standby (us-east-1a, multi-AZ failover)
resource "aws_subnet" "private_db" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.subnet_private_cidr_2
  availability_zone = var.private_subnet_az_1

  tags = {
    Name = "${var.app_name}-subnet-db-2"
  }
}

# Internet Gateway - Conecta VPC con internet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.app_name}-igw"
  }
}

# Route Table - Enruta tráfico público hacia Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.app_name}-public-rt"
  }
}

# Asociar subnets públicas con route table
resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_3" {
  subnet_id      = aws_subnet.public_3.id
  route_table_id = aws_route_table.public.id
}

# Security Groups - Firewalls para ALB, EC2 y RDS

# SG para ALB - Permite HTTP/HTTPS desde internet
resource "aws_security_group" "alb" {
  name        = "${var.app_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-alb-sg"
  }
}

# SG para EC2 - HTTP/HTTPS público, SSH desde IP específica
resource "aws_security_group" "ec2" {
  name        = "${var.app_name}-ec2-sg"
  description = "Security group for EC2 instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-ec2-sg"
  }
}

# SG para RDS - Solo PostgreSQL (5432) desde EC2
resource "aws_security_group" "rds" {
  name        = "${var.app_name}-rds-sg"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-rds-sg"
  }
}

# ECR - Repositorio para imágenes Docker
resource "aws_ecr_repository" "main" {
  name = var.ecr_repo_name
  image_scanning_configuration {
    scan_on_push = true
  }
}

# SSH Key Pair - Generado automáticamente (RSA 4096-bit)
resource "tls_private_key" "generated" {
  count     = var.ec2_key_name != "" ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "main" {
  key_name   = var.ec2_key_name
  public_key = length(tls_private_key.generated) > 0 ? tls_private_key.generated[0].public_key_openssh : ""

  tags = {
    Name = "${var.app_name}-key-pair"
  }
}

# DB Subnet Group - Agrupa subnets privadas para RDS multi-AZ
resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private.id, aws_subnet.private_db.id]

  tags = {
    Name = "${var.app_name}-db-subnet-group"
  }
}

# AMI más reciente de Amazon Linux 2 (desde SSM Parameter Store)
data "aws_ssm_parameter" "amazon_linux_2_ami" {
  name = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
}

# RDS PostgreSQL - db.t3.micro, 20GB, multi-AZ, solo accesible desde EC2
resource "aws_db_instance" "main" {
  identifier             = "${var.app_name}-db"
  db_name                = var.db_name
  engine                 = "postgres"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  storage_type           = "gp2"
  username               = var.db_user
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  skip_final_snapshot    = true
}

# EC2 Instances - t3.micro con Amazon Linux 2 y Docker preinstalado

# Instancia Frontend - React en subnet pública (us-east-1a)
resource "aws_instance" "front" {
  ami                    = data.aws_ssm_parameter.amazon_linux_2_ami.value
  instance_type          = var.ec2_instance_type
  key_name               = aws_key_pair.main.key_name
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              usermod -a -G docker ec2-user
              EOF

  tags = {
    Name = "${var.app_name}-front-instance"
  }
}

# Instancia Backend - Flask API en subnet pública (us-east-1b)
resource "aws_instance" "back" {
  ami                    = data.aws_ssm_parameter.amazon_linux_2_ami.value
  instance_type          = var.ec2_instance_type
  key_name               = aws_key_pair.main.key_name
  subnet_id              = aws_subnet.public_2.id
  vpc_security_group_ids = [aws_security_group.ec2.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              usermod -a -G docker ec2-user
              EOF

  tags = {
    Name = "${var.app_name}-back-instance"
  }
}

# Application Load Balancer - Distribuye tráfico HTTP entre EC2 (multi-AZ)
resource "aws_lb" "main" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public.id, aws_subnet.public_2.id, aws_subnet.public_3.id]

  tags = {
    Name = "${var.app_name}-alb"
  }
}

# Target Group Frontend - Health check en "/" para React
resource "aws_lb_target_group" "frontend" {
  name        = "${var.app_name}-frontend-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.app_name}-frontend-tg"
  }
}

# Target Group Backend - Health check en "/health" para Flask
resource "aws_lb_target_group" "backend" {
  name        = "${var.app_name}-backend-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.app_name}-backend-tg"
  }
}

# Listener HTTP - Puerto 80, redirige al frontend por defecto
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Listener Rule - Enruta /questions, /health, /api/* al backend
resource "aws_lb_listener_rule" "backend_api" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/questions*", "/health", "/api/*"]
    }
  }

  tags = {
    Name = "${var.app_name}-backend-rule"
  }
}

# Attachments - Registra instancias en sus respectivos target groups
resource "aws_lb_target_group_attachment" "frontend" {
  target_group_arn = aws_lb_target_group.frontend.arn
  target_id        = aws_instance.front.id
  port             = 80
}

resource "aws_lb_target_group_attachment" "backend" {
  target_group_arn = aws_lb_target_group.backend.arn
  target_id        = aws_instance.back.id
  port             = 80
}