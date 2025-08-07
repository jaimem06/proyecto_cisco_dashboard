# app.py
from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import os
import json

# Importamos nuestras funciones de análisis
from analisis import (
    generar_todos_los_analisis, 
    df, 
    analizar_respuesta_unica,
    generar_resumen_estadistico
)

app = Flask(__name__)

# Función para cargar el resumen estadístico
def cargar_resumen():
    if os.path.exists('static/resumen_estadistico.csv'):
        return pd.read_csv('static/resumen_estadistico.csv').iloc[0].to_dict()
    return generar_resumen_estadistico()

# --- RUTAS ---
@app.route('/')
def dashboard():
    # Ejecutamos el análisis para asegurarnos de que los gráficos estén actualizados
    generar_todos_los_analisis()

    # --- PREPARAMOS DATOS ADICIONALES PARA MOSTRAR EN TABLAS ---
    
    # Tabla de modalidad por ciclo
    modalidad_por_ciclo = df.groupby('ciclo')['modalidad'].agg(
        lambda x: x.value_counts().index[0]
    ).reset_index()
    modalidad_por_ciclo.rename(columns={'modalidad': 'Modalidad Preferida'}, inplace=True)
    
    # Tabla de experiencia previa
    tabla_experiencia = analizar_respuesta_unica(df, 'experiencia_previa', 'Experiencia Previa', 'experiencia.png')
    
    # Tabla de disposición
    tabla_disposicion = analizar_respuesta_unica(df, 'disposicion', 'Disposición a Participar', 'disposicion.png')
    
    # Resumen estadístico
    resumen = cargar_resumen()
    
    # Conteo por ciclo para gráficos
    conteo_por_ciclo = df['ciclo'].value_counts().reset_index()
    conteo_por_ciclo.columns = ['Ciclo', 'Cantidad']
    conteo_por_ciclo_json = conteo_por_ciclo.to_json(orient='records')

    # Pasamos los datos y nombres de archivos al template HTML
    return render_template('index.html', 
                          titulo_pagina="Intereses Cisco NetAcad",
                          tabla_ciclos_html=modalidad_por_ciclo.to_html(classes='table table-striped table-hover', index=False, justify='center'),
                          tabla_experiencia_html=tabla_experiencia.to_html(classes='table table-striped table-hover', justify='center'),
                          tabla_disposicion_html=tabla_disposicion.to_html(classes='table table-striped table-hover', justify='center'),
                          resumen=resumen,
                          conteo_por_ciclo=conteo_por_ciclo_json,
                          tiempo_actualizacion=pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S")
                         )

# Ruta para estadísticas en formato JSON (para posible uso con AJAX)
@app.route('/api/estadisticas')
def api_estadisticas():
    resumen = cargar_resumen()
    return jsonify(resumen)

# Ruta para descargar el archivo JSON con los resultados
@app.route('/download/results')
def download_results():
    try:
        # Verificar si el archivo existe
        if os.path.exists('static/resultados_analisis.json'):
            # Devolver el archivo para descarga
            return send_file('static/resultados_analisis.json',
                             mimetype='application/json',
                             download_name='resultados_cisco_netacad.json',
                             as_attachment=True)
        else:
            # Si no existe, generar el análisis primero
            from analisis import exportar_resultados_json
            exportar_resultados_json()
            return send_file('static/resultados_analisis.json',
                             mimetype='application/json',
                             download_name='resultados_cisco_netacad.json',
                             as_attachment=True)
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
            from analisis import exportar_resultados_json
            resultados = exportar_resultados_json()
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)