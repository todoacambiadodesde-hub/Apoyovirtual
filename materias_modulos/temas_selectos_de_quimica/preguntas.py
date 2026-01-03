import json
import os
import random

def cargar_desde_json():
    # Buscamos la carpeta donde vive este archivo preguntas.py
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_json = os.path.join(directorio_actual, 'preguntasquimica.json')
    
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return [{"e": f"Error de lectura JSON: {e}", "r": "0", "id": "ERR"}]
    
    # Si no existe, lanza este error que viste en tu captura
    return [{"e": "Error: preguntasquimica.json no encontrado en la carpeta", "r": "0", "id": "ERR"}]

def obtener_20_preguntas():
    todas = cargar_desde_json()
    # Si hay un error, no intentamos hacer sample para no romper la app
    if "Error" in todas[0]['e']:
        return todas
    return random.sample(todas, min(len(todas), 20))

# Mantenemos esto para que tu esqueleto original no falle al importar
LISTA_PREGUNTAS = cargar_desde_json()
