# Configuración de proveedores Terraform

terraform {
  required_providers {
    # Provider de AWS para gestionar infraestructura en Amazon Web Services
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    # Provider TLS para generación de claves SSH RSA
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

# Provider AWS - Región desde var.region
provider "aws" {
  region = var.region
}