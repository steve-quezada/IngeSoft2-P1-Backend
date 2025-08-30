"""
Script para probar que la aplicación refactorizada funciona correctamente
"""
import requests
import json
import time
import sys
import os

# Agregar el directorio padre al path para importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from threading import Thread

def test_api():
    """Prueba los endpoints de la API"""
    base_url = "http://127.0.0.1:5000"
    
    # Esperar a que el servidor esté listo
    time.sleep(2)
    
    try:
        # Prueba 1: Crear una pregunta
        print(" Probando creación de pregunta...")
        question_data = {
            "title": "¿Funciona la refactorización?",
            "description": "Prueba del código refactorizado",
            "anonymous": False,
            "author_name": "Desarrollador"
        }
        
        response = requests.post(f"{base_url}/questions", json=question_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("Pregunta creada exitosamente")
        
        # Prueba 2: Listar preguntas
        print("\n Probando listado de preguntas...")
        response = requests.get(f"{base_url}/questions")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("Listado de preguntas exitoso")
        
        # Prueba 3: Crear respuesta
        print("\n Probando creación de respuesta...")
        answer_data = {
            "text": "¡Sí, la refactorización funciona perfectamente!"
        }
        
        response = requests.post(f"{base_url}/questions/1/answers", json=answer_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("Respuesta creada exitosamente")
        
        print("\n ¡Todas las pruebas pasaron exitosamente!")
        
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    print("Iniciando pruebas de la aplicación refactorizada...\n")
    
    # Crear y ejecutar la aplicación en un hilo separado
    app = create_app()
    
    def run_app():
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    
    server_thread = Thread(target=run_app)
    server_thread.daemon = True
    server_thread.start()
    
    # Ejecutar pruebas
    test_api()
