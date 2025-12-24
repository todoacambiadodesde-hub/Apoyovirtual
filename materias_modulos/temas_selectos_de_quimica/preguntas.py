import random

# Banco de ejercicios de Química (Exactas)
# Nota: No llevan llaves 'a, b, c, d' para que el HTML muestre el cuadro de texto.
BANCO_QUIMICA = [
    {
        "e": "Calcule la masa molar del Ácido Sulfúrico ($H_2SO_4$). <br>Datos: H=1, S=32, O=16. <br><b>Indique solo el número en g/mol:</b>",
        "r": "98"
    },
    {
        "e": "En la reacción $N_2 + 3H_2 \\rightarrow 2NH_3$, ¿cuántos moles de $H_2$ se necesitan para producir 10 moles de $NH_3$?",
        "r": "15"
    },
    {
        "e": "Un gas ocupa 2L a una presión de 3 atm. Si el volumen aumenta a 6L a temperatura constante, ¿cuál será la nueva presión en atm? (Ley de Boyle)",
        "r": "1"
    },
    {
        "e": "¿Cuál es el pH de una solución cuya concentración de iones hidrógeno $[H^+]$ es $1 \\times 10^{-5}$ M?",
        "r": "5"
    },
    {
        "e": "Determine la molaridad (M) de una solución que contiene 2 moles de soluto en 4 litros de disolución.",
        "r": "0.5"
    }
]

def obtener_20_preguntas():
    """
    Retorna 20 preguntas. 
    Como el banco es pequeño, usamos random.choices para completar las 20 
    hasta que agregues más ejercicios manuales.
    """
    return random.choices(BANCO_QUIMICA, k=20)

# Variable necesaria para la carga dinámica de tu app.py
LISTA_PREGUNTAS = obtener_20_preguntas()
