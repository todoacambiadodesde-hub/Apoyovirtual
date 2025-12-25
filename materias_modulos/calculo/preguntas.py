import random 
from sympy import symbols, diff, limit, latex, simplify, sin, cos, tan, log, sqrt 

x = symbols('x') 

def crear_expresion_compleja(n_terminos=None):
    """Genera polinomios dinámicos con potencias variadas y fracciones ocasionales (10%)."""
    if n_terminos is None:
        n_terminos = random.choice([2, 3])
    
    terminos = []
    # Pool de grados para asegurar diversidad: constantes, lineales y potencias altas
    grados_posibles = [0, 1, 2, 3, 4, 7] 
    random.shuffle(grados_posibles)
    
    for i in range(n_terminos):
        a = random.randint(2, 8)
        signo = random.choice([1, -1])
        grado = grados_posibles[i]
        
        if grado == 0: terminos.append(signo * a)
        elif grado == 1: terminos.append(signo * a * x)
        else: terminos.append(signo * a * x**grado)
    
    # Capacidad de fracciones internas (4/x) limitada al 10%
    if random.random() < 0.10:
        b = random.randint(2, 9)
        terminos.append(random.choice([1, -1]) * (b/x))
        
    return sum(terminos)

def generar_pregunta_por_tipo(tipo):
    """Genera el ejercicio según el tipo exacto solicitado por la cuota."""
    
    if tipo == 'limite':
        # Subtipos de límites para asegurar variedad (incluyendo división compleja)
        sub = random.random()
        if sub < 0.10: # Límite con radical (1 de cada 10 límites aprox)
            a = random.randint(2, 9)
            f = (sqrt(x + a) - sqrt(a)) / x
            enunciado = f"Calcule el límite con radical: $$\\lim_{{x \\to 0}} {latex(f)}$$"
            resultado = limit(f, x, 0)
        else: # Límites de división (3x^2-5x+7)/(3x^2-5) o al infinito
            num, den = crear_expresion_compleja(), crear_expresion_compleja()
            punto = random.choice([0, 1, 'oo'])
            txt_punto = 'x \\to \\infty' if punto == 'oo' else f'x \\to {punto}'
            enunciado = f"Determine el valor del límite: $$\\lim_{{{txt_punto}}} \\frac{{{latex(num)}}}{{{latex(den)}}}$$"
            resultado = limit(num/den, x, punto if punto != 'oo' else 'oo')

    elif tipo == 'derivada':
        variante = random.random()
        if variante < 0.70: # Cociente complejo (lo que más pediste)
            f = crear_expresion_compleja() / crear_expresion_compleja()
            enunciado = f"Halle la derivada de la función: $$f(x) = {latex(f)}$$"
        elif variante < 0.85: # Trigonométrica
            f = sin(random.randint(2, 5)*x**2 - random.randint(1, 4)*x)
            enunciado = f"Derive la expresión trigonométrica: $$f(x) = {latex(f)}$$"
        else: # Potencia compuesta
            f = ((x + random.randint(1, 2))**random.randint(2, 6)) / (random.randint(2, 5)*x + 3)
            enunciado = f"Aplique reglas de derivación para: $$f(x) = {latex(f)}$$"
        resultado = diff(f, x)

    else: # TANGENTE (Fijo 2 de 20)
        num = crear_expresion_compleja(n_terminos=2)
        den = crear_expresion_compleja(n_terminos=2)
        f = num / den
        x0 = random.choice([0, 1])
        try:
            m = diff(f, x).subs(x, x0)
            y0 = f.subs(x, x0)
            if m.is_infinite or y0.is_infinite: return generar_pregunta_por_tipo('tangente')
            recta = simplify(m*(x - x0) + y0)
            enunciado = f"Encuentre la recta tangente a $$f(x) = {latex(f)}$$ en el punto $$x = {x0}$$."
            resultado = recta
        except:
            return generar_pregunta_por_tipo('tangente')

    # Limpieza de formato para salida humana
    res_str = str(simplify(resultado)).replace('**', '^').replace('oo', '∞')
    for i in range(30, 1, -1):
        res_str = res_str.replace(f"{i}*x", f"{i}x")
    res_str = res_str.replace("*", "")
    
    return {"e": enunciado, "r": res_str}

def obtener_bloque_examen_fijo():
    """Genera exactamente 9 límites, 9 derivadas y 2 tangentes."""
    lista_tipos = (['limite'] * 9) + (['derivada'] * 9) + (['tangente'] * 2)
    random.shuffle(lista_tipos) # Mezclamos el orden para que no salgan todos los límites juntos
    
    bloque_final = []
    for tipo in lista_tipos:
        bloque_final.append(generar_pregunta_por_tipo(tipo))
    return bloque_final

# Esta es la lista que tu programa principal consumirá
LISTA_PREGUNTAS = obtener_bloque_examen_fijo()
