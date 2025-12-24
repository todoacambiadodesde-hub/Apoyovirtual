import os
import importlib
import random
import re  # Necesario para la reparación de sintaxis
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sympy import sympify, simplify

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta_aqui'

# --- CONFIGURACIÓN DE BASE DE DATOS ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    es_exacta = db.Column(db.Boolean, default=False)

class Pregunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enunciado = db.Column(db.Text, nullable=False)
    respuesta_correcta = db.Column(db.String(200), nullable=False)
    opcion_a = db.Column(db.String(200), nullable=True)
    opcion_b = db.Column(db.String(200), nullable=True)
    opcion_c = db.Column(db.String(200), nullable=True)
    opcion_d = db.Column(db.String(200), nullable=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)


def normalizar_nombre(nombre):
    reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', '(': '', ')': ''}
    n = nombre.lower()
    for k, v in reemplazos.items():
        n = n.replace(k, v)
    return n.replace(" ", "_")

def procesar_respuesta_usuario(texto):
    """Limpia la respuesta, repara multiplicaciones y traduce potencias."""
    if not texto: return "0"
    
    # 1. Limpieza básica y minúsculas
    res = str(texto).lower().replace(' ', '')
    
    # 2. Traducir símbolos visuales a lenguaje SymPy
    res = res.replace('^', '**').replace('∞', 'oo').replace('infinito', 'oo')
    
    # 3. REPARACIÓN DE MULTIPLICACIÓN INVISIBLE (Ej: 8x -> 8*x)
    # Número seguido de letra o paréntesis: 8x -> 8*x, 8( -> 8*(
    res = re.sub(r'(\d)([a-z\(])', r'\1*\2', res)
    # Paréntesis seguido de letra, número o paréntesis: )x -> )*x, )( -> )*(
    res = re.sub(r'(\))([a-z\d\(])', r'\1*\2', res)
    # Letra 'x' seguida de una función: xcos -> x*cos
    res = re.sub(r'([x])([a-z\(])', r'\1*\2', res)
    
    return res

# --- RUTAS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    nombre = request.form.get('nombre')
    if nombre:
        nuevo_usuario = Usuario(nombre=nombre)
        db.session.add(nuevo_usuario)
        db.session.commit()
        session['usuario_nombre'] = nombre
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_nombre' not in session:
        return redirect(url_for('index'))
    materias = Materia.query.all()
    return render_template('dashboard.html', nombre=session['usuario_nombre'], materias=materias)

@app.route('/examen/<int:materia_id>')
def examen(materia_id):
    if 'usuario_nombre' not in session:
        return redirect(url_for('index'))
    
    materia = Materia.query.get_or_404(materia_id)
    nombre_folder = normalizar_nombre(materia.nombre)
    
    try:
        modulo_path = f'materias_modulos.{nombre_folder}.preguntas'
        modulo = importlib.import_module(modulo_path)
        importlib.reload(modulo)
        
        if hasattr(modulo, 'obtener_20_preguntas'):
            preguntas_data = modulo.obtener_20_preguntas()
        else:
            preguntas_data = modulo.LISTA_PREGUNTAS
        
        Pregunta.query.filter_by(materia_id=materia.id).delete()
        for p in preguntas_data:
            nueva = Pregunta(
                enunciado=p['e'], 
                respuesta_correcta=p['r'],
                opcion_a=p.get('a'), 
                opcion_b=p.get('b'),
                opcion_c=p.get('c'), 
                opcion_d=p.get('d'),
                materia_id=materia.id
            )
            db.session.add(nueva)
        db.session.commit()

    except Exception as e:
        print(f"Error cargando el módulo de {materia.nombre}: {e}")

    preguntas_db = Pregunta.query.filter_by(materia_id=materia.id).all()
    if not preguntas_db:
        return f"<h1>Error: No hay preguntas cargadas para {materia.nombre}</h1>"

    pregunta = random.choice(preguntas_db)
    return render_template('examen.html', materia=materia, pregunta=pregunta, es_exacta=materia.es_exacta)

