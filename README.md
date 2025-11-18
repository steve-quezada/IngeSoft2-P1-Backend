# Práctica 4 - Despliegue en AWS con Terraform [Nube + Servicios (Cuenta AWS + Terraform)]

### Integrantes
- **Steve Quezada** (@steve-quezada)
- **Etnicst** (@etnicst)

### Repositorios
- Backend: [github.com/steve-quezada/IngeSoft2-P1-Backend](https://github.com/steve-quezada/IngeSoft2-P1-Backend)
- Frontend: [github.com/steve-quezada/IngeSoft2-P1-Frontend](https://github.com/steve-quezada/IngeSoft2-P1-Frontend)

### Prerequisitos AWS
- Cuenta AWS creada con Plan Gratuito
- Usuarios IAM creados: `steve-quezada`, `etnicst`, `mauricioriva`, `cofy43`
- Presupuesto Zero-Spend configurado
- AWS CLI instalado y configurado (región: `us-east-1`)
- Terraform instalado

### Infraestructura Desplegada (29 recursos)
- **VPC**: Red virtual 10.0.0.0/16 con Internet Gateway
- **Subnets**: 3 públicas + 2 privadas en 4 AZs
- **Security Groups**: ALB, EC2, RDS con reglas específicas
- **EC2 Instances**: 2 x t3.micro (Frontend + Backend) con Docker
- **RDS PostgreSQL**: db.t3.micro en subnet privada
- **Application Load Balancer**: Distribución de tráfico HTTP con 2 Target Groups
- **ECR**: Repositorio privado para imágenes Docker
- **SSH Keys**: Generadas automáticamente con TLS provider

## Arquitectura AWS

<div align="center">

```
         Internet
         │
         ▼
        ┌────────────────────────────────────────┐
        │            Internet Gateway            │
        └────────────────────────────────────────┘
          │
          ▼
        ┌───────────────────────────────────────────────────┐
        │          Application Load Balancer (ALB)          │
        │  ing-soft-2-alb-xxxxx.us-east-1.elb.amazonaws.com │
        └───────────────────────────────────────────────────┘
       │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
        ┌────────────┐       ┌────────────┐       ┌────────────┐
        │   Subnet   │       │   Subnet   │       │   Subnet   │
        │  Public 1  │       │  Public 2  │       │  Public 3  │
        │ us-east-1a │       │ us-east-1b │       │ us-east-1c │
        │            │       │            │       │            │
        │     ECR    │       │  Frontend  │       │   Backend  │
        │ Repository │       │    EC2     │       │    EC2     │
        │            │       │  t3.micro  │       │  t3.micro  │
        │            │       │   Docker   │       │   Docker   │
        └────────────┘       └────────────┘       └────────────┘
                                                  │
                                                  ▼
                                                  ┌────────────┐
                                                  │   Subnet   │
                                                  │   Private  │
                                                  │ us-east-1a │
                                                  │            │
                                                  │    RDS     │
                                                  │ PostgreSQL │
                                                  │ db.t3.micro│
                                                  └────────────┘
```

</div>

## Estructura del Proyecto

```
Proyecto Completo/
├── IngeSoft2-P1-Backend/              ← Repositorio Backend
│   ├── .github/workflows/             ←  CI/CD Pipelines
│   │   └── backend-docker-build.yml   ← Pipeline Backend
   ├── terraform/                     ← Infraestructura como código
   │   ├── main.tf                    ← 29 recursos AWS (VPC, EC2, RDS, ALB, ECR)
   │   ├── variables.tf               ← Variables configurables (db_password, etc.)
│   │   ├── outputs.tf                 ← Outputs (IPs, DNS, endpoints)
│   │   ├── provider.tf                ← Providers (AWS, TLS)
│   │   ├── ssh-key.pem                ← Llave privada SSH (generada)
│   │   └── outputs.txt                ← Outputs guardados
│   ├── scripts/                       ← Scripts de base de datos
│   │   └── init.sql                   ← Schema PostgreSQL (3 tablas, índices)
│   ├── config/                        ← Configuración
│   │   ├── __init__.py
│   │   ├── config.py                  ← Config Flask + Database
│   │   └── database.py                ← Connection pool PostgreSQL
│   ├── src/                           ← Código fuente backend
│   │   ├── __init__.py
│   │   ├── models/                    ← Modelos de datos
│   │   │   ├── __init__.py
│   │   │   └── question.py
│   │   ├── routes/                    ← Endpoints API REST
│   │   │   ├── __init__.py
│   │   │   └── questions.py
│   │   ├── services/                  ← Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   └── question_service.py
│   │   └── utils/                     ← Utilidades y validadores
│   │       ├── __init__.py
│   │       └── validators.py
│   ├── tests/                         ← Testing (20 tests + PostgreSQL)
│   │   ├── test_all.py                ← Tests principales
│   │   ├── test_answers.py            ← Tests respuestas
│   │   ├── test_integration.py        ← Tests integración
│   │   ├── test_questions.py          ← Tests preguntas
│   │   └── test_refactored.py         ← Tests funcionales
│   ├── docker/                        ← Orquestación
│   │   ├── docker-compose.yml         ← Desarrollo
│   │   └── docker-compose.prod.yml    ← Producción
│   ├── Dockerfile                     ← Multi-stage build Python 3.11
│   ├── requirements.txt               ← Dependencias (Flask, PostgreSQL, etc.)
│   ├── supervisord.conf               ← Supervisor para procesos
│   └── app.py                         ← Aplicación Flask principal
│
└── IngeSoft2-P1-Frontend/             ← Repositorio Frontend
    ├── .github/workflows/             ←  CI/CD Pipelines
    │   └── frontend-docker-build.yml  ← Pipeline Frontend
    ├── Dockerfile                     ← Multi-stage build Node 20 (con VITE_API_URL)
    ├── supervisord.conf               ← Supervisor para procesos
    ├── proyecto-is2/                  ← Aplicación React/Vite
    │   ├── package.json               ← Dependencias + scripts test
    │   ├── package-lock.json          ← Lock para reproducibilidad
    │   ├── vite.config.js             ← Config Vitest
    │   ├── src/                       ← Código React
    │   │   ├── services/
    │   │   │   └── api.js             ← Configurado con import.meta.env
    │   │   ├── __tests__/             ←  Tests frontend (Vitest)
    │   │   │   ├── App.test.jsx       ← Test componente principal
    │   │   │   ├── InputPregunta.test.jsx  ← Test formulario
    │   │   │   └── frontend-integration.test.js  ← Test integración
    │   │   └── test/setup.js          ← Setup testing-library
    │   └── public/                    ← Assets estáticos
```

## URLs de Acceso (Producción AWS)

### Aplicación Desplegada
```bash
# Application Load Balancer (Principal)
http://ing-soft-2-alb-1167984181.us-east-1.elb.amazonaws.com

# Frontend directo (EC2)
http://98.92.205.135

# Backend API (EC2)
http://54.197.12.24/questions
http://54.197.12.24/health
```

### Recursos AWS
```bash
# RDS PostgreSQL Endpoint
ing-soft-2-db.c2zsu6mmqs1n.us-east-1.rds.amazonaws.com:5432

# ECR Repository
311136344575.dkr.ecr.us-east-1.amazonaws.com/mi-app-repo
```

## Configuración y Despliegue

### 1. Clonar Repositorio

### 2. Configurar AWS CLI

```bash
# Instalar AWS CLI v2

# Configurar credenciales
aws configure
# AWS Access Key ID
# AWS Secret Access Key
# Default region name: us-east-1
# Default output format: json

# Verificar configuración
aws sts get-caller-identity
```

### 3. Configurar Variables de Terraform

```bash
cd terraform

# Editar variables.tf
code variables.tf
```

**Variables críticas**:
- `db_password`: Contraseña de RDS PostgreSQL ("123456Absrc")
- `my_ip_cidr`: Tu IP para acceso SSH (por defecto 0.0.0.0/0)
- `app_name`: Nombre base de recursos (ing-soft-2)
- `region`: Región AWS (us-east-1)

### 4. Desplegar Infraestructura con Terraform

```bash
# Inicializar Terraform
terraform init

# Validar sintaxis
terraform validate

# Ver plan de ejecución (29 recursos)
terraform plan

# Aplicar cambios (crear infraestructura)
terraform apply
# Escribir: yes

# Guardar outputs importantes
terraform output -raw ec2_private_key_pem > ssh-key.pem
terraform output > outputs.txt

# Configurar permisos de SSH key (Windows)
icacls ssh-key.pem /inheritance:r /grant:r "$env:USERNAME:R"
```

### 5. Construir y Subir Imágenes Docker

```bash
# Obtener URL de ECR
$ECR_URL = terraform output -raw ecr_repository_url

# Autenticar Docker con ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL

# Backend
cd "../Proyecto Back"
docker build -t backend-flask .
docker tag backend-flask:latest ${ECR_URL}:backend-latest
docker push ${ECR_URL}:backend-latest

# Frontend (con variable de entorno - usar IP actual del backend)
cd "../Proyecto Front"
docker build --build-arg VITE_API_URL=http://54.197.12.24 -t frontend-react .
docker tag frontend-react:latest ${ECR_URL}:frontend-latest
docker push ${ECR_URL}:frontend-latest
```

### 6. Desplegar Backend en EC2

```bash
# Conectar a EC2 Backend
ssh -i terraform/ssh-key.pem ec2-user@54.197.12.24

# Dentro del servidor:
# Configurar AWS CLI
aws configure

# Autenticar con ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 311136344575.dkr.ecr.us-east-1.amazonaws.com

# Descargar imagen
docker pull 311136344575.dkr.ecr.us-east-1.amazonaws.com/mi-app-repo:backend-latest

# Ejecutar contenedor
docker run -d \
  --name backend \
  -p 80:5000 \
  -e DATABASE_URL="postgresql://dbadmin:123456Absrc@ing-soft-2-db.c2zsu6mmqs1n.us-east-1.rds.amazonaws.com:5432/miappdb" \
  311136344575.dkr.ecr.us-east-1.amazonaws.com/mi-app-repo:backend-latest

# Verificar
docker ps
docker logs backend

exit
```

### 7. Inicializar Base de Datos

```bash
# Copiar script SQL al EC2
scp -i terraform/ssh-key.pem scripts/init.sql ec2-user@54.197.12.24:~/

# Conectar y ejecutar desde máquina local (PowerShell)
ssh -i terraform/ssh-key.pem ec2-user@54.197.12.24 @"
cat > /tmp/init_db.py << 'EOFPY'
import psycopg2
conn = psycopg2.connect('postgresql://dbadmin:123456Absrc@ing-soft-2-db.c2zsu6mmqs1n.us-east-1.rds.amazonaws.com:5432/miappdb')
cur = conn.cursor()
with open('/tmp/init.sql', 'r') as f:
    sql = f.read()
cur.execute(sql)
conn.commit()
conn.close()
print('Database initialized successfully')
EOFPY
docker cp ~/init.sql backend:/tmp/init.sql
docker cp /tmp/init_db.py backend:/tmp/init_db.py
docker exec backend python /tmp/init_db.py
"@
```

### 8. Desplegar Frontend en EC2

```bash
# Conectar a EC2 Frontend
ssh -i terraform/ssh-key.pem ec2-user@98.92.205.135

# Configurar AWS CLI
aws configure

# Autenticar con ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 311136344575.dkr.ecr.us-east-1.amazonaws.com

# Descargar y ejecutar
docker pull 311136344575.dkr.ecr.us-east-1.amazonaws.com/mi-app-repo:frontend-latest
docker run -d \
  --name frontend \
  -p 80:3000 \
  311136344575.dkr.ecr.us-east-1.amazonaws.com/mi-app-repo:frontend-latest

# Verificar
docker ps
docker logs frontend

exit
```

### 9. Verificación Completa del Despliegue

```bash
# Verificar Backend
curl http://54.197.12.24/health
curl http://54.197.12.24/questions

# Verificar Frontend
curl -I http://98.92.205.135

# Verificar Application Load Balancer
curl -I http://ing-soft-2-alb-1167984181.us-east-1.elb.amazonaws.com

# Ver contenedores en Backend EC2
ssh -i terraform/ssh-key.pem ec2-user@54.197.12.24 "docker ps"

# Ver contenedores en Frontend EC2
ssh -i terraform/ssh-key.pem ec2-user@98.92.205.135 "docker ps"
```

### Verificar Estado de Recursos

```bash
# AWS Console
# - VPC: https://console.aws.amazon.com/vpc/
# - EC2: https://console.aws.amazon.com/ec2/
# - RDS: https://console.aws.amazon.com/rds/
# - Load Balancers: EC2 > Load Balancers
# - ECR: https://console.aws.amazon.com/ecr/

# Terraform
cd terraform
terraform state list  # Listar 29 recursos
terraform show        # Ver detalles completos
```