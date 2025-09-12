"""
Configuración de la aplicación Flask
"""
import os

class Config:
    """Configuración base de la aplicación"""
    DEBUG = True
    DATA_FILE = "data.json"
    HOST = "0.0.0.0"  # Permitir conexiones desde cualquier IP en Docker
    PORT = 5000
    
    # Límites de validación
    TITLE_MIN_LENGTH = 5
    TITLE_MAX_LENGTH = 80
    DESCRIPTION_MAX_LENGTH = 300
    AUTHOR_MAX_LENGTH = 50

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    DATA_FILE = "test_data.json"

# Mapeo de configuraciones
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'default')
    return config_map.get(env, DevelopmentConfig)
