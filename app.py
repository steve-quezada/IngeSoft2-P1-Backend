"""
P1-Backend - API REST/Flask

Módulo que implementa una API que permite:
- Crear preguntas con título y descripción.
- Listar preguntas.

Endpoints disponibles:
- POST /questions: Crear nueva pregunta
- GET /questions: Listar todas las preguntas

Autor: etnicst, steve-quezada, diego-sc96-crypto

Fecha: Agosto 2025
Versión: 1.0.0
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os

file = "data.json"

# Configuración Flask
app = Flask(__name__)
CORS(app)

# Almacenamiento para las preguntas
questions = []

@app.route("/questions", methods=["POST"])
def create_question():
    """
    Endpoint para crear preguntas con título, descripción, privacidad y autor.
    
    Request Body (JSON):
        title (str): Título. (Debe tener entre 5 y 80 caracteres)
        description (str, opcional): Descripción. (Máximo 300 caracteres)
        anonymous (bool, opcional): La pregunta debe publicarse en anónimo. (por defecto: False)
        author_name (str, opcional): Nombre del autor. (Máximo 50 caracteres)
        
    Nota: Debe proporcionar author_name O marcar anonymous=True, no ambos vacíos.

    Returns:
        tuple: Una tupla con la respuesta JSON y el código HTTP.
        
        En caso positivo:
            dict: Diccionario con los datos:
                - id (int): Identificador 
                - title (str): Título
                - description (str): Descripción
                - author (str): "Anónimo" o nombre del autor
        
        En caso negativo:
            dict: Diccionario con mensaje de error:
                - error (str): Descripción del error
    """
    # Obtener datos del cuerpo de JSON
    data = request.json
    title = data.get("title", "")
    description = data.get("description", "")
    anonymous = data.get("anonymous", False)
    author_name = data.get("author_name", "").strip()

    # Validación del título
    if not (5 <= len(title) <= 80):
        return jsonify({"error": "El título debe tener entre 5 y 80 caracteres"}), 400
    
    # Validación de la descripción
    if len(description) > 300:
        return jsonify({"error": "La descripción supera los 300 caracteres"}), 400

    # Validación del nombre del autor (si se proporciona)
    if author_name and len(author_name) > 50:
        return jsonify({"error": "El nombre del autor no puede superar los 50 caracteres"}), 400

    # Validación: debe elegir entre anónimo o proporcionar nombre
    if not anonymous and not author_name:
        return jsonify({"error": "Debe proporcionar un nombre o marcar la pregunta como anónima"}), 400

    # Determinar el autor según las opciones
    if anonymous:
        author = "Anónimo"
    else:
        author = author_name  # Ya validamos que existe si no es anónimo

    # Crear el objeto con un ID
    question = {
        "id": len(questions) + 1,
        "title": title,
        "description": description,
        "author": author,
    }
    
    # Agregar la pregunta
    questions.append(question)
    save_data()  
    # Retornar la pregunta
    return jsonify(question), 201

@app.route("/questions", methods=["GET"])
def list_questions():
    """    
    Endpoint que retorna las preguntas ordenadas de la más recientes a la más antigua.
    
    Returns:
        tuple: Una tupla con la respuesta JSON y el código HTTP.
        
        En caso positivo:
            list: Lista de diccionarios con:
                - id (int): Identificador
                - title (str): Título 
                - description (str): Descripción 
                - author (str): "Anónimo" o "Usuario"
    
    Note:
        Las preguntas se retornan en orden LIFO (Last In, First Out).
    
    """
    # Retornar lista de preguntas en orden LIFO
    return jsonify(list(reversed(questions)))

answers = {}  # { question_id: [ {id, text, votes}, ... ] }

@app.route("/questions/<int:qid>/answers", methods=["POST"])
def create_answer(qid):
    data = request.json
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "La respuesta no puede estar vacía"}), 400

    # Crear estructura de respuestas si no existe
    if qid not in answers:
        answers[qid] = []

    answer = {
        "id": len(answers[qid]) + 1,
        "text": text,
        "votes": 0
    }
    answers[qid].append(answer)

    save_data()  
    return jsonify(answer), 201


@app.route("/questions/<int:qid>/answers", methods=["GET"])
def list_answers(qid):
    return jsonify(answers.get(qid, [])), 200


@app.route("/questions/<int:qid>/answers/<int:aid>/vote", methods=["POST"])
def vote_answer(qid, aid):
    data = request.json
    change = data.get("change", 0)

    if qid not in answers:
        return jsonify({"error": "Pregunta no encontrada"}), 404

    for answer in answers[qid]:
        if answer["id"] == aid:
            answer["votes"] += change
            save_data()
            return jsonify(answer), 200

    return jsonify({"error": "Respuesta no encontrada"}), 404


def save_data():
    with open(file, "w", encoding="utf-8") as f:
        json.dump({"questions": questions, "answers": answers}, f, ensure_ascii=False, indent=2)

def load_data():
    global questions, answers
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            questions = data.get("questions", [])   
            answers = {int(k): v for k, v in data.get("answers", {}).items()}

            

load_data()

if __name__ == "__main__":
    """
    Punto de entrada.
    """
    app.run(debug=True)
