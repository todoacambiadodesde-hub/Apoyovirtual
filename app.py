import os
import importlib
import random
import re
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
    if not texto: return "0"
    res = str(texto).lower().replace(' ', '')
    res = res.replace('^', '**').replace('∞', 'oo').replace('infinito', 'oo')
    res = re.sub(r'(\d)([a-z\(])', r'\1*\2', res)
    res = re.sub(r'(\))([a-z\d\(])', r'\1*\2', res)
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
    if 'usuario_nombre' not in session: return redirect(url_for('index'))
    
    materia = Materia.query.get_or_404(materia_id)
    nombre_folder = normalizar_nombre(materia.nombre)
    
    try:
        modulo_path = f'materias_modulos.{nombre_folder}.preguntas'
        modulo = importlib.import_module(modulo_path)
        if os.environ.get('RENDER') is None: importlib.reload(modulo)
        
        preguntas_data = modulo.obtener_20_preguntas() if hasattr(modulo, 'obtener_20_preguntas') else modulo.LISTA_PREGUNTAS
        
        Pregunta.query.filter_by(materia_id=materia.id).delete()
        for p in preguntas_data:
            enunciado_final = p['e']
            
            # --- LÓGICA DE MULTIHUECOS ---
            # Si el JSON dice que es multihueco, agregamos los espacios [[_]] al final
            if p.get('tipo') == 'multihueco':
                # Contamos cuántas respuestas hay separadas por coma
                respuestas_lista = str(p['r']).split(',')
                # Agregamos un cuadrito [[_]] por cada respuesta para que el HTML los renderice
                espacios = " ".join(["[[_]]" for _ in respuestas_lista])
                enunciado_final += f"<br><br>{espacios}"
            
            nueva = Pregunta(
                enunciado=enunciado_final,
                respuesta_correcta=str(p['r']),
                opcion_a=p.get('a'), opcion_b=p.get('b'),
                opcion_c=p.get('c'), opcion_d=p.get('d'),
                materia_id=materia.id
            )
            db.session.add(nueva)
        db.session.commit()
    except Exception as e:
        print(f"Error cargando materia {materia.nombre}: {e}")

    preguntas_db = Pregunta.query.filter_by(materia_id=materia.id).all()
    pregunta = random.choice(preguntas_db)
    return render_template('examen.html', materia=materia, pregunta=pregunta)

@app.route('/verificar', methods=['POST'])
def verificar():
    data = request.json
    pregunta = Pregunta.query.get(data['id'])
    materia = Materia.query.get(pregunta.materia_id)
    user_ans = data.get('respuesta', '').strip()
    correcta = pregunta.respuesta_correcta.strip()

    # 1. OPCIÓN MÚLTIPLE (Prioridad)
    if pregunta.opcion_a:
        if user_ans.upper() == correcta.upper():
            return jsonify({"status": "ok", "msg": "¡Correcto! ✅"})
    
    # 2. CIENCIAS EXACTAS (Cálculo / Física / Química Multihueco)
    elif materia.es_exacta:
        try:
            if "," in correcta:
                u_parts = [procesar_respuesta_usuario(x) for x in user_ans.split(",")]
                c_parts = [procesar_respuesta_usuario(x) for x in correcta.split(",")]
                if len(u_parts) == len(c_parts) and all(simplify(sympify(u) - sympify(c)) == 0 for u, c in zip(u_parts, c_parts)):
                    return jsonify({"status": "ok", "msg": "¡Todo correcto! ✅"})
            else:
                u = procesar_respuesta_usuario(user_ans)
                c = procesar_respuesta_usuario(correcta)
                if simplify(sympify(u) - sympify(c)) == 0:
                    return jsonify({"status": "ok", "msg": "¡Correcto! ✅"})
        except:
            if user_ans.lower() == correcta.lower():
                return jsonify({"status": "ok", "msg": "¡Correcto! ✅"})

    # 3. HUMANIDADES / OTROS
    else:
        if user_ans.lower() == correcta.lower():
            return jsonify({"status": "ok", "msg": "¡Correcto! ✅"})

    return jsonify({"status": "error", "msg": f"Incorrecto. Era: {correcta}"})

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
        if pregunta_db.opcion_a:
            es_correcta = (user_ans_raw.upper() == correct_ans_raw.upper())
        elif materia.es_exacta:
            try:
                u_proc, c_proc = procesar_respuesta_usuario(user_ans_raw), procesar_respuesta_usuario(correct_ans_raw)
                es_correcta = (simplify(sympify(u_proc) - sympify(c_proc)) == 0)
            except:
                es_correcta = (user_ans_raw.lower() == correct_ans_raw.lower())
        else:
            es_correcta = (user_ans_raw.lower() == correct_ans_raw.lower())

        if es_correcta: aciertos += 1
        resumen_detalle.append({"enunciado": pregunta_db.enunciado, "tu_respuesta": user_ans_raw, "correcta": correct_ans_raw, "es_correcta": es_correcta})

    session['resumen_examen'] = {"materia": nombre_materia, "aciertos": aciertos, "total": len(historial), "detalle": resumen_detalle}
    return jsonify({"redirect": url_for('ver_resultados')})

@app.route('/resultados')
def ver_resultados():
    if 'usuario_nombre' not in session or 'resumen_examen' not in session:
        return redirect(url_for('dashboard'))
    return render_template('resultados.html', r=session.get('resumen_examen'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        materias_nombres = [
            ('Cálculo', True), ('Física', True), ('Estadistica', True), ('Física para Ingenierías', True),
            ('Calculo integral e diferencial', True), ('Temas selectos de Química', True),
            ('Bioquímica', False), ('Biología Celular', False), ('Microbiología', False),
            ('Filosofía (Prob. del conocimiento)', False), ('Psicología', False),
            ('Economía', False), ('Lengua Extranjera', False), ('Intr. al Derecho', False),
            ('Intr. a las Cs. Sociales', False), ('Procesos Económicos', False)
        ]
        if not Materia.query.first():
            materias_nombres = [
                ('Cálculo', True), ('Estadistica', True), ('Física', True), ('Física para Ingenierías', True),
                ('Calculo integral e diferencial', True), ('Temas selectos de Química', True),
                ('Bioquímica', False), ('Biología Celular', False), ('Microbiología', False),
                ('Filosofía (Prob. del conocimiento)', False), ('Psicología', False),
                ('Economía', False), ('Lengua Extranjera', False), ('Intr. al Derecho', False),
                ('Intr. a las Cs. Sociales', False), ('Procesos Económicos', False)
            ]
            for nom, exa in materias_nombres:
                db.session.add(Materia(nombre=nom, es_exacta=exa))
            db.session.commit()

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
