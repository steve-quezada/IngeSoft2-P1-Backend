## P1-Backend: API REST

### Descripción del Proyecto

Sistema backend con Flask que implementa una API REST para un foro de preguntas y respuestas.

### Funcionalidades Implementadas

#### Módulo Principal:

1. **Creación de Preguntas**

2. **Listado de Preguntas**

3. **Sistema de Validación**

### Arquitectura del Sistema

- **Lenguaje:** Python 3.13+
    - pip (Gestor de paquetes)
- **Framework Web:** Flask 2.3.3

#### Estructura del Proyecto

```
P1-Backend/
├── app.py                          # Punto de entrada principal (Application Factory)
├── requirements.txt                # Dependencias del proyecto
├── data.json                       # Archivo de persistencia de datos
├── config/                         # Configuración de la aplicación
│   ├── __init__.py
│   └── config.py                   # Configuraciones por ambiente
├── src/                            # Código fuente principal
│   ├── __init__.py
│   ├── models/                     # Modelos de datos
│   │   ├── __init__.py
│   │   └── question.py             # Modelos de preguntas y respuestas
│   ├── services/                   # Lógica de negocio
│   │   ├── __init__.py
│   │   └── question_service.py     # Servicio de preguntas y respuestas
│   ├── routes/                     # Controladores/Endpoints
│   │   ├── __init__.py
│   │   └── questions.py            # Rutas de preguntas y respuestas
│   └── utils/                      # Utilidades
│       ├── __init__.py
│       └── validators.py           # Validadores de datos
└── tests/                          # Pruebas unitarias
    ├── README_tests.md
    ├── test_answers.py
    └── test_questions.py
```

#### Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/etnicst/IngeSoft2-P1-Backend.git
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   ```

3. **Activar entorno virtual:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

4. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución del Sistema

```bash
python app.py
```

#### Configuración de Servidor
El servidor se ejecuta por defecto en:
- **Host:** 127.0.0.1 (localhost)
- **Puerto:** 5000
- **Modo:** Debug activado
- **URL de acceso:** http://127.0.0.1:5000

#### Salida Esperada del Sistema
```
* Serving Flask app 'app'
* Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
* Restarting with stat
* Debugger is active!
* Debugger PIN: [PIN-NUMBER]
```

### Documentación de la API

#### URL Base
```
http://127.0.0.1:5000
```

#### Endpoint 1: Crear Pregunta

**Método:** POST  
**Ruta:** /questions  
**Content-Type:** application/json

**Parámetros de Entrada:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| title | string | Sí | Título de la pregunta (5-80 caracteres) |
| description | string | No | Descripción detallada (máximo 300 caracteres) |
| anonymous | boolean | No | Modo de publicación anónima (default: false) |

**Ejemplo de Petición:**
```json
{
  "title": "¿Cómo implementar una API REST con Flask?",
  "description": "Necesito ayuda para crear endpoints básicos",
  "anonymous": false
}
```

**Respuesta Exitosa (HTTP 201):**
```json
{
  "id": 1,
  "title": "¿Cómo implementar una API REST con Flask?",
  "description": "Necesito ayuda para crear endpoints básicos",
  "author": "Usuario"
}
```

**Respuesta de Error (HTTP 400):**
```json
{
  "error": "El título debe tener entre 5 y 80 caracteres"
}
```

#### Endpoint 2: Listar Preguntas

**Método:** GET  
**Ruta:** /questions

**Respuesta Exitosa (HTTP 200):**
```json
[
  {
    "id": 3,
    "title": "Pregunta más reciente",
    "description": "Esta aparece primero",
    "author": "Anónimo"
  },
  {
    "id": 2,
    "title": "Segunda pregunta",
    "description": "Esta aparece segunda",
    "author": "Usuario"
  },
  {
    "id": 1,
    "title": "Primera pregunta",
    "description": "Esta aparece última",
    "author": "Usuario"
  }
]
```

**Respuesta Exitosa (HTTP 200):**
```json
[]
```

### Prueba rapida del Sistema
```bash
# Crear pregunta
curl -X POST "http://127.0.0.1:5000/questions" -H "Content-Type: application/json" -d '{"title": "¿Qué es Flask?", "description": "Duda sobre Flask", "anonymous": false}'

# Listar preguntas
curl http://127.0.0.1:5000/questions
```
