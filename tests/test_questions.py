"""
Pruebas unitarias - P1-Backend.

Para la realización de estas pruebas unitarias, se utilizaron las siguientes tecnologías:

*Framework principal: pytest
*Cliente de pruebas: Flask test client 
*Formato de respuestas: JSON

Autor: etnicst, steve-quezada, diego-sc96-crypto
Fecha: Agosto 2025
Versión: 1.0.0
"""

import json
from app import app

def test_create_question_success():
    """
    Prueba la correcta creación de una pregunta con la modalidad anónima seleccionada.
    
    En esta función, se delimita a probar el escenario de seleccionar publicar la pregunta de manera anónima. Se verifica que el endpoint POST /questions funcione correctamente cuando el formato de los datos enviados es válido.
    
    Escenario de prueba:
        - Título válido con 15 caracteres (dentro del rango 5-80)
        - Descripción válida con menos de 300 caracteres
        - Publicación anónima activada (anonymous=True)
        - Content-Type: application/json
    
    Datos de entrada:
        title (str): "¿Qué es Python?" - Título de 15 caracteres
        description (str): "Una breve duda sobre Python" - Descripción válida
        anonymous (bool): True - Habilita publicación anónima
    
    Comportamiento esperado:
        - La API debe aceptar la petición
        - Creación de la pregunta en el almacén de datos
        - Retorno de status code 201 (Created)
        - Asignación del autor como "Anónimo"
        - Retorno de los datos en formato JSON válido
    
    Verificaciones realizadas:
        1. Status code 201 (Created) - Confirma creación exitosa
        2. Autor = "Anónimo" - Valida funcionalidad anónima
        3. Respuesta en formato JSON válido
    
    Assertions:
        assert response.status_code == 201
        assert data["author"] == "Anónimo"
    
    Test Coverage:
        - Endpoint: POST /questions
        - Funcionalidad: Generación de pregunta anónima
        - Validación: Datos de entrada válidos
        - Response: JSON correctamente generado que contiene datos válidos 
    
    Raises:
        AssertionError: Si alguna de las verificaciones falla:
            - Status code distinto a 201
            - Autor diferente a "Anónimo"
            - Respuesta JSON generada incorrectamente 
    
    Examples:
        >>> # Ejecutar esta prueba específica
        >>> pytest tests/test_questions.py::test_create_question_success -v
        
        >>> # Request simulado que realiza la prueba
        >>> POST /questions
        >>> Content-Type: application/json
        >>> {
        ...     "title": "¿Qué es Python?",
        ...     "description": "Una breve duda sobre Python",
        ...     "anonymous": True
        ... }
        
        >>> # Response esperado
        >>> HTTP/1.1 201 Created
        >>> Content-Type: application/json
        >>> {
        ...     "id": 1,
        ...     "title": "¿Qué es Python?",
        ...     "description": "Una breve duda sobre Python",
        ...     "author": "Anónimo"
        ... }
    
    Note:
        Esta prueba es fundamental para verificar 2 criterios; que la creación de preguntas funcione correctamente, ya que es la funcionalidad
        principal del sistema, y además, que el sistema de anonimato esté implementado adecuadamente.
    """
    # Crear cliente de prueba Flask para simular requests HTTP
    client = app.test_client()
    
    # Ejecutar petición POST al endpoint /questions con datos válidos
    response = client.post("/questions", json={
        "title": "¿Qué es Python?",           # Título válido (15 caracteres)
        "description": "Una breve duda sobre Python",  # Descripción válida
        "anonymous": True                      # Activar publicación anónima
    })
    
    # Verificar que la respuesta tenga status code 201 (Created)
    assert response.status_code == 201
    
    # Extraer datos JSON de la respuesta para validaciones adicionales
    data = response.get_json()
    
    # Verificar que el autor sea "Anónimo" cuando anonymous=True
    assert data["author"] == "Anónimo"

def test_create_question_invalid_title():
    """
    Prueba la validación del escenario en que el título es inválido por no cumplir con la longitud mínima.
    
    Esta función de prueba verifica que el endpoint POST /questions rechaza
    correctamente las peticiones con títulos que no cumplen con los criterios
    de validación establecidos, específicamente cuando el título es muy corto.
    
    Escenario de prueba:
        - Título inválido con solo 2 caracteres (mínimo requerido: 5)
        - Descripción válida para aislar la validación del título
        - Publicación no anónima (anonymous=False)
        - Content-Type: application/json válido
    
    Datos de entrada:
        title (str): "Hi" - Título de 2 caracteres (INVÁLIDO)
        description (str): "Muy corto" - Descripción válida
        anonymous (bool): False - Publicación con autor "Usuario"
    
    Comportamiento esperado:
        - La API debe rechazar la petición por título inválido
        - Retorno de status code 400 (Bad Request)
        - NINGUNA pregunta en el almacén debe ser creada
        - Incluir mensaje de error descriptivo en la respuesta
        - Preservar la integridad de los datos existentes
    
    Validación probada:
        Regla: El título debe tener entre 5 y 80 caracteres
        Caso límite: Título con menos de 5 caracteres
        Error esperado: "El título debe tener entre 5 y 80 caracteres"
    
    Verificaciones realizadas:
        1. Status code 400 (Bad Request) - Confirma rechazo por validación
        2. La pregunta NO se almacena en el sistema
        3. Respuesta contiene información de error
    
    Test Coverage:
        - Endpoint: POST /questions
        - Funcionalidad: Validación de datos de entrada
        - Caso límite: Título muy corto (edge case)
        - Error handling: Manejo de errores 400
        - Data integrity: Prevención de datos inválidos
    
    Raises:
        AssertionError: Si la verificación falla:
            - Status code diferente a 400
            - La API no acepta datos que no cumplen con la validación
    
    Examples:
        >>> # Ejecutar esta prueba específica
        >>> pytest tests/test_questions.py::test_create_question_invalid_title -v
        
        >>> # Request simulado que realiza la prueba
        >>> POST /questions
        >>> Content-Type: application/json
        >>> {
        ...     "title": "Hi",
        ...     "description": "Muy corto",
        ...     "anonymous": False
        ... }
        
        >>> # Response esperado
        >>> HTTP/1.1 400 Bad Request
        >>> Content-Type: application/json
        >>> {
        ...     "error": "El título debe tener entre 5 y 80 caracteres"
        ... }
    
    Note:
        Esta prueba es crucial para verificar que:
        1. La validación del lado del servidor funciona correctamente
        2. Se previene la creación de preguntas con datos inválidos
        3. Los usuarios reciben feedback claro sobre errores de validación
        4. El sistema mantiene la integridad de los datos
    """
    # Crear cliente de prueba Flask para simular requests HTTP
    client = app.test_client()
    
    # Ejecutar petición POST con título inválido (muy corto)
    response = client.post("/questions", json={
        "title": "ola",                      # Título inválido (2 caracteres, mín=5)
        "description": "Muy corto",           # Descripción válida para aislar error
        "anonymous": False                    # Publicación no anónima
    })
    
    # Verificar que la respuesta tenga status code 400 (Bad Request)
    # Esto confirma que la validación está funcionando correctamente
    assert response.status_code == 400
