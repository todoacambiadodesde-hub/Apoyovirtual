import random

# Definimos una lista grande de preguntas (puedes agregar las que quieras)
BANCO_PREGUNTAS = [
    {
        "e": "¿Quién es considerado el padre del Psicoanálisis?",
        "a": "Sigmund Freud",
        "b": "B.F. Skinner",
        "c": "Jean Piaget",
        "d": "Lev Vygotsky",
        "r": "Sigmund Freud"
    },
    {
        "e": "¿Qué corriente psicológica se enfoca en el estudio del comportamiento observable?",
        "a": "Humanismo",
        "b": "Conductismo",
        "c": "Cognitivismo",
        "d": "Gestalt",
        "r": "Conductismo"
    },
    {
        "e": "Según Piaget, ¿en qué etapa los niños desarrollan la permanencia de objeto?",
        "a": "Preoperacional",
        "b": "Operaciones Concretas",
        "c": "Sensoriomotriz",
        "d": "Operaciones Formales",
        "r": "Sensoriomotriz"
    },
    {
        "e": "¿Cuál de estos conceptos pertenece a la psicología humanista de Abraham Maslow?",
        "a": "Inconsciente colectivo",
        "b": "Condicionamiento operante",
        "c": "Autorrealización",
        "d": "El Ello y el Superyó",
        "r": "Autorrealización"
    },
    {
        "e": "¿Qué experimento es famoso por estudiar la obediencia a la autoridad?",
        "a": "Experimento de la cárcel de Stanford",
        "b": "Experimento de Milgram",
        "c": "Experimento de los perros de Pavlov",
        "d": "Experimento del pequeño Albert",
        "r": "Experimento de Milgram"
    }
]

def obtener_20_preguntas():
    """
    Selecciona 20 preguntas al azar del banco. 
    Si tienes menos de 20, usará random.choices para repetir o 
    simplemente devuelve la lista completa.
    """
    if len(BANCO_PREGUNTAS) >= 20:
        return random.sample(BANCO_PREGUNTAS, 20)
    else:
        # Si aún no llenas las 20, te devuelve las que tengas
        return BANCO_PREGUNTAS

# Dejamos esta variable por compatibilidad con tu lógica de carga
LISTA_PREGUNTAS = obtener_20_preguntas()