@app.route('/verificar', methods=['POST'])
def verificar():
    data = request.json
    pregunta = Pregunta.query.get(data['id'])
    materia = Materia.query.get(pregunta.materia_id)
    
    # Procesamos la respuesta del usuario para corregir su sintaxis automáticamente
    user_ans = procesar_respuesta_usuario(data.get('respuesta', ''))
    
    if materia.es_exacta:
        try:
            correcta_db = procesar_respuesta_usuario(pregunta.respuesta_correcta)
            # SymPy compara si la diferencia es cero para aceptar variantes matemáticas
            if simplify(sympify(user_ans) - sympify(correcta_db)) == 0:
                return jsonify({"status": "ok", "msg": "¡Correcto! ✅"})
        except Exception:
            # Mensaje educativo para errores de formato
            return jsonify({
                "status": "error", 
                "msg": "Formato no reconocido. Asegúrate de cerrar todos los paréntesis y usar funciones como cos(x) o log(x)."
            })
    else:
        if user_ans.strip().lower() == pregunta.respuesta_correcta.strip().lower():
            return jsonify({"status": "ok", "msg": "¡Correcto! ✅"})
    
    return jsonify({"status": "error", "msg": f"Incorrecto. Era: {pregunta.respuesta_correcta}"})

@app.route('/finalizar', methods=['POST'])
def finalizar():
    if 'usuario_nombre' not in session:
        return jsonify({"redirect": url_for('index')})
    
    data = request.json
    historial = data.get('respuestas', [])
    
    resumen_detalle = []
    aciertos = 0
    nombre_materia = "Examen"

    for item in historial:
        pregunta_db = Pregunta.query.get(item['id'])
        if not pregunta_db: continue
            
        materia = Materia.query.get(pregunta_db.materia_id)
        nombre_materia = materia.nombre
        user_ans_raw = str(item['respuesta']).strip()
        correct_ans_raw = str(pregunta_db.respuesta_correcta).strip()
        es_correcta = False

        if materia.es_exacta:
            try:
                u_proc = procesar_respuesta_usuario(user_ans_raw)
                c_proc = procesar_respuesta_usuario(correct_ans_raw)
                if simplify(sympify(u_proc) - sympify(c_proc)) == 0:
                    es_correcta = True
            except:
                if user_ans_raw.lower() == correct_ans_raw.lower():
                    es_correcta = True
        else:
            if user_ans_raw.lower() == correct_ans_raw.lower():
                es_correcta = True

        if es_correcta: aciertos += 1

        resumen_detalle.append({
            "enunciado": pregunta_db.enunciado,
            "tu_respuesta": user_ans_raw,
            "correcta": correct_ans_raw,
            "es_correcta": es_correcta
        })

    session['resumen_examen'] = {
        "materia": nombre_materia,
        "aciertos": aciertos,
        "total": len(historial),
        "detalle": resumen_detalle
    }

    return jsonify({"redirect": url_for('ver_resultados')})

@app.route('/resultados')
def ver_resultados():
    if 'usuario_nombre' not in session or 'resumen_examen' not in session:
        return redirect(url_for('dashboard'))
    resultado = session.get('resumen_examen')
    return render_template('resultados.html', r=resultado)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        materias_nombres = [
            ('Cálculo', True), ('Física', True), ('Física para Ingenierías', True),
            ('Temas selectos de Matemáticas', True), ('Temas selectos de Química', True),
            ('Bioquímica', False), ('Biología Celular', False), ('Microbiología', False),
            ('Filosofía (Prob. del conocimiento)', False), ('Psicología', False),
            ('Economía', False), ('Lengua Extranjera', False), ('Intr. al Derecho', False),
            ('Intr. a las Cs. Sociales', False), ('Procesos Económicos', False)
        ]

        if not Materia.query.first():
            for nom, exa in materias_nombres:
                m = Materia(nombre=nom, es_exacta=exa)
                db.session.add(m)
            db.session.commit()

        base_modulos = os.path.join(basedir, 'materias_modulos')
        if not os.path.exists(base_modulos):
            os.makedirs(base_modulos)
            open(os.path.join(base_modulos, '__init__.py'), 'a').close()

        for nom, _ in materias_nombres:
            folder = normalizar_nombre(nom)
            ruta_folder = os.path.join(base_modulos, folder)
            if not os.path.exists(ruta_folder):
                os.makedirs(ruta_folder)
                open(os.path.join(ruta_folder, '__init__.py'), 'a').close()
                with open(os.path.join(ruta_folder, 'preguntas.py'), 'w') as f:
                    f.write('LISTA_PREGUNTAS = [{"e": "Pregunta de prueba", "r": "0"}]')

      port = int(os.environ.get("PORT", 5000))
      app.run(host='0.0.0.0', port=port)
