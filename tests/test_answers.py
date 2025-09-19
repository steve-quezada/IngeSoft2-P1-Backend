
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_answer(client):
    q = client.post("/questions", json={
        "title": "Pregunta con respuestas",
        "description": "",
        "anonymous": True
    }).get_json()

    response = client.post(f"/questions/{q['id']}/answers", json={
        "text": "Esta es una respuesta de prueba"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["text"] == "Esta es una respuesta de prueba"
    assert data["votes"] == 0

def test_vote_answer(client):
    q = client.post("/questions", json={
        "title": "Otra pregunta",
        "description": "",
        "anonymous": True
    }).get_json()

    a = client.post(f"/questions/{q['id']}/answers", json={
        "text": "Respuesta votable"
    }).get_json()


    res = client.post(f"/questions/{q['id']}/answers/{a['id']}/vote", json={"change": 1})
    assert res.status_code == 200
    data = res.get_json()
    assert data["votes"] == 1

    res = client.post(f"/questions/{q['id']}/answers/{a['id']}/vote", json={"change": -1})
    data = res.get_json()
    assert data["votes"] == 0