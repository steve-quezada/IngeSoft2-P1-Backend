# Práctica 5 - CI/CD, Elastic IPs y Route 53 [Dominio + DNS + Despliegue Automático]

### Integrantes
- **Kevin Steve Quezada Ordoñez** (@steve-quezada)
- **Etni Sarai Castro Sierra** (@etnicst)

### Repositorios
- Backend: [github.com/steve-quezada/IngeSoft2-P1-Backend](https://github.com/steve-quezada/IngeSoft2-P1-Backend)
- Frontend: [github.com/steve-quezada/IngeSoft2-P1-Frontend](https://github.com/steve-quezada/IngeSoft2-P1-Frontend)

### URLs de Producción
| Componente | URL |
|------------|-----|
| Frontend | http://is2-ss.me |
| Frontend (www) | http://www.is2-ss.me |
| Health Check | http://api.is2-ss.me/health |
| API Preguntas | http://api.is2-ss.me/questions |

### Prerequisitos
- Práctica 4 completada (infraestructura AWS desplegada)
- Dominio registrado (Namecheap via GitHub Student Pack)
- GitHub Secrets configurados para CI/CD
- AWS CLI y Terraform instalados

### Nuevos Recursos Implementados (Práctica 5)
- **Elastic IPs**: 2 IPs estáticas (Frontend + Backend)
- **Route 53 Hosted Zone**: Zona DNS para `is2-ss.me`
- **Route 53 Records**: 3 registros tipo A (root, www, api)
- **GitHub Actions CI/CD**: Pipelines con ECR + SSH Deploy
- **User Data**: Instalación automática de Docker en EC2

## Arquitectura con DNS

<div align="center">

```
            Internet
             │
             ▼
              ┌─────────────────────────────┐
              │     Namecheap (Registrar)   │
              │   Nameservers → Route 53    │
              └─────────────────────────────┘
             │
             ▼
              ┌─────────────────────────────┐
              │    AWS Route 53 DNS Zone    │
              │        is2-ss.me            │
              └─────────────────────────────┘
           │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  is2-ss.me  │  │www.is2-ss.me│  │api.is2-ss.me│
    │  (Record A) │  │  (Record A) │  │  (Record A) │
    └─────────────┘  └─────────────┘  └─────────────┘
           │                │                │
           └────────────────┼────────────────┘
           │
           ┌────────────────┴────────────────┐
           ▼                                 ▼
    ┌──────────────────┐            ┌──────────────────┐
    │   Elastic IP     │            │   Elastic IP     │
    │  (Frontend EIP)  │            │  (Backend EIP)   │
    │   18.209.X.X     │            │   54.197.X.X     │
    └──────────────────┘            └──────────────────┘
           │                                 │
           ▼                                 ▼
    ┌──────────────────┐            ┌──────────────────┐
    │   EC2 Frontend   │            │   EC2 Backend    │
    │    t3.micro      │            │    t3.micro      │
    │  React + Nginx   │            │  Flask + Gunicorn│
    │    Port 80       │◄───────────│    Port 80       │
    └──────────────────┘   fetch    └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │  RDS PostgreSQL  │
                                    │   db.t3.micro    │
                                    │  Private Subnet  │
                                    └──────────────────┘
```

</div>

## Pipeline CI/CD

<div align="center">

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Workflow                          │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌─────────────────┐       ┌─────────────────┐      ┌─────────────────┐
│    Job: test    │       │ Job: build-push │      │   Job: deploy   │
│                 │       │                 │      │                 │
│   pytest/vitest │─────▶│  docker build   │─────▶│    SSH to EC2   │
│  Run tests      │       │  docker push    │      │  docker pull    │
│                 │       │  → AWS ECR      │      │  docker run     │
└─────────────────┘       └─────────────────┘      └─────────────────┘
```

</div>

## Estructura de Archivos Nuevos

```
IngeSoft2-P1-Backend/
├── .github/workflows/
│   └── backend-docker-build.yml    ← Pipeline CI/CD Backend
├── terraform/
│   ├── main.tf                     ← +Elastic IPs, Route 53
│   ├── variables.tf                ← +domain_name
│   └── outputs.tf                  ← +nameservers, elastic_ips

IngeSoft2-P1-Frontend/
├── .github/workflows/
│   └── frontend-docker-build.yml   ← Pipeline CI/CD Frontend
```

## GitHub Secrets Requeridos

| Secret | Descripción |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | Access Key de IAM |
| `AWS_SECRET_ACCESS_KEY` | Secret Key de IAM |
| `ECR_REGISTRY` | URL del registry ECR |
| `EC2_SSH_KEY` | Llave privada SSH |
| `BACKEND_HOST` | IP/Dominio del Backend |
| `FRONTEND_HOST` | IP/Dominio del Frontend |
| `DATABASE_URL` | Connection string PostgreSQL |
| `VITE_API_URL` | URL del Backend para React |

## Configuración Paso a Paso

### 1. Aplicar Cambios de Terraform

```bash
cd terraform

# Ver los nuevos recursos
terraform plan

# Aplicar (crea Elastic IPs + Route 53)
terraform apply

# Ver los nameservers generados
terraform output route53_nameservers
```

### 2. Configurar Nameservers en Namecheap

1. Ir a [Namecheap Dashboard](https://ap.www.namecheap.com/)
2. Domain List → Manage → Nameservers
3. Seleccionar "Custom DNS"
4. Agregar los 4 nameservers de Route 53:
   ```
   ns-XXX.awsdns-XX.org
   ns-XXX.awsdns-XX.co.uk
   ns-XXX.awsdns-XX.com
   ns-XXX.awsdns-XX.net
   ```
5. Guardar cambios (propagación: 5-30 minutos)

### 3. Configurar GitHub Secrets

```bash
# En cada repositorio:
# Settings → Secrets and variables → Actions → New repository secret

# Backend Secrets:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
ECR_REGISTRY
EC2_SSH_KEY
BACKEND_HOST
DATABASE_URL

# Frontend Secrets (adicional):
FRONTEND_HOST
VITE_API_URL
```

### 4. Trigger del Pipeline

```bash
# Hacer push para activar el pipeline
git push origin main
```

## Verificación Final

```bash
# DNS Resolution
nslookup is2-ss.me
# → Debe mostrar la Elastic IP del Frontend

nslookup api.is2-ss.me
# → Debe mostrar la Elastic IP del Backend

# Aplicación Frontend
curl -I http://is2-ss.me
# → HTTP/1.1 200 OK

# API Backend
curl http://api.is2-ss.me/health
# → {"service":"backend","status":"healthy"}

curl http://api.is2-ss.me/questions
# → [{"id":1,"text":"..."},...]

# GitHub Actions
# → Verificar que los 3 jobs (test, build-and-push, deploy)
```

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
ssh -i terraform/temp-key.pem ec2-user@54.197.12.24

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
scp -i terraform/temp-key.pem scripts/init.sql ec2-user@54.197.12.24:~/

# Conectar y ejecutar desde máquina local (PowerShell)
ssh -i terraform/temp-key.pem ec2-user@54.197.12.24 @"
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
ssh -i terraform/temp-key.pem ec2-user@98.92.205.135

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
ssh -i terraform/temp-key.pem ec2-user@54.197.12.24 "docker ps"

# Ver contenedores en Frontend EC2
ssh -i terraform/temp-key.pem ec2-user@98.92.205.135 "docker ps"
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

# Práctica 3 CI/CD - Pipeline GitHub Actions

## Estructura de Repositorios

```
Proyecto Completo/
├── IngeSoft2-P1-Backend/              ← Repositorio Backend
│   ├── .github/workflows/             ←  CI/CD Pipelines
│   │   └── backend-docker-build.yml   ← Pipeline Backend
│   ├── Dockerfile                     ← Multi-stage build
│   ├── app.py                         ← Flask API
│   ├── requirements.txt               ← Dependencias Python (+ requests)
│   ├── src/                           ← Código fuente
│   ├── tests/                         ← Testing (20 tests unitarios)
│   │   ├── test_all.py                ← Tests principales
│   │   ├── test_answers.py            ← Tests respuestas
│   │   ├── test_integration.py        ← Tests integración
│   │   ├── test_questions.py          ← Tests preguntas
│   │   └── test_refactored.py         ← Tests funcionales
│   └── docker/                        ← Orquestación
│       ├── docker-compose.yml         ← Desarrollo
│       └── docker-compose.prod.yml    ← Producción
│
└── IngeSoft2-P1-Frontend/             ← Repositorio Frontend
    ├── .github/workflows/             ←  CI/CD Pipelines
    │   └── frontend-docker-build.yml  ← Pipeline Frontend
    ├── Dockerfile                     ← Multi-stage build
    ├── proyecto-is2/                  ← Proyecto React/Vite
    │   ├── package.json               ← Dependencias + scripts test
    │   ├── package-lock.json          ← Lock para reproducibilidad
    │   ├── vite.config.js             ← Config Vitest
    │   ├── src/                       ← Código React
    │   │   ├── __tests__/             ←  Tests frontend (Vitest)
    │   │   │   ├── App.test.jsx       ← Test componente principal
    │   │   │   ├── InputPregunta.test.jsx  ← Test formulario
    │   │   │   └── frontend-integration.test.js  ← Test integración
    │   │   └── test/setup.js          ← Setup testing-library
    │   └── public/                    ← Assets estáticos
```

---

## GitHub Actions

#### Jobs Implementados

##### **Job 1: `test`** 
**Configuración del entorno:**
- Backend: Python 3.11 + pip cache
- Frontend: Node.js 20 + npm cache

**Instalación de dependencias:**
- Backend: `pip install -r requirements.txt`
- Frontend: `npm ci --legacy-peer-deps`

**Ejecución de pruebas unitarias:**
- Backend: 20 tests con `pytest`
- Frontend: 9 tests con `Vitest`

**Pruebas de instalación:**
- Verificación de imports
- Validación de creación
- Checks de versiones y build

##### **Job 2: `build-and-push`**
Solo se ejecuta si `test` fue exitoso

**Autenticación segura:**
- `docker/login-action@v3` con GITHUB_TOKEN
- Acceso automático a GitHub Container Registry

**Construcción de imágenes:**
- Build desde Dockerfile multi-stage

**Etiquetado:**
```yaml
tags:
  - type=ref,event=branch            # nombre-rama
  - type=ref,event=pr                # PR-número
  - type=sha,prefix=sha-             # SHA commit
  - type=raw,value=latest            # latest (rama main)
  - type=semver,pattern={{version}}  # versión semántica
```

**Publicación automática:**
- Push a `ghcr.io/steve-quezada/ingesoft2-p1-backend`
- Push a `ghcr.io/steve-quezada/ingesoft2-p1-frontend`
- Imágenes públicas y listas para uso

## Guía de Uso del Sistema CI/CD

### Autenticación para Imágenes Privadas

Las imágenes en GitHub Container Registry son privadas y requieren autenticación para su descarga.

#### Paso 1: Crear Personal Access Token (Classic)

1. **Ir a GitHub Settings:**
   - Ve a tu perfil de GitHub → Settings
   - O accede directamente: https://github.com/settings/tokens

2. **Generar nuevo token:**
   - Click en "Developer settings" (panel izquierdo)
   - Click en "Personal access tokens"
   - Click en "Tokens (classic)"
   - Click en "Generate new token" → "Generate new token (classic)"

3. **Configurar el token:**
   ```
   Note: Docker GHCR Access
   
   Permisos requeridos:
        read:packages    - Descargar imágenes de contenedor
        write:packages   - Subir imágenes (opcional)
        delete:packages  - Eliminar imágenes (opcional)
        repo             - Acceso a repositorios privados
   ```

4. **Copiar el token:** 
   - Click "Generate token"
   - Copia el token inmediatamente (solo se muestra una vez)
   - Guárdalo en un lugar seguro

#### Paso 2: Autenticar Docker con GHCR

```bash
# Login interactivo
docker login ghcr.io

# Cuando solicite credenciales:
# Username: usuario-github
# Password: ghp_xxxxxxxxxxxxxxxxxxxx (PAT) [Token]
```

### Despliegue Automático

Antes de ejecutar los comandos Docker o Docker Desktop debe estar en ejecución.

Las imágenes se construyen automáticamente en cada push. Para usar la última versión:

```bash
# 1. Clonar repositorio backend
git clone https://github.com/steve-quezada/IngeSoft2-P1-Backend.git
cd IngeSoft2-P1-Backend

# 2. Iniciar sistema completo con imágenes del registry
cd docker
docker-compose -f docker-compose.prod.yml up -d

# 3. Verificar servicios
docker-compose -f docker-compose.prod.yml ps

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000

# 5. Parar servicios
docker-compose -f docker-compose.prod.yml down
```

# Práctica 2

### Estructura de Repositorios
```
Proyecto Completo/
├── IngeSoft2-P1-Backend/              ← Repositorio Backend
│   ├── .github/workflows/
│   │   └── backend-docker-build.yml   ← CI/CD Backend
│   ├── Dockerfile                     ← Multi-stage build
│   ├── .dockerignore                  ← Optimización
│   ├── supervisord.conf               ← Gestión procesos
│   ├── app.py                         ← Flask API
│   ├── requirements.txt               ← Dependencias Python
│   ├── src/                           ← Código fuente
│   ├── tests/                         ← Testing
│   └── docker/                        ← Orquestación
│       ├── docker-compose.yml         ← Desarrollo
│       └── docker-compose.prod.yml    ← Producción
│
└── IngeSoft2-P1-Frontend/             ← Repositorio Frontend
    ├── .github/workflows/
    │   └── frontend-docker-build.yml  ← CI/CD Frontend
    ├── Dockerfile                     ← Multi-stage build
    ├── .dockerignore                  ← Optimización
    ├── package.json                   ← Dependencias Node.js
    ├── src/                           ← Código React
    └── public/                        ← Assets estáticos
```

---

## Guía de Instalación

### Opción 1: Despliegue Producción
```bash
# 1. Clonar repositorio backend
git clone https://github.com/etnicst/IngeSoft2-P1-Backend.git
cd IngeSoft2-P1-Backend

# 2. Desplegar sistema completo
cd docker
docker-compose -f docker-compose.prod.yml up -d

# 3. Verificar servicios
docker-compose -f docker-compose.prod.yml ps

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# Health Check: http://localhost:5000/health
```

**Nota:** Las imágenes Docker están configuradas como públicas en GitHub Container Registry, por lo que no es necesario autenticarse para descargarlas y usar el proyecto.

### Opción 2: Desarrollo Local
```bash
# 1. Clonar ambos repositorios
git clone https://github.com/etnicst/IngeSoft2-P1-Backend.git
git clone https://github.com/etnicst/IngeSoft2-P1-Frontend.git

# 2. Iniciar en modo desarrollo
cd IngeSoft2-P1-Backend/docker
docker-compose up -d

# 3. Los cambios en código se reflejan automáticamente (hot reload)
```

---

## Comandos de Gestión

### Gestión Básica
```bash
# Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver estado de servicios
docker-compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Parar servicios
docker-compose -f docker-compose.prod.yml down

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

# Reiniciar servicio específico
docker-compose -f docker-compose.prod.yml restart backend
```

### Debugging y Mantenimiento
```bash
# Acceder al contenedor backend
docker exec -it backend-flask-prod /bin/bash

# Acceder al contenedor frontend
docker exec -it frontend-react-prod /bin/sh

# Ver recursos utilizados
docker stats

# Inspeccionar red
docker network inspect docker_app-network

# Ver volúmenes
docker volume ls
docker volume inspect docker_backend_logs
```

# # Práctica 1 - Sistema de Preguntas - Facultad de Ciencias

### Descripción del Proyecto

Sistema de preguntas y respuestas que integra un **frontend React + Vite** con un **backend Flask**. Permite a los usuarios crear preguntas, visualizarlas y navegar entre ellas.


### Arquitectura del Sistema

#### Stack Tecnológico:
- **Frontend:** React 19.1.1 + Vite 7.1.2 + React Router 7.8.2
- **Backend:** Python 3.13+ + Flask 2.3.3 + Flask-CORS 4.0.0
- **Testing:** pytest 7.0.0+
- **Linting:** ESLint 9.33.0

#### Estructura del Proyecto

```
Ingenieria de Software 2/
├── data.json                    # Archivo de datos compartido
├── Proyecto Back/               # Backend Flask
│   ├── app.py                   # Punto de entrada principal (Application Factory)
│   ├── requirements.txt         # Dependencias Python
│   ├── data.json               # Persistencia local de datos
│   ├── config/                 # Configuración de la aplicación
│   │   ├── __init__.py
│   │   └── config.py           # Configuraciones por ambiente
│   ├── src/                    # Código fuente principal
│   │   ├── __init__.py
│   │   ├── models/             # Modelos de datos
│   │   │   ├── __init__.py
│   │   │   └── question.py     # Modelo de preguntas
│   │   ├── services/           # Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   └── question_service.py # Servicio de preguntas
│   │   ├── routes/             # Controladores/Endpoints
│   │   │   ├── __init__.py
│   │   │   └── questions.py    # Rutas de la API
│   │   └── utils/              # Utilidades
│   │       ├── __init__.py
│   │       └── validators.py   # Validadores de datos
│   ├── tests/                  # Suite de pruebas
│   │   ├── README_tests.md     # Documentación de pruebas
│   │   ├── test_questions.py   # Pruebas de preguntas
│   │   └── test_answers.py     # Pruebas de respuestas
│   └── htmlcov/                # Reportes de cobertura HTML
├── Proyecto Front/             # Frontend React + Vite
│   └── proyecto-is2/           # Aplicación React
│       ├── package.json        # Dependencias Node.js
│       ├── vite.config.js      # Configuración Vite
│       ├── eslint.config.js    # Configuración ESLint
│       ├── index.html          # Página principal
│       └── src/
│           ├── App.jsx         # Componente principal y rutas
│           ├── main.jsx        # Punto de entrada React
│           ├── componentes/    # Componentes reutilizables
│           │   ├── HomeButton.jsx
│           │   └── InputPregunta.jsx
│           ├── pages/          # Páginas de la aplicación
│           │   ├── Home.jsx    # Página principal
│           │   ├── Pregunta.jsx # Vista individual
│           │   └── ListaPreguntas.jsx # Lista de preguntas
│           └── services/       # Servicios de comunicación
│               └── api.js      # Cliente API REST
└── README.md                   # Documentación del proyecto
```

## Instalación y Configuración

### Prerrequisitos

- **Python 3.13+** con pip instalado
- **Node.js 18+** con npm instalado
- **Git** para clonar los repositorios

### Configuración del Entorno

**Importante:** Este proyecto está dividido en **dos repositorios separados**:

- **Backend**: `IngeSoft2-P1-Backend` 
- **Frontend**: `IngeSoft2-P1-Frontend`

**Ambos repositorios deben estar clonados al mismo nivel**

### Paso 1: Configurar el Backend (Flask)

1. **Crear y activar entorno virtual de Python:**
   ```bash
   # Crear entorno virtual
   python -m venv .venv
   
   # Activar entorno virtual
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   
   # Windows (CMD)
   .venv\Scripts\activate.bat
   
   # Linux/macOS
   source .venv/bin/activate
   ```

2. **Navegar al directorio del backend:**
   ```bash
   cd "Proyecto Back"
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verificar instalación ejecutando las pruebas:**
   ```bash
   pytest tests/ -v --cov=src
   ```

### Paso 2: Configurar el Frontend (React + Vite)

1. **Navegar al directorio del frontend:**
   ```bash
   cd "Proyecto Front/proyecto-is2"
   ```

2. **Instalar dependencias de Node.js:**
   ```bash
   npm install
   ```

3. **Verificar instalación ejecutando el linter:**
   ```bash
   npm run lint
   ```

## Ejecución del Sistema

**Siempre ejecutar primero el backend y luego el frontend**

### Paso 1: Iniciar el Backend (Terminal 1)

```bash
# Desde el directorio raíz del proyecto
python ".\Proyecto Back\app.py"
```

El backend se iniciará en: **http://localhost:5000**

### Paso 2: Iniciar el Frontend (Terminal 2)

```bash
# Desde el directorio del frontend
cd "Proyecto Front/proyecto-is2"
npm run dev
```

El frontend se iniciará en: **http://localhost:5173**

### Paso 3: Abrir la Aplicación

Abrir el navegador en: **http://localhost:5173/**

## Testing
La información se encuentra en ```\tests\README.md```
