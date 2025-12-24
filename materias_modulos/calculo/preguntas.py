import random
from sympy import symbols, diff, limit, latex, simplify, sin, cos, tan, log, sqrt

x = symbols('x')

def generar_una_pregunta():
    """Genera variantes basadas en las fotos: cocientes trigonométricos y racionales complejos."""
    
    # Probabilidad de raíz (5%) o tipos normales (95%)
    es_pregunta_raiz = random.random() < 0.05
    tipo = 'limite_raiz' if es_pregunta_raiz else random.choice(['limite', 'derivada', 'tangente'])
    
    a = random.randint(2, 6)
    b = random.randint(1, 4)

    if tipo == 'limite':
        # VARIANTES DE LÍMITES (Basados en el nivel de las fotos)
        subtipo = random.choice(['trig', 'racional', 'infinito'])
        
        if subtipo == 'trig':
            # Límite tipo: (sen x + cos x) / cos x cuando x -> 0
            f = (sin(x) + cos(x)) / cos(x)
            enunciado = f"Calcule el límite trigonométrico: $$\\lim_{{x \\to 0}} {latex(f)}$$"
            resultado = limit(f, x, 0)
        
        elif subtipo == 'racional':
            # Límite tipo: (x^2 - 9) / (x + 4) cuando x -> a
            punto = random.randint(-3, 3)
            num = x**2 - (a**2)
            den = x + b
            enunciado = f"Determine el valor del límite: $$\\lim_{{x \\to {punto}}} \\frac{{{latex(num)}}}{{{latex(den)}}}$$"
            resultado = limit(num/den, x, punto)
            
        else: # infinito
            # Límite al infinito de un cociente complejo
            f = (a*x**2 + b) / (b*x**2 - a*x + 8)
            enunciado = f"Calcule el límite al infinito: $$\\lim_{{x \\to \\infty}} {latex(f)}$$"
            resultado = limit(f, x, 'oo')

    elif tipo == 'limite_raiz':
        # Variante de raíz (1 de cada 20)
        enunciado = f"Calcule el límite con radical: $$\\lim_{{x \\to 0}} \\frac{{\\sqrt{{x + {a}}} - \\sqrt{{{a}}}}}{{x}}$$"
        resultado = limit((sqrt(x+a) - sqrt(a))/x, x, 0)

    elif tipo == 'derivada':
        # VARIANTES EXTRAÍDAS DE TUS FOTOS:
        variante = random.choice([1, 2, 3, 4])
        
        if variante == 1: # sen(2x^2 - 3x)
            f = sin(a*x**2 - b*x)
            enunciado = f"Encontrar la derivada de la función: $$f(x) = {latex(f)}$$"
        elif variante == 2: # (x^2 - 9) / (x + 4)
            f = (x**2 - 9) / (x + 4)
            enunciado = f"Halle la derivada $f'(x)$ del cociente: $$f(x) = {latex(f)}$$"
        elif variante == 3: # (sen x + cos x) / cos x
            f = (sin(x) + cos(x)) / cos(x)
            enunciado = f"Derive la expresión trigonométrica: $$f(x) = {latex(f)}$$"
        else: # ((x+1)^2) / (3x + 4)
            f = ((x + 1)**2) / (a*x + b)
            enunciado = f"Aplique la regla del cociente y cadena para: $$f(x) = {latex(f)}$$"
        
        resultado = diff(f, x)

    else: # TANGENTE (Basada en el ejercicio 5 de tu foto)
        # f(x) = (x^2 + 3) / (2x^2 - 3x + 8)
        num = x**2 + 3
        den = 2*x**2 - 3*x + 8
        f = num / den
        x0 = 1
        m = diff(f, x).subs(x, x0)
        y0 = f.subs(x, x0)
        recta_derecha = simplify(m*(x - x0) + y0)
        enunciado = f"Encontrar la ecuación de la recta tangente a la curva $$f(x) = {latex(f)}$$ cuando $$x = {x0}$$."
        resultado = recta_derecha

    # Traducción final para el sistema
    res_str = str(resultado).replace('**', '^').replace('oo', '∞')
    return {"e": enunciado, "r": res_str}

def obtener_20_preguntas():
    preguntas = []
    enunciados_vistos = set()
    while len(preguntas) < 20:
        p = generar_una_pregunta()
        if p['e'] not in enunciados_vistos:
            enunciados_vistos.add(p['e'])
            preguntas.append(p)
    return preguntas

LISTA_PREGUNTAS = obtener_20_preguntas()
