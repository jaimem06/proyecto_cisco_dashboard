# analisis.py

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import json
from json import JSONEncoder
from collections import Counter

# Add a custom JSON encoder class to handle NumPy types
class NumpyEncoder(JSONEncoder):
    """ Custom encoder for numpy data types """
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

# --- CONFIGURACIÓN INICIAL ---
# Estilo de los gráficos
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.sans-serif'] = ['Arial', 'sans-serif']

# Colores personalizados (paleta de Cisco)
CISCO_COLORS = ['#049fd9', '#33ab84', '#8bc34a', '#ffc107', '#ff9800', '#ff5722', '#e91e63', '#9c27b0']
sns.set_palette(CISCO_COLORS)

# Crear carpetas para guardar los gráficos si no existen
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# --- CARGA DE DATOS ---
try:
    df = pd.read_csv('respuestas_cisco.csv')
    print("✅ Archivo CSV cargado exitosamente.")
    
    # Validación básica de datos
    if df.empty:
        print("⚠️ Advertencia: El archivo CSV está vacío.")
    elif len(df.columns) < 5:
        print("⚠️ Advertencia: El archivo CSV parece no tener suficientes columnas.")
    else:
        print(f"📊 {len(df)} respuestas encontradas con {len(df.columns)} campos.")
except FileNotFoundError:
    print("❌ Error: El archivo 'respuestas_cisco.csv' no se encontró.")
    exit()
except Exception as e:
    print(f"❌ Error al cargar el CSV: {str(e)}")
    exit()

# --- LIMPIEZA Y PREPARACIÓN ---
# Renombrar columnas para un acceso más fácil
df.rename(columns={
    '¿En qué ciclo se encuentra actualmente?': 'ciclo',
    '¿Ha tomado anteriormente algún curso en la plataforma Cisco NetAcad?': 'experiencia_previa',
    'Redes y ciberseguridad ': 'cursos_redes', # El espacio al final es importante
    'IA y Ciencia de Datos': 'cursos_ia',
    'Programación': 'cursos_programacion',
    'Hardware  y Sistemas Operativos': 'cursos_so',
    '¿Qué modalidad prefiere para tomar estos cursos?': 'modalidad',
    '¿Qué tan dispuesto/a estaría a participar en un curso opcional de este tipo durante el semestre?': 'disposicion',
    '¿Qué días y horarios prefiere para tomar este tipo de cursos presenciales o síncronos?': 'horario'
}, inplace=True)

# Eliminar filas completamente vacías y valores nulos en columnas clave
df = df.dropna(how='all')

# --- FUNCIONES DE ANÁLISIS MEJORADAS ---

