# Variables de configuración Terraform

# Configuración General

# Región AWS (us-east-1 tiene mayor disponibilidad Free Tier)
variable "region" {
  description = "Región de AWS para desplegar los recursos."
  type        = string
  default     = "us-east-1"
}

# Nombre base de recursos (usado como prefijo en tags)
variable "app_name" {
  description = "Nombre base para los recursos (VPC, SGs, etc.)"
  type        = string
  default     = "ing-soft-2"
}

# Nombre del repositorio ECR para imágenes Docker
variable "ecr_repo_name" {
  description = "Nombre del repositorio ECR para las imágenes Docker."
  type        = string
  default     = "mi-app-repo"
}

# Configuración de Red

# VPC CIDR (10.0.0.0/16 = 65,536 IPs)
variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block"
  default     = "10.0.0.0/16"
}

# Subnets Públicas (256 IPs cada una)
variable "subnet_public_cidr_1" {
  type        = string
  description = "CIDR for the public subnet"
  default     = "10.0.1.0/24"
}

variable "subnet_public_cidr_2" {
  type        = string
  description = "CIDR para la segunda subnet pública (necesaria para ALB en 2 AZs)."
  default     = "10.0.2.0/24"
}

variable "subnet_public_cidr_3" {
  type        = string
  description = "CIDR para la tercera subnet pública (necesaria para ALB en 2 AZs)."
  default     = "10.0.3.0/24"
}

# Subnets Privadas (256 IPs cada una, para RDS)
variable "subnet_private_cidr" {
  type        = string
  description = "CIDR for the first private subnet"
  default     = "10.0.6.0/24"
}

variable "subnet_private_cidr_2" {
  type        = string
  description = "CIDR for the second private subnet"
  default     = "10.0.7.0/24"
}

# Availability Zones (us-east-1 tiene a, b, c, d, e, f)
variable "public_subnet_az_1" {
  description = "Availability zone for the first public subnet (e.g. us-east-1a)"
  type        = string
  default     = "us-east-1a"
}

variable "public_subnet_az_2" {
  description = "Availability zone for the second public subnet (e.g. us-east-1b)"
  type        = string
  default     = "us-east-1b"
}

# AZ para subnet pública 3 (ALB)
variable "public_subnet_az_3" {
  description = "Availability zone for the second public subnet (e.g. us-east-1b)"
  type        = string
  default     = "us-east-1c"
}


variable "private_subnet_az_4" {
  type        = string
  description = "Availability Zone for the first private subnet (e.g. us-east-1a)"
  default     = "us-east-1d"
}

# AZ para subnet privada 2 (RDS Standby para failover)
variable "private_subnet_az_1" {
  type        = string
  description = "Availability Zone for the first private subnet (e.g. us-east-1a)"
  default     = "us-east-1a"
}

# Configuración de Instancias EC2

# Nombre del par de claves SSH (Terraform genera clave privada automáticamente)
variable "ec2_key_name" {
  description = "Nombre del Key Pair de EC2 para el acceso SSH."
  type        = string
  default     = "ssh-keys-mi-app"
}

# Tipo de instancia (t3.micro = Free Tier, 2 vCPUs, 1GB RAM)
variable "ec2_instance_type" {
  description = "Tipo de instancia para el servidor de la app (Capa Gratuita)."
  type        = string
  default     = "t3.micro"
}

# IP pública para SSH (CAMBIAR por tu IP: curl ifconfig.me)
variable "my_ip_cidr" {
  type        = string
  description = "Your public IP in CIDR format for SSH access, e.g. 1.2.3.4/32"
  default     = "0.0.0.0/0"
}

# Configuración de Base de Datos RDS

# Clase de instancia (db.t3.micro = Free Tier)
variable "db_instance_class" {
  description = "Tipo de instancia para RDS (Capa Gratuita)."
  type        = string
  default     = "db.t3.micro"
}

# Nombre de la base de datos inicial
variable "db_name" {
  description = "Nombre de la base de datos inicial."
  type        = string
  default     = "miappdb"
}

# Usuario administrador (no usar 'user' ni 'postgres')
variable "db_user" {
  description = "Usuario administrador de la base de datos."
  type        = string
  default     = "dbadmin"

  validation {
    condition     = lower(var.db_user) != "user" && lower(var.db_user) != "postgres"
    error_message = "db_user no puede ser 'user' ni 'postgres' (palabras reservadas). Elige otro usuario, p.ej. 'dbadmin'."
  }
}

# Contraseña DB (CAMBIAR antes de apply, mín 8 caracteres)
variable "db_password" {
  description = "Contraseña para el administrador de la base de datos."
  type        = string
  sensitive   = true
  default = "123456Absrc"
}

# ===================================
# PRÁCTICA 5: Variables para Route 53
# ===================================

# Nombre del dominio (comprado en Namecheap)
variable "domain_name" {
  description = "Nombre del dominio para Route 53"
  type        = string
  default     = "is2-ss.me"
}
