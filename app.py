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

# Configuración Flask
app = Flask(__name__)

# Almacenamiento para las preguntas
questions = []

@app.route("/questions", methods=["POST"])
def create_question():
    """
    Endpoint para crear preguntas con título, descripción y privacidad.
    
    Request Body (JSON):
        title (str): Título. (Debe tener entre 5 y 80 caracteres)
        description (str, opcional): Descripción. (Máximo 300 caracteres)
        anonymous (bool, opcional): La pregunta debe publicarse en anónimo. (por defecto: False)

    Returns:
        tuple: Una tupla con la respuesta JSON y el código HTTP.
        
        En caso positivo:
            dict: Diccionario con los datos:
                - id (int): Identificador 
                - title (str): Título
                - description (str): Descripción
                - author (str): "Anónimo" o "Usuario"
        
        En caso negativo:
            dict: Diccionario con mensaje de error:
                - error (str): Descripción del error
    """
    # Obtener datos del cuerpo de JSON
    data = request.json
    title = data.get("title", "")
    description = data.get("description", "")
    anonymous = data.get("anonymous", False)

    # Validación del título
    if not (5 <= len(title) <= 80):
        return jsonify({"error": "El título debe tener entre 5 y 80 caracteres"}), 400
    
    # Validación de la descripción
    if len(description) > 300:
        return jsonify({"error": "La descripción supera los 300 caracteres"}), 400

    # Crear el objeto con un ID
    question = {
        "id": len(questions) + 1,
        "title": title,
        "description": description,
        "author": "Anónimo" if anonymous else "Usuario",
    }
    
    # Agregar la pregunta
    questions.append(question)
    
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

if __name__ == "__main__":
    """
    Punto de entrada.
    """
    app.run(debug=True)
