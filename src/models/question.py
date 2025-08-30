"""
Modelo para representar una pregunta
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Question:
    """Modelo de datos para una pregunta"""
    id: int
    title: str
    description: str
    author: str
    
    def to_dict(self) -> dict:
        """Convierte la pregunta a diccionario"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "author": self.author
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """Crea una pregunta desde un diccionario"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            author=data["author"]
        )

@dataclass
class QuestionRequest:
    """Modelo para la creación de preguntas"""
    title: str
    description: str = ""
    anonymous: bool = False
    author_name: str = ""
    
    def get_author(self) -> str:
        """Obtiene el nombre del autor según la configuración"""
        if self.anonymous:
            return "Anónimo"
        return self.author_name if self.author_name else "Usuario"

@dataclass
class Answer:
    """Modelo de datos para una respuesta"""
    id: int
    text: str
    votes: int = 0
    
    def to_dict(self) -> dict:
        """Convierte la respuesta a diccionario"""
        return {
            "id": self.id,
            "text": self.text,
            "votes": self.votes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Answer':
        """Crea una respuesta desde un diccionario"""
        return cls(
            id=data["id"],
            text=data["text"],
            votes=data.get("votes", 0)
        )

@dataclass
class AnswerRequest:
    """Modelo para la creación de respuestas"""
    text: str
