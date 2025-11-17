"""
Módulo de conexión a base de datos PostgreSQL
Gestiona el pool de conexiones y proporciona funciones auxiliares
"""

import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pool de conexiones
connection_pool = None


def init_db_pool(min_conn=1, max_conn=10):
    """
    Inicializa el pool de conexiones a PostgreSQL
    
    Args:
        min_conn: Número mínimo de conexiones en el pool
        max_conn: Número máximo de conexiones en el pool
    """
    global connection_pool
    
    try:
        database_url = os.getenv('DATABASE_URL', 
                                'postgresql://admin:admin123@localhost:5432/ingesoft2')
        
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            database_url
        )
        
        logger.info(f"Pool de conexiones inicializado: {min_conn}-{max_conn} conexiones")
        return connection_pool
        
    except Exception as e:
        logger.error(f"Error al inicializar pool de conexiones: {e}")
        raise


def close_db_pool():
    """
    Cierra todas las conexiones del pool
    """
    global connection_pool
    
    if connection_pool:
        connection_pool.closeall()
        logger.info("Pool de conexiones cerrado")


@contextmanager
def get_db_connection():
    """
    Context manager para obtener una conexión del pool
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions")
            results = cursor.fetchall()
    """
    global connection_pool
    
    if not connection_pool:
        init_db_pool()
    
    conn = connection_pool.getconn()
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error en transacción de BD: {e}")
        raise
    finally:
        connection_pool.putconn(conn)


@contextmanager
def get_db_cursor(commit=True):
    """
    Context manager para obtener un cursor de base de datos
    
    Args:
        commit: Si True, hace commit automáticamente. Si False, solo rollback en error.
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM questions")
            results = cursor.fetchall()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en cursor de BD: {e}")
            raise
        finally:
            cursor.close()


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Ejecuta una query SQL y retorna resultados
    
    Args:
        query: Query SQL a ejecutar
        params: Parámetros para la query (tupla o dict)
        fetch_one: Si True, retorna solo un registro
        fetch_all: Si True, retorna todos los registros
        
    Returns:
        Resultados de la query o None
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            return cursor.rowcount


def dict_cursor_factory(cursor, row):
    """
    Factory para convertir resultados a diccionarios
    
    Args:
        cursor: Cursor de psycopg2
        row: Fila de resultados
        
    Returns:
        Diccionario con nombres de columnas como keys
    """
    if row is None:
        return None
    
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


@contextmanager
def get_dict_cursor():
    """
    Context manager para cursor que retorna diccionarios
    
    Usage:
        with get_dict_cursor() as cursor:
            cursor.execute("SELECT * FROM questions")
            results = cursor.fetchall()  # Lista de diccionarios
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Modificar row_factory para retornar diccionarios
        original_row_factory = cursor.row_factory if hasattr(cursor, 'row_factory') else None
        
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en dict_cursor: {e}")
            raise
        finally:
            cursor.close()


def test_connection():
    """
    Prueba la conexión a la base de datos
    
    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            logger.info(f"Conexión a PostgreSQL exitosa: {result}")
            return True
    except Exception as e:
        logger.error(f"Error al conectar con PostgreSQL: {e}")
        return False


# Inicializar pool al importar el módulo (opcional)
# init_db_pool()
