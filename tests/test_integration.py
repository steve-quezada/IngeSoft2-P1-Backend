"""
Prueba de integración para flujo completo
"""
import pytest
import json
from app import create_app


@pytest.fixture
def client():
    """Cliente de prueba para la aplicación Flask"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_complete_flow(client):
    """Prueba de flujo completo: crear pregunta → obtener preguntas → añadir respuesta"""
    
    # 1. Crear pregunta
    question_data = {
        "title": "¿Cómo funciona Python?",
        "description": "Necesito ayuda básica",
        "author_name": "Usuario Test"
    }
    
    response = client.post('/questions', 
                          data=json.dumps(question_data),
                          content_type='application/json')
    assert response.status_code == 201
    question_id = response.json['id']
    
    # 2. Obtener todas las preguntas
    response = client.get('/questions')
    assert response.status_code == 200
    assert len(response.json) >= 1
    
    # 3. Añadir respuesta a la pregunta
    answer_data = {
        "text": "Python es un lenguaje interpretado"
    }
    
    response = client.post(f'/questions/{question_id}/answers',
                          data=json.dumps(answer_data),
                          content_type='application/json')
    assert response.status_code == 201
    
    # 4. Verificar que la respuesta se agregó
    response = client.get(f'/questions/{question_id}/answers')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['text'] == "Python es un lenguaje interpretado"
