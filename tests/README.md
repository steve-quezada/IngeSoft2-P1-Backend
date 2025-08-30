# Tests - P1-Backend

Este directorio contiene todos los tests unitarios para el proyecto P1-Backend.

## Estructura de Tests

```
tests/
├── conftest.py          # Configuración y fixtures de pytest
├── test_refactored.py   # Test de integración con servidor real
├── test_questions.py    # Tests legacy de preguntas (2 tests)
├── test_all.py          # PRINCIPAL - Tests unificados (14 tests)
├── test_answers.py      # Tests legacy de respuestas (2 tests)
└── README.md            # Esta documentación
```

### `test_all.py`

#### **TESTS DE PREGUNTAS** (5 tests)
```python
def test_create_question_anonymous(client)           # Pregunta anónima
def test_create_question_with_author(client)         # Pregunta con autor
def test_create_question_invalid_title_short(client) # Título muy corto (<5)
def test_create_question_invalid_title_long(client)  # Título muy largo (>80)
def test_list_questions(client)                      # Listar preguntas
```

#### **TESTS DE RESPUESTAS** (3 tests)
```python
def test_create_answer(client)           # Crear respuesta válida
def test_create_answer_empty_text(client) # Validar texto vacío
def test_list_answers(client)            # Listar respuestas
```

#### **TESTS DE VOTACIÓN** (3 tests)
```python
def test_vote_answer_upvote(client)      # Voto positivo (+1)
def test_vote_answer_downvote(client)    # Voto negativo (-1)
def test_vote_answer_sequence(client)    # Secuencia de votos
```

#### **TESTS DE CASOS EDGE** (3 tests)
```python
def test_answer_nonexistent_question(client)  # Pregunta inexistente
def test_vote_nonexistent_answer(client)      # Respuesta inexistente
def test_invalid_json_data(client)            # JSON inválido
```

## Cómo Ejecutar los Tests

### Prerequisitos
```bash
# Instalar dependencias
pip install pytest flask
```

### Ejecutar Todos los Tests
```bash
# Desde la carpeta raíz del proyecto (Proyecto Back)

# Todos los tests
pytest tests/ -v

# Tests unificados
pytest tests/test_all.py -v

# Tests legacy
pytest tests/test_questions.py -v

pytest tests/test_answers.py -v

# Test con servidor real
python tests/test_refactored.py
```

### Ejecutar Tests con Coverage
```bash
# Instalar coverage
pip install pytest-cov

# Ejecutar con reporte de cobertura
pytest tests/ --cov=src --cov-report=html
```
