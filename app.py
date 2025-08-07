# app.py (versión optimizada)

from flask import Flask, render_template, send_file, jsonify
import pandas as pd
import os
import datetime
import json

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

    TABLA_CICLOS_HTML = modalidad_por_ciclo.to_html(classes='table table-striped table-hover', index=False, justify='center')
    TABLA_EXPERIENCIA_HTML = experiencia_counts.to_html(classes='table table-striped table-hover', index=False, justify='center')
    
    # Calcular datos para el resumen
    modalidad_preferida = df['¿Qué modalidad prefiere para tomar estos cursos?'].value_counts()
    experiencia_previa = df['¿Ha tomado anteriormente algún curso en la plataforma Cisco NetAcad?'].value_counts()
    
    # Crear el diccionario resumen que espera el template
    RESUMEN = {
        'Total de respuestas': len(df),
        'Estudiantes con experiencia previa': experiencia_previa.get('Sí', 0),
        'Modalidad más solicitada': modalidad_preferida.index[0] if len(modalidad_preferida) > 0 else 'No disponible',
        'Número de estudiantes en modalidad preferida': modalidad_preferida.iloc[0] if len(modalidad_preferida) > 0 else 0
    }

except FileNotFoundError:
    df = None
    TABLA_CICLOS_HTML = "<p>Error: No se encontró el archivo de datos.</p>"
    TABLA_EXPERIENCIA_HTML = "<p>Error: No se encontró el archivo de datos.</p>"
    RESUMEN = {
        'Total de respuestas': 0,
        'Estudiantes con experiencia previa': 0,
        'Modalidad más solicitada': 'No disponible',
        'Número de estudiantes en modalidad preferida': 0
    }


# --- RUTAS ---
@app.route('/')
def dashboard():
    # Ahora también pasamos el resumen y el tiempo de actualización
    return render_template('index.html', 
                           titulo_pagina="Dashboard de Intereses Cisco NetAcad",
                           tabla_ciclos_html=TABLA_CICLOS_HTML,
                           tabla_experiencia_html=TABLA_EXPERIENCIA_HTML,
                           resumen=RESUMEN,
                           tiempo_actualizacion=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                          )

# Ruta para descargar el archivo JSON con los resultados
@app.route('/download/results')
def download_results():
    try:
        # Comprobar si existe un archivo JSON de resultados
        if os.path.exists('static/resultados_analisis.json'):
            return send_file('static/resultados_analisis.json',
                             mimetype='application/json',
                             download_name='resultados_cisco_netacad.json',
                             as_attachment=True)
        else:
            # Si no existe, devolver el resumen básico
            return jsonify(RESUMEN)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para ver los resultados JSON en el navegador
@app.route('/api/results')
def api_results():
    try:
        if os.path.exists('static/resultados_analisis.json'):
            with open('static/resultados_analisis.json', 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        else:
            # Si no existe, devolver el resumen básico
            return jsonify({
                "meta": {
                    "fecha_analisis": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_respuestas": RESUMEN['Total de respuestas']
                },
                "resumen": RESUMEN
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)