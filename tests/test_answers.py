"""
Tests para funcionalidad de respuestas - Legacy
Mantiene compatibilidad con la estructura refactorizada
"""

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