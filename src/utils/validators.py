"""
Validadores para los modelos de datos
"""
from typing import Optional, Tuple
from config.config import get_config

config = get_config()

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

class QuestionValidator:
    """Validador para preguntas"""
    
    @staticmethod
    def validate_title(title: str) -> None:
        """Valida el título de una pregunta"""
        if not title or not title.strip():
            raise ValidationError("El título es requerido")
        
        title_length = len(title.strip())
        if not (config.TITLE_MIN_LENGTH <= title_length <= config.TITLE_MAX_LENGTH):
            raise ValidationError(
                f"El título debe tener entre {config.TITLE_MIN_LENGTH} y {config.TITLE_MAX_LENGTH} caracteres"
            )
    
    @staticmethod
    def validate_description(description: str) -> None:
        """Valida la descripción de una pregunta"""
        if description and len(description) > config.DESCRIPTION_MAX_LENGTH:
            raise ValidationError(
                f"La descripción supera los {config.DESCRIPTION_MAX_LENGTH} caracteres"
            )
    
    @staticmethod
    def validate_author(author_name: str, anonymous: bool) -> None:
        """Valida el autor de una pregunta"""
        if author_name and len(author_name) > config.AUTHOR_MAX_LENGTH:
            raise ValidationError(
                f"El nombre del autor no puede superar los {config.AUTHOR_MAX_LENGTH} caracteres"
            )
        
        if not anonymous and not author_name.strip():
            raise ValidationError(
                "Debe proporcionar un nombre o marcar la pregunta como anónima"
            )
    
    @classmethod
    def validate_question_data(cls, title: str, description: str = "", 
                             anonymous: bool = False, author_name: str = "") -> None:
        """Valida todos los datos de una pregunta"""
        cls.validate_title(title)
        cls.validate_description(description)
        cls.validate_author(author_name, anonymous)

class AnswerValidator:
    """Validador para respuestas"""
    
    @staticmethod
    def validate_text(text: str) -> None:
        """Valida el texto de una respuesta"""
        if not text or not text.strip():
            raise ValidationError("La respuesta no puede estar vacía")
    
    @staticmethod
    def validate_vote_change(change: int) -> None:
        """Valida el cambio de votos"""
        if not isinstance(change, int):
            raise ValidationError("El cambio de votos debe ser un número entero")
        
        if abs(change) > 1:
            raise ValidationError("El cambio de votos debe ser -1, 0 o 1")
