"""
Servicio para manejar la lógica de negocio de preguntas y respuestas
"""
import json
import os
from typing import List, Optional, Dict, Any
from config.config import get_config
from src.models.question import Question, QuestionRequest, Answer, AnswerRequest
from src.utils.validators import QuestionValidator, AnswerValidator, ValidationError

config = get_config()

class QuestionService:
    """Servicio para manejar preguntas y respuestas"""
    
    def __init__(self):
        self.data_file = config.DATA_FILE
        self.questions: List[Question] = []
        self.answers: Dict[int, List[Answer]] = {}
        self.load_data()
    
    def create_question(self, request: QuestionRequest) -> Question:
        """Crea una nueva pregunta"""
        # Validar datos
        QuestionValidator.validate_question_data(
            title=request.title,
            description=request.description,
            anonymous=request.anonymous,
            author_name=request.author_name
        )
        
        # Crear la pregunta
        question = Question(
            id=self._get_next_question_id(),
            title=request.title.strip(),
            description=request.description.strip(),
            author=request.get_author()
        )
        
        # Guardar
        self.questions.append(question)
        self.save_data()
        
        return question
    
    def get_questions(self) -> List[Question]:
        """Obtiene todas las preguntas ordenadas por más reciente"""
        # Recargar datos para sincronizar con otros workers
        self.load_data()
        return list(reversed(self.questions))
    
    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Obtiene una pregunta por su ID"""
        # Recargar datos para sincronizar con otros workers
        self.load_data()
        for question in self.questions:
            if question.id == question_id:
                return question
        return None
    
    def create_answer(self, question_id: int, request: AnswerRequest) -> Answer:
        """Crea una nueva respuesta para una pregunta"""
        # Recargar datos para sincronizar con otros workers
        self.load_data()
        
        # Validar que la pregunta existe
        if not self.get_question_by_id(question_id):
            raise ValidationError("Pregunta no encontrada")
        
        # Validar el texto de la respuesta
        AnswerValidator.validate_text(request.text)
        
        # Crear estructura de respuestas si no existe
        if question_id not in self.answers:
            self.answers[question_id] = []
        
        # Crear la respuesta
        answer = Answer(
            id=self._get_next_answer_id(question_id),
            text=request.text.strip(),
            votes=0
        )
        
        # Guardar
        self.answers[question_id].append(answer)
        self.save_data()
        
        return answer
    
    def get_answers(self, question_id: int) -> List[Answer]:
        """Obtiene todas las respuestas de una pregunta"""
        # Recargar datos para sincronizar con otros workers
        self.load_data()
        return self.answers.get(question_id, [])
    
    def vote_answer(self, question_id: int, answer_id: int, change: int) -> Answer:
        """Vota por una respuesta"""
        # Validar el cambio de votos
        AnswerValidator.validate_vote_change(change)
        
        # Verificar que la pregunta existe
        if question_id not in self.answers:
            raise ValidationError("Pregunta no encontrada")
        
        # Buscar la respuesta
        for answer in self.answers[question_id]:
            if answer.id == answer_id:
                answer.votes += change
                self.save_data()
                return answer
        
        raise ValidationError("Respuesta no encontrada")
    
    def _get_next_question_id(self) -> int:
        """Obtiene el siguiente ID para una pregunta"""
        if not self.questions:
            return 1
        return max(q.id for q in self.questions) + 1
    
    def _get_next_answer_id(self, question_id: int) -> int:
        """Obtiene el siguiente ID para una respuesta"""
        if question_id not in self.answers or not self.answers[question_id]:
            return 1
        return max(a.id for a in self.answers[question_id]) + 1
    
    def save_data(self) -> None:
        """Guarda los datos en el archivo JSON"""
        data = {
            "questions": [q.to_dict() for q in self.questions],
            "answers": {
                str(qid): [a.to_dict() for a in answers]
                for qid, answers in self.answers.items()
            }
        }
        
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_data(self) -> None:
        """Carga los datos desde el archivo JSON"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Cargar preguntas
            self.questions = [
                Question.from_dict(q_data)
                for q_data in data.get("questions", [])
            ]
            
            # Cargar respuestas
            self.answers = {}
            answers_data = data.get("answers", {})
            for qid_str, answers_list in answers_data.items():
                qid = int(qid_str)
                self.answers[qid] = [
                    Answer.from_dict(a_data)
                    for a_data in answers_list
                ]
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error al cargar datos: {e}")
            self.questions = []
            self.answers = {}