def analizar_respuestas_multiples(dataframe, columna, titulo, archivo_salida, max_items=10):
    """
    Toma una columna con strings de valores separados por comas,
    los separa, cuenta las ocurrencias y genera un gráfico de barras horizontal.
    """
    # Verificar si la columna existe
    if columna not in dataframe.columns:
        print(f"❌ Error: La columna '{columna}' no existe en el dataframe.")
        return pd.Series()
    
    # 1. Separar los strings por comas, eliminar espacios, valores vacíos y crear una lista única
    items_series = dataframe[columna].dropna().astype(str)
    all_items = []
    
    for respuesta in items_series:
        # Solo procesar si no es una cadena vacía
        if respuesta and respuesta.strip():
            items = [item.strip() for item in respuesta.split(',') if item.strip()]
            all_items.extend(items)
    
    # 2. Contar la frecuencia de cada item y obtener los más populares
    counter = Counter(all_items)
    conteo = pd.Series(dict(counter.most_common(max_items)))
    
    if conteo.empty:
        print(f"⚠️ Advertencia: No hay datos para analizar en '{columna}'.")
        return pd.Series()
    
    # 3. Ordenar por frecuencia y generar el gráfico horizontal
    plt.figure(figsize=(12, max(7, len(conteo)*0.4)))  # Ajustar altura dinámicamente
    ax = sns.barplot(x=conteo.values, y=conteo.index, palette='viridis', hue=conteo.index, dodge=False, legend=False)
    
    # Añadir valores numéricos a las barras
    for i, v in enumerate(conteo.values):
        ax.text(v + 0.5, i, str(v), va='center')
    
    ax.set_title(titulo, fontsize=16, fontweight='bold')
    ax.set_xlabel('Número de Estudiantes', fontsize=12)
    ax.set_ylabel('Cursos', fontsize=12)
    
    # Mejorar el formato del gráfico
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    # 4. Guardar el gráfico
    ruta_guardado = f'static/images/{archivo_salida}'
    plt.savefig(ruta_guardado, dpi=100, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico generado: {ruta_guardado}")
    
    # 5. Calcular estadísticas adicionales
    total_selecciones = sum(conteo.values)
    promedio = total_selecciones / len(conteo) if len(conteo) > 0 else 0
    
    print(f"   - Total de selecciones: {total_selecciones}")
    print(f"   - Promedio por opción: {promedio:.2f}")
    
    return conteo

def analizar_respuesta_unica(dataframe, columna, titulo, archivo_salida, tipo_grafico='pie'):
    """
    Analiza columnas de respuesta única generando gráficos mejorados.
    """
    # Verificar si la columna existe
    if columna not in dataframe.columns:
        print(f"❌ Error: La columna '{columna}' no existe en el dataframe.")
        return pd.DataFrame()
    
    # Filtrar valores nulos y contar frecuencias
    serie_filtrada = dataframe[columna].dropna()
    if serie_filtrada.empty:
        print(f"⚠️ Advertencia: No hay datos para analizar en '{columna}'.")
        return pd.DataFrame()
    
    conteo = serie_filtrada.value_counts()
    
    plt.figure(figsize=(12, 8))
    
    if tipo_grafico == 'pie':
        # Calcular porcentajes para las etiquetas
        sizes = conteo.values
        total = sum(sizes)
        labels = [f"{item} ({size/total*100:.1f}%)" for item, size in zip(conteo.index, sizes)]
        
        # Crear gráfico de pastel con destacado de la porción más grande
        explode = [0.1 if i == conteo.values.argmax() else 0 for i in range(len(conteo))]
        
        plt.pie(sizes, labels=labels, explode=explode, autopct='%1.1f%%', 
                startangle=140, colors=CISCO_COLORS[:len(conteo)],
                shadow=True, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
        plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')  # Para que el círculo sea un círculo
        
    else:  # Gráfico de barras
        # Fix seaborn warning by using hue parameter correctly
        ax = sns.barplot(x=conteo.index, y=conteo.values, hue=conteo.index, palette=CISCO_COLORS[:len(conteo)], legend=False)
        
        # Añadir valores sobre las barras
        for i, v in enumerate(conteo.values):
            ax.text(i, v + 0.1, str(v), ha='center')
            
        ax.set_title(titulo, fontsize=16, fontweight='bold')
        ax.set_ylabel('Número de Estudiantes', fontsize=12)
        ax.set_xlabel('')
        
        # Rotar etiquetas si son largas
        if max([len(str(x)) for x in conteo.index]) > 10:
            plt.xticks(rotation=30, ha="right")
        
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    
    # Guardar el gráfico
    ruta_guardado = f'static/images/{archivo_salida}'
    plt.savefig(ruta_guardado, dpi=100, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico generado: {ruta_guardado}")
    
    # Convertir a DataFrame con porcentajes
    total = conteo.sum()
    df_resultado = conteo.to_frame(name='Cantidad')
    df_resultado['Porcentaje'] = df_resultado['Cantidad'] / total * 100
    
    return df_resultado

# Función para generar un resumen estadístico
def generar_resumen_estadistico():
    """
    Genera un resumen estadístico de los datos principales y lo guarda como CSV
    """
    # Contar estudiantes por ciclo
    ciclos = df['ciclo'].value_counts().reset_index()
    ciclos.columns = ['Ciclo', 'Cantidad']
    
    # Calcular experiencia previa
    experiencia = df['experiencia_previa'].value_counts().reset_index()
    experiencia.columns = ['Experiencia', 'Cantidad']
    
    # Preferencia de modalidad
    modalidad = df['modalidad'].value_counts().reset_index()
    modalidad.columns = ['Modalidad', 'Cantidad']
    
    # Resumen general
    resumen = {
        'Total de respuestas': len(df),
        'Estudiantes con experiencia previa': experiencia[experiencia['Experiencia'] == 'Sí']['Cantidad'].values[0] if 'Sí' in experiencia['Experiencia'].values else 0,
        'Modalidad más solicitada': modalidad.iloc[0]['Modalidad'],
        'Número de estudiantes en modalidad preferida': modalidad.iloc[0]['Cantidad']
    }
    
    # Guardar como CSV para uso futuro
    pd.DataFrame([resumen]).to_csv('static/resumen_estadistico.csv', index=False)
    
    return resumen

# Función para analizar interés por área
def analizar_interes_por_area():
    """
    Compara el interés en las diferentes áreas temáticas
    """
    # Contar respuestas no vacías en cada columna de cursos
    areas = ['cursos_redes', 'cursos_ia', 'cursos_programacion', 'cursos_so']
    nombres = ['Redes y Ciberseguridad', 'IA y Ciencia de Datos', 'Programación', 'Hardware y SO']
    
    # Contar respuestas no vacías (que indican interés)
    interes = {}
    for area, nombre in zip(areas, nombres):
        interes[nombre] = df[area].notna().sum()
    
    # Crear gráfico
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=list(interes.keys()), y=list(interes.values()), 
                     hue=list(interes.keys()), palette=CISCO_COLORS[:4], legend=False)
    
    # Añadir etiquetas
    for i, v in enumerate(interes.values()):
        ax.text(i, v + 1, str(v), ha='center')
    
    ax.set_title('Interés por Área Temática', fontsize=16, fontweight='bold')
    ax.set_ylabel('Número de Estudiantes Interesados', fontsize=12)
    ax.set_xlabel('')
    plt.tight_layout()
    
    # Guardar
    plt.savefig('static/images/interes_por_area.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    return interes

# Función para analizar disposición por ciclo
def analizar_disposicion_por_ciclo():
    """
    Analiza la disposición a participar según el ciclo académico
    """
    # Crear tabla pivote
    pivot = pd.crosstab(df['ciclo'], df['disposicion'])
    
    # Normalizar por fila para obtener porcentajes
    pivot_norm = pivot.div(pivot.sum(axis=1), axis=0) * 100
    
    # Graficar
    plt.figure(figsize=(12, 8))
    ax = pivot_norm.plot(kind='bar', stacked=True, colormap='viridis')
    
    ax.set_title('Disposición a Participar por Ciclo Académico', fontsize=16, fontweight='bold')
    ax.set_ylabel('Porcentaje (%)', fontsize=12)
    ax.set_xlabel('Ciclo', fontsize=12)
    ax.legend(title='Disposición')
    
    # Guardar
    plt.tight_layout()
    plt.savefig('static/images/disposicion_por_ciclo.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    return pivot

# Función para analizar los cursos más populares por ciclo académico
def analizar_cursos_por_ciclo():
    """
    Analiza los cursos más populares para cada ciclo académico
    y genera un gráfico comparativo.
    """
    print("\nAnalizando cursos más populares por ciclo académico:")
    
    # Definir los ciclos y columnas de cursos
    ciclos = df['ciclo'].unique()
    columnas_cursos = ['cursos_redes', 'cursos_ia', 'cursos_programacion', 'cursos_so']
    
    # Diccionario para almacenar el curso más popular por ciclo
    cursos_por_ciclo = {}
    
    # Para cada ciclo, encontrar el curso más popular entre todas las categorías
    for ciclo in ciclos:
        # Filtrar el dataframe para este ciclo
        df_ciclo = df[df['ciclo'] == ciclo]
        
        # Contar todos los cursos mencionados en todas las categorías
        all_cursos = []
        
        for col in columnas_cursos:
            items_series = df_ciclo[col].dropna().astype(str)
            
            for respuesta in items_series:
                if respuesta and respuesta.strip():
                    items = [item.strip() for item in respuesta.split(',') if item.strip()]
                    all_cursos.extend(items)
        
        # Si no hay cursos para este ciclo, continuar con el siguiente
        if not all_cursos:
            continue
        
        # Encontrar el curso más popular
        counter = Counter(all_cursos)
        curso_mas_popular, conteo = counter.most_common(1)[0]
        
        # Almacenar el resultado
        cursos_por_ciclo[ciclo] = {
            'curso': curso_mas_popular,
            'conteo': conteo
        }
    
    # Preparar datos para graficar
    ciclos_ord = sorted(cursos_por_ciclo.keys(), 
                        key=lambda x: (
                            # Primero los ciclos numéricos
                            0 if any(c.isdigit() for c in str(x)) else 1,
                            # Ordenar primero por número
                            int(''.join(c for c in str(x) if c.isdigit() or c == '.').split('.')[0]) 
                            if any(c.isdigit() for c in str(x)) else 999,
                            # Luego por texto
                            str(x)
                        ))
    
    ciclos_graf = [str(c) for c in ciclos_ord]
    cursos_graf = [cursos_por_ciclo[c]['curso'] for c in ciclos_ord]
    conteos_graf = [cursos_por_ciclo[c]['conteo'] for c in ciclos_ord]
    
    # Crear gráfico
    plt.figure(figsize=(14, 8))
    
    # Usar barras horizontales para nombres de cursos largos
    ax = plt.barh(ciclos_graf, conteos_graf, color=CISCO_COLORS[:len(ciclos_graf)])
    
    # Agregar etiquetas con el nombre del curso en cada barra
    for i, (curso, conteo) in enumerate(zip(cursos_graf, conteos_graf)):
        # Acortar nombre del curso si es muy largo
        curso_texto = curso if len(curso) < 30 else curso[:27] + "..."
        plt.text(
            conteo + 0.3,  # Posición x (ligeramente a la derecha de la barra)
            i,             # Posición y (índice de la barra)
            curso_texto,   # Texto a mostrar
            va='center',   # Alineación vertical centrada
            fontsize=9,    # Tamaño de fuente
            fontweight='bold'
        )
    
    plt.title('Curso Más Popular por Ciclo Académico', fontsize=16, fontweight='bold')
    plt.xlabel('Número de Estudiantes', fontsize=12)
    plt.ylabel('Ciclo Académico', fontsize=12)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    # Guardar gráfico
    ruta_guardado = 'static/images/cursos_por_ciclo.png'
    plt.savefig(ruta_guardado, dpi=100, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico generado: {ruta_guardado}")
    
    return cursos_por_ciclo

# Función para exportar resultados a JSON
def exportar_resultados_json():
    """
    Exporta los resultados del análisis a un archivo JSON estructurado
    para facilitar la generación de informes.
    """
    print("\nExportando resultados a JSON...")
    
    # Análisis de cursos por ciclo
    cursos_por_ciclo = analizar_cursos_por_ciclo()
    
    # Crear estructura del JSON
    resultados = {
        "meta": {
            "fecha_analisis": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "total_respuestas": int(len(df))  # Convert to regular Python int
        },
        "resumen": {k: (int(v) if isinstance(v, (np.integer, np.int64)) else v) 
                    for k, v in generar_resumen_estadistico().items()},
        "preferencias": {
            "modalidad": {str(k): int(v) for k, v in df['modalidad'].value_counts().to_dict().items()},
            "disposicion": {str(k): int(v) for k, v in df['disposicion'].value_counts().to_dict().items()},
            "horarios": analizar_horarios_preferidos()
        },
        "interes_por_area": analizar_interes_por_area_json(),
        "cursos_populares": {
            "redes_ciberseguridad": obtener_top_cursos('cursos_redes', 10),
            "ia_ciencia_datos": obtener_top_cursos('cursos_ia', 10),
            "programacion": obtener_top_cursos('cursos_programacion', 10),
            "hardware_so": obtener_top_cursos('cursos_so', 10)
        },
        "analisis_por_ciclo": {
            "modalidad_preferida": {str(k): str(v) for k, v in df.groupby('ciclo')['modalidad'].agg(lambda x: x.value_counts().index[0]).to_dict().items()},
            "disposicion": obtener_disposicion_por_ciclo_json(),
            "curso_mas_popular": {str(k): {"curso": v["curso"], "conteo": int(v["conteo"])} for k, v in cursos_por_ciclo.items()}
        },
        "experiencia_previa": {str(k): int(v) for k, v in df['experiencia_previa'].value_counts().to_dict().items()},
        "sugerencias": obtener_sugerencias()
    }
    
    # Guardar el JSON usando el encoder personalizado
    ruta_json = 'static/resultados_analisis.json'
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4, cls=NumpyEncoder)
    
    print(f"✅ Resultados exportados a: {ruta_json}")
    return resultados

# Funciones auxiliares para el JSON

def analizar_horarios_preferidos():
    """Obtiene los horarios preferidos en formato de diccionario"""
    horarios = df['horario'].dropna().astype(str)
    all_horarios = []
    
    for respuesta in horarios:
        if respuesta and respuesta.strip():
            items = [item.strip() for item in respuesta.split(',') if item.strip()]
            all_horarios.extend(items)
    
    # Convert Counter results to regular Python types
    return {str(k): int(v) for k, v in Counter(all_horarios).most_common()}

def analizar_interes_por_area_json():
    """Análisis de interés por área en formato para JSON"""
    areas = ['cursos_redes', 'cursos_ia', 'cursos_programacion', 'cursos_so']
    nombres = ['Redes y Ciberseguridad', 'IA y Ciencia de Datos', 'Programación', 'Hardware y SO']
    
    interes = {}
    for area, nombre in zip(areas, nombres):
        # Convert NumPy int64 to regular Python int
        interes[nombre] = int(df[area].notna().sum())
    
    return interes

def obtener_top_cursos(columna, n=10):
    """Obtiene los top n cursos más populares de una columna"""
    if columna not in df.columns:
        return {}
    
    items_series = df[columna].dropna().astype(str)
    all_items = []
    
    for respuesta in items_series:
        if respuesta and respuesta.strip():
            items = [item.strip() for item in respuesta.split(',') if item.strip()]
            all_items.extend(items)
    
    counter = Counter(all_items)
    # Convert to regular Python types for JSON serialization
    return {str(k): int(v) for k, v in counter.most_common(n)}

def obtener_disposicion_por_ciclo_json():
    """Obtiene la disposición por ciclo en formato JSON"""
    pivot = pd.crosstab(df['ciclo'], df['disposicion'])
    result = {}
    
    for ciclo in pivot.index:
        # Convert all values to regular Python types
        result[str(ciclo)] = {str(k): int(v) for k, v in pivot.loc[ciclo].to_dict().items()}
    
    return result

def obtener_sugerencias():
    """Extrae las sugerencias de los estudiantes"""
    if '¿Qué sugerencias tiene para estos cursos o qué otros temas le gustaría que se incluyan?' in df.columns:
        col = '¿Qué sugerencias tiene para estos cursos o qué otros temas le gustaría que se incluyan?'
        return df[col].dropna().tolist()
    return []

# Función principal que ejecuta todos los análisis
def generar_todos_los_analisis():
    print("\n--- INICIANDO ANÁLISIS ---")
    
    # 1. Cursos más populares por área
    print("\nAnalizando preferencias de cursos por área:")
    analizar_respuestas_multiples(df, 'cursos_redes', 'Top Cursos de Redes y Ciberseguridad', 'cursos_redes.png')
    analizar_respuestas_multiples(df, 'cursos_ia', 'Top Cursos de IA y Ciencia de Datos', 'cursos_ia.png')
    analizar_respuestas_multiples(df, 'cursos_programacion', 'Top Cursos de Programación', 'cursos_programacion.png')
    analizar_respuestas_multiples(df, 'cursos_so', 'Top Cursos de Hardware y SO', 'cursos_so.png')
    
    # 2. Análisis general
    print("\nAnalizando preferencias generales:")
    analizar_respuesta_unica(df, 'modalidad', 'Modalidad Preferida por los Estudiantes', 'modalidad.png', tipo_grafico='bar')
    analizar_respuesta_unica(df, 'disposicion', 'Disposición a Participar en Cursos', 'disposicion.png')
    analizar_respuestas_multiples(df, 'horario', 'Horarios de Preferencia', 'horarios.png')
    analizar_respuesta_unica(df, 'experiencia_previa', 'Experiencia Previa en Cisco NetAcad', 'experiencia.png')
    
    # 3. Análisis por ciclo
    print("\nAnalizando datos por segmentos:")
    ciclos_interes = df.groupby('ciclo')['modalidad'].agg(lambda x: x.value_counts().index[0])
    print("\nModalidad preferida por ciclo:")
    print(ciclos_interes)
    
    # 4. Nuevos análisis
    print("\nGenerando análisis adicionales:")
    analizar_interes_por_area()
    analizar_disposicion_por_ciclo()
    analizar_cursos_por_ciclo()  # Agregar esta línea
    
    # 5. Resumen estadístico
    print("\nGenerando resumen estadístico:")
    resumen = generar_resumen_estadistico()
    for key, value in resumen.items():
        print(f"   - {key}: {value}")
    
    # 6. Exportar resultados a JSON
    print("\nExportando resultados a JSON:")
    exportar_resultados_json()
    
    print("\n--- ANÁLISIS COMPLETADO ---\n")
    return True

# Si ejecutamos este script directamente, generará los gráficos
if __name__ == '__main__':
    generar_todos_los_analisis()