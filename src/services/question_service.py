"""
Servicio para manejar la lógica de negocio de preguntas y respuestas
Versión PostgreSQL - usa base de datos en lugar de JSON
"""
from typing import List, Optional
from datetime import datetime
from config.database import get_db_cursor, init_db_pool
from src.models.question import Question, QuestionRequest, Answer, AnswerRequest
from src.utils.validators import QuestionValidator, AnswerValidator, ValidationError
import logging

logger = logging.getLogger(__name__)


class QuestionService:
    """Servicio para manejar preguntas y respuestas con PostgreSQL"""
    
    def __init__(self):
        """Inicializa el servicio y el pool de conexiones"""
        try:
            init_db_pool(min_conn=2, max_conn=10)
            logger.info("QuestionService inicializado con PostgreSQL")
        except Exception as e:
            logger.error(f"Error al inicializar QuestionService: {e}")
            raise
    
    def create_question(self, request: QuestionRequest) -> Question:
        """Crea una nueva pregunta en la base de datos"""
        # Validar datos
        QuestionValidator.validate_question_data(
            title=request.title,
            description=request.description,
            anonymous=request.anonymous,
            author_name=request.author_name
        )
        
        # Insertar en la base de datos
        query = """
            INSERT INTO questions (title, description, author)
            VALUES (%s, %s, %s)
            RETURNING id, title, description, author, created_at
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (
                    request.title.strip(),
                    request.description.strip(),
                    request.get_author()
                ))
                
                row = cursor.fetchone()
                
                question = Question(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    author=row[3]
                )
                
                logger.info(f"Pregunta creada: ID={question.id}")
                return question
                
        except Exception as e:
            logger.error(f"Error al crear pregunta: {e}")
            raise ValidationError(f"Error al crear pregunta: {str(e)}")
    
    def get_questions(self) -> List[Question]:
        """Obtiene todas las preguntas ordenadas por más reciente"""
        query = """
            SELECT id, title, description, author, created_at
            FROM questions
            ORDER BY created_at DESC
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                
                questions = [
                    Question(
                        id=row[0],
                        title=row[1],
                        description=row[2],
                        author=row[3]
                    )
                    for row in rows
                ]
                
                logger.info(f"{len(questions)} preguntas obtenidas")
                return questions
                
        except Exception as e:
            logger.error(f"Error al obtener preguntas: {e}")
            raise ValidationError(f"Error al obtener preguntas: {str(e)}")
    
    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Obtiene una pregunta por su ID"""
        query = """
            SELECT id, title, description, author, created_at
            FROM questions
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (question_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                question = Question(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    author=row[3]
                )
                
                return question
                
        except Exception as e:
            logger.error(f"Error al obtener pregunta {question_id}: {e}")
            raise ValidationError(f"Error al obtener pregunta: {str(e)}")
    
    def create_answer(self, question_id: int, request: AnswerRequest) -> Answer:
        """Crea una nueva respuesta para una pregunta"""
        # Validar que la pregunta existe
        if not self.get_question_by_id(question_id):
            raise ValidationError("Pregunta no encontrada")
        
        # Validar el texto de la respuesta
        AnswerValidator.validate_text(request.text)
        
        # Insertar en la base de datos
        query = """
            INSERT INTO answers (question_id, text, votes)
            VALUES (%s, %s, 0)
            RETURNING id, text, votes, created_at
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (question_id, request.text.strip()))
                row = cursor.fetchone()
                
                answer = Answer(
                    id=row[0],
                    text=row[1],
                    votes=row[2]
                )
                
                logger.info(f"Respuesta creada: ID={answer.id} para pregunta {question_id}")
                return answer
                
        except Exception as e:
            logger.error(f"Error al crear respuesta: {e}")
            raise ValidationError(f"Error al crear respuesta: {str(e)}")
    
    def get_answers(self, question_id: int) -> List[Answer]:
        """Obtiene todas las respuestas de una pregunta ordenadas por votos"""
        query = """
            SELECT id, text, votes, created_at
            FROM answers
            WHERE question_id = %s
            ORDER BY votes DESC, created_at ASC
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (question_id,))
                rows = cursor.fetchall()
                
                answers = [
                    Answer(
                        id=row[0],
                        text=row[1],
                        votes=row[2]
                    )
                    for row in rows
                ]
                
                logger.info(f"{len(answers)} respuestas obtenidas para pregunta {question_id}")
                return answers
                
        except Exception as e:
            logger.error(f"Error al obtener respuestas: {e}")
            raise ValidationError(f"Error al obtener respuestas: {str(e)}")
    
    def vote_answer(self, question_id: int, answer_id: int, change: int) -> Answer:
        """Vota por una respuesta (incrementa o decrementa votos)"""
        # Validar el cambio de votos
        AnswerValidator.validate_vote_change(change)
        
        # Actualizar votos en la base de datos
        query = """
            UPDATE answers
            SET votes = votes + %s
            WHERE id = %s AND question_id = %s
            RETURNING id, text, votes
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (change, answer_id, question_id))
                row = cursor.fetchone()
                
                if not row:
                    raise ValidationError("Respuesta no encontrada")
                
                answer = Answer(
                    id=row[0],
                    text=row[1],
                    votes=row[2]
                )
                
                logger.info(f"Voto registrado: Answer ID={answer_id}, cambio={change}, total={answer.votes}")
                return answer
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error al votar respuesta: {e}")
            raise ValidationError(f"Error al votar respuesta: {str(e)}")
    
    def get_statistics(self) -> dict:
        """Obtiene estadísticas de la plataforma"""
        query = """
            SELECT 
                (SELECT COUNT(*) FROM questions) as total_questions,
                (SELECT COUNT(*) FROM answers) as total_answers,
                (SELECT COALESCE(SUM(votes), 0) FROM answers) as total_votes
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
                return {
                    "total_questions": row[0],
                    "total_answers": row[1],
                    "total_votes": row[2]
                }
                
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {
                "total_questions": 0,
                "total_answers": 0,
                "total_votes": 0
            }
