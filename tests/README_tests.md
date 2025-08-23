## P1-Backend: Documentación de Pruebas Unitarias

#### Tecnologías Utilizadas
- **Framework de Pruebas:** pytest 8.4.1
- **Cliente de Pruebas:** Flask Test Client
- **Formato de Datos:** JSON

#### Instalación de Dependencias
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias de pruebas
pip install pytest
```

#### Comandos Básicos

**Ejecutar todas las pruebas:**
```bash
python -m pytest -v
```

### Especificación de Pruebas

#### Suite: test_questions.py

##### Prueba 1: test_create_question_success()

**Propósito:** Verificar la creación exitosa de preguntas con publicación anónima

**Escenario de Prueba:**
- **Endpoint:** POST /questions
- **Datos válidos:** Título de 15 caracteres, descripción válida
- **Modo:** Publicación anónima activada
- **Formato:** JSON válido

**Datos de Entrada:**
```json
{
  "title": "¿Qué es Python?",
  "description": "Una breve duda sobre Python",
  "anonymous": true
}
```

**Verificaciones Realizadas:**
1. Status code 201 (Created)
2. Autor establecido como "Anónimo"
3. Respuesta en formato JSON válido

##### Prueba 2: test_create_question_invalid_title()

**Propósito:** Verificar el rechazo de títulos inválidos por longitud insuficiente

**Escenario de Prueba:**
- **Endpoint:** POST /questions
- **Datos inválidos:** Título de solo 3 caracteres (mínimo: 5)
- **Validación:** Rechazo por longitud insuficiente
- **Error esperado:** Status code 400

**Datos de Entrada:**
```json
{
  "title": "ola",
  "description": "Muy corto",
  "anonymous": false
}
```

**Verificaciones Realizadas:**
1. Status code 400 (Bad Request)
2. Rechazo de datos inválidos
3. Prevención de almacenamiento incorrecto
