"""
Rutas para el manejo de preguntas y respuestas
"""
from flask import Blueprint, request, jsonify
from src.services.question_service import QuestionService
from src.models.question import QuestionRequest, AnswerRequest
from src.utils.validators import ValidationError

# Crear blueprint
questions_bp = Blueprint('questions', __name__)

# Inicializar servicio
question_service = QuestionService()

@questions_bp.route("/health", methods=["GET"])
def health_check():
    """
    Endpoint de health check para monitoreo del contenedor
    """
    return jsonify({"status": "healthy", "service": "backend"}), 200

@questions_bp.route("/questions", methods=["POST"])
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
        JSON: Datos de la pregunta creada o mensaje de error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos JSON requeridos"}), 400
        
        # Crear objeto de solicitud
        question_request = QuestionRequest(
            title=data.get("title", ""),
            description=data.get("description", ""),
            anonymous=data.get("anonymous", False),
            author_name=data.get("author_name", "")
        )
        
        # Crear pregunta a través del servicio
        question = question_service.create_question(question_request)
        
        return jsonify(question.to_dict()), 201
    
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500

@questions_bp.route("/questions", methods=["GET"])
def list_questions():
    """    
    Endpoint que retorna las preguntas ordenadas de la más recientes a la más antigua.
    
    Returns:
        JSON: Lista de preguntas ordenadas por fecha de creación (LIFO)
    """
    try:
        questions = question_service.get_questions()
        return jsonify([q.to_dict() for q in questions]), 200
    
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500

@questions_bp.route("/questions/<int:question_id>/answers", methods=["POST"])
def create_answer(question_id):
    """
    Endpoint para crear una respuesta a una pregunta específica.
    
    Args:
        question_id (int): ID de la pregunta
        
    Request Body (JSON):
        text (str): Texto de la respuesta
        
    Returns:
        JSON: Datos de la respuesta creada o mensaje de error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos JSON requeridos"}), 400
        
        # Crear objeto de solicitud
        answer_request = AnswerRequest(
            text=data.get("text", "")
        )
        
        # Crear respuesta a través del servicio
        answer = question_service.create_answer(question_id, answer_request)
        
        return jsonify(answer.to_dict()), 201
    
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500

@questions_bp.route("/questions/<int:question_id>/answers", methods=["GET"])
def list_answers(question_id):
    """
    Endpoint que retorna todas las respuestas de una pregunta específica.
    
    Args:
        question_id (int): ID de la pregunta
        
    Returns:
        JSON: Lista de respuestas de la pregunta
    """
    try:
        answers = question_service.get_answers(question_id)
        return jsonify([a.to_dict() for a in answers]), 200
    
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500

@questions_bp.route("/questions/<int:question_id>/answers/<int:answer_id>/vote", methods=["POST"])
def vote_answer(question_id, answer_id):
    """
    Endpoint para votar por una respuesta específica.
    
    Args:
        question_id (int): ID de la pregunta
        answer_id (int): ID de la respuesta
        
    Request Body (JSON):
        change (int): Cambio en los votos (-1, 0, 1)
        
    Returns:
        JSON: Datos de la respuesta actualizada o mensaje de error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos JSON requeridos"}), 400
        
        change = data.get("change", 0)
        
        # Votar a través del servicio
        answer = question_service.vote_answer(question_id, answer_id, change)
        
        return jsonify(answer.to_dict()), 200
    
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500
