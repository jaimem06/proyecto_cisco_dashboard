# app.py (versión optimizada)

from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# --- CARGA DE DATOS SOLO PARA LAS TABLAS ---
# Hacemos esto fuera de la ruta para que se cargue una sola vez al iniciar la app.
try:
    df = pd.read_csv('respuestas_cisco.csv')
    
    # Pre-calculamos las tablas que necesita el HTML
    modalidad_por_ciclo = df.groupby('¿En qué ciclo se encuentra actualmente?')['¿Qué modalidad prefiere para tomar estos cursos?'].agg(
        lambda x: x.value_counts().index[0]
    ).reset_index()
    modalidad_por_ciclo.rename(columns={
        '¿En qué ciclo se encuentra actualmente?': 'Ciclo',
        '¿Qué modalidad prefiere para tomar estos cursos?': 'Modalidad Preferida'
    }, inplace=True)
    
    experiencia_counts = df['¿Ha tomado anteriormente algún curso en la plataforma Cisco NetAcad?'].value_counts().to_frame().reset_index()
    experiencia_counts.columns = ['Respuesta', 'Número de Estudiantes']

    TABLA_CICLOS_HTML = modalidad_por_ciclo.to_html(classes='table table-striped', index=False, justify='center')
    TABLA_EXPERIENCIA_HTML = experiencia_counts.to_html(classes='table table-striped', index=False, justify='center')

except FileNotFoundError:
    df = None
    TABLA_CICLOS_HTML = "<p>Error: No se encontró el archivo de datos.</p>"
    TABLA_EXPERIENCIA_HTML = "<p>Error: No se encontró el archivo de datos.</p>"


# --- RUTA PRINCIPAL (DASHBOARD) ---
@app.route('/')
def dashboard():
    # La función ahora es muy simple: solo renderiza el template.
    # Ya no llama a generar_todos_los_analisis().
    return render_template('index.html', 
                           titulo_pagina="Dashboard de Intereses Cisco NetAcad",
                           tabla_ciclos_html=TABLA_CICLOS_HTML,
                           tabla_experiencia_html=TABLA_EXPERIENCIA_HTML
                          )