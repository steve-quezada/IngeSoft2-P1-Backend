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