"""
P1-Backend - API REST/Flask

Aplicación Flask que implementa una API REST para un foro de preguntas y respuestas.

Endpoints disponibles:
- POST /questions: Crear nueva pregunta
- GET /questions: Listar todas las preguntas
- POST /questions/<id>/answers: Crear respuesta a una pregunta
- GET /questions/<id>/answers: Listar respuestas de una pregunta
- POST /questions/<id>/answers/<id>/vote: Votar por una respuesta

Autor: etnicst, steve-quezada, diego-sc96-crypto

Fecha: Agosto 2025
Versión: 2.0.0 (Refactorizada)
"""

from flask import Flask
from flask_cors import CORS
from config.config import get_config
from src.routes.questions import questions_bp

def create_app():
    """
    Factory function para crear la aplicación Flask
    """
    # Obtener configuración
    config = get_config()
    
    # Crear aplicación Flask
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app)
    
    # Registrar blueprints
    app.register_blueprint(questions_bp)
    
    # Configuración adicional
    app.config['DEBUG'] = config.DEBUG
    
    return app

# Para Gunicorn
app = create_app()

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación
    """
    # Crear aplicación
    app = create_app()
    config = get_config()
    
    # Ejecutar aplicación
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
