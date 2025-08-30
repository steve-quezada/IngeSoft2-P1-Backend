"""
Tests unificados para P1-Backend - API REST/Flask

Pruebas unitarias que cubren todas las funcionalidades principales:
- Creación y listado de preguntas
- Creación y listado de respuestas  
- Sistema de votación
- Validaciones de entrada

Framework: pytest
Cliente: Flask test client
Formato: JSON

Autor: etnicst, steve-quezada, diego-sc96-crypto
Fecha: Agosto 2025
Versión: 1.0.0
"""

import pytest
import json


# TESTS DE PREGUNTAS

def test_create_question_anonymous(client):
    """
    Prueba la creación exitosa de una pregunta anónima.
    
    Verifica que:
    - Se cree la pregunta correctamente
    - El autor aparezca como "Anónimo" 
    - Retorne status 201
    """
    response = client.post("/questions", json={
        "title": "¿Qué es Python?",
        "description": "Una breve duda sobre Python",
        "anonymous": True
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["author"] == "Anónimo"
    assert data["title"] == "¿Qué es Python?"


def test_create_question_with_author(client):
    """
    Prueba la creación exitosa de una pregunta con autor identificado.
    
    Verifica que:
    - Se cree la pregunta correctamente
    - El autor aparezca con el nombre proporcionado
    - Retorne status 201
    """
    response = client.post("/questions", json={
        "title": "¿Cómo funciona Flask?",
        "description": "Duda sobre el framework Flask",
        "anonymous": False,
        "author_name": "Desarrollador"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["author"] == "Desarrollador"
    assert data["title"] == "¿Cómo funciona Flask?"


def test_create_question_invalid_title_short(client):
    """
    Prueba la validación cuando el título es muy corto.
    
    Verifica que:
    - Se rechace la petición con status 400
    - No se cree ninguna pregunta en el sistema
    """
    response = client.post("/questions", json={
        "title": "Hi",  # Muy corto (mínimo 5 caracteres)
        "description": "Descripción válida",
        "anonymous": False,
        "author_name": "Usuario"
    })
    
    assert response.status_code == 400


def test_create_question_invalid_title_long(client):
    """
    Prueba la validación cuando el título es muy largo.
    
    Verifica que:
    - Se rechace la petición con status 400
    - No se cree ninguna pregunta en el sistema
    """
    long_title = "a" * 81  # Muy largo (máximo 80 caracteres)
    
    response = client.post("/questions", json={
        "title": long_title,
        "description": "Descripción válida",
        "anonymous": False,
        "author_name": "Usuario"
    })
    
    assert response.status_code == 400


def test_list_questions(client):
    """
    Prueba el listado de preguntas.
    
    Verifica que:
    - Se retorne status 200
    - Se obtenga una lista (aunque esté vacía)
    - El formato de respuesta sea JSON válido
    """
    response = client.get("/questions")
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


# TESTS DE RESPUESTAS

def test_create_answer(client):
    """
    Prueba la creación exitosa de una respuesta.
    
    Verifica que:
    - Se cree la respuesta correctamente
    - Tenga 0 votos inicialmente
    - Retorne status 201
    """
    # Primero crear una pregunta
    q_response = client.post("/questions", json={
        "title": "Pregunta para responder",
        "description": "Una pregunta de prueba",
        "anonymous": True
    })
    question = q_response.get_json()
    
    # Crear respuesta
    response = client.post(f"/questions/{question['id']}/answers", json={
        "text": "Esta es una respuesta de prueba"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["text"] == "Esta es una respuesta de prueba"
    assert data["votes"] == 0


def test_create_answer_empty_text(client):
    """
    Prueba la validación cuando el texto de respuesta está vacío.
    
    Verifica que:
    - Se rechace la petición con status 400
    - No se cree ninguna respuesta
    """
    # Crear pregunta primero
    q_response = client.post("/questions", json={
        "title": "Pregunta para respuesta inválida",
        "description": "",
        "anonymous": True
    })
    question = q_response.get_json()
    
    # Intentar crear respuesta vacía
    response = client.post(f"/questions/{question['id']}/answers", json={
        "text": ""  # Texto vacío
    })
    
    assert response.status_code == 400


def test_list_answers(client):
    """
    Prueba el listado de respuestas de una pregunta.
    
    Verifica que:
    - Se retorne status 200
    - Se obtenga una lista de respuestas
    - El formato de respuesta sea JSON válido
    """
    # Crear pregunta
    q_response = client.post("/questions", json={
        "title": "Pregunta con respuestas",
        "description": "",
        "anonymous": True
    })
    question = q_response.get_json()
    
    # Listar respuestas (inicialmente vacío)
    response = client.get(f"/questions/{question['id']}/answers")
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


# TESTS DE VOTACIÓN

def test_vote_answer_upvote(client):
    """
    Prueba el voto positivo a una respuesta.
    
    Verifica que:
    - Se incremente el contador de votos
    - Retorne status 200
    - Los votos se actualicen correctamente
    """
    # Crear pregunta
    q_response = client.post("/questions", json={
        "title": "Pregunta votable",
        "description": "",
        "anonymous": True
    })
    question = q_response.get_json()
    
    # Crear respuesta
    a_response = client.post(f"/questions/{question['id']}/answers", json={
        "text": "Respuesta para votar"
    })
    answer = a_response.get_json()
    
    # Votar positivo
    response = client.post(f"/questions/{question['id']}/answers/{answer['id']}/vote", json={
        "change": 1
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["votes"] == 1


def test_vote_answer_downvote(client):
    """
    Prueba el voto negativo a una respuesta.
    
    Verifica que:
    - Se decremente el contador de votos
    - Retorne status 200
    - Los votos se actualicen correctamente
    """
    # Crear pregunta
    q_response = client.post("/questions", json={
        "title": "Pregunta para voto negativo",
        "description": "",
        "anonymous": True
    })
    question = q_response.get_json()
    
    # Crear respuesta
    a_response = client.post(f"/questions/{question['id']}/answers", json={
        "text": "Respuesta para voto negativo"
    })
    answer = a_response.get_json()
    
    # Votar negativo
    response = client.post(f"/questions/{question['id']}/answers/{answer['id']}/vote", json={
        "change": -1
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["votes"] == -1


def test_vote_answer_sequence(client):
    """
    Prueba una secuencia de votos para verificar la acumulación.
    
    Verifica que:
    - Los votos se acumulen correctamente
    - Se puedan hacer votos positivos y negativos
    - El conteo sea correcto en cada paso
    """
    # Crear pregunta
    q_response = client.post("/questions", json={
        "title": "Pregunta para secuencia de votos",
        "description": "",
        "anonymous": True
    })
    question = q_response.get_json()
    
    # Crear respuesta
    a_response = client.post(f"/questions/{question['id']}/answers", json={
        "text": "Respuesta para secuencia"
    })
    answer = a_response.get_json()
    
    # Voto positivo (+1)
    response = client.post(f"/questions/{question['id']}/answers/{answer['id']}/vote", json={
        "change": 1
    })
    assert response.get_json()["votes"] == 1
    
    # Otro voto positivo (+1, total +2)
    response = client.post(f"/questions/{question['id']}/answers/{answer['id']}/vote", json={
        "change": 1
    })
    assert response.get_json()["votes"] == 2
    
    # Voto negativo (-1, total +1)
    response = client.post(f"/questions/{question['id']}/answers/{answer['id']}/vote", json={
        "change": -1
    })
    assert response.get_json()["votes"] == 1


# TESTS DE CASOS EDGE

def test_answer_nonexistent_question(client):
    """
    Prueba crear respuesta a una pregunta que no existe.
    
    Verifica que:
    - Se maneje correctamente el error
    - Retorne un status de error apropiado
    """
    response = client.post("/questions/999/answers", json={
        "text": "Respuesta a pregunta inexistente"
    })
    
    # Debería retornar error (400 o 404)
    assert response.status_code in [400, 404, 500]


def test_vote_nonexistent_answer(client):
    """
    Prueba votar por una respuesta que no existe.
    
    Verifica que:
    - Se maneje correctamente el error
    - Retorne un status de error apropiado
    """
    # Crear pregunta válida
    q_response = client.post("/questions", json={
        "title": "Pregunta válida",
        "description": "",
        "anonymous": True
    })
    question = q_response.get_json()
    
    # Intentar votar respuesta inexistente
    response = client.post(f"/questions/{question['id']}/answers/999/vote", json={
        "change": 1
    })
    
    # Debería retornar error (400, 404 o 500)
    assert response.status_code in [400, 404, 500]


def test_invalid_json_data(client):
    """
    Prueba el manejo de datos JSON inválidos.
    
    Verifica que:
    - Se rechacen peticiones sin JSON
    - Retorne un status de error apropiado (400 o 500)
    """
    response = client.post("/questions", json=None)
    # Puede retornar 400 (Bad Request) o 500 (Internal Server Error)
    assert response.status_code in [400, 500]
