"""
Script para generar un informe en formato Markdown o HTML a partir
de los datos JSON del análisis de la encuesta Cisco NetAcad
"""

import json
import os
import sys
import pandas as pd
from datetime import datetime

def cargar_datos():
    """Carga los datos del archivo JSON de resultados"""
    try:
        json_path = 'static/resultados_analisis.json'
        if not os.path.exists(json_path):
            print("❌ Error: El archivo JSON de resultados no existe.")
            print("   Ejecute primero el análisis para generar el archivo JSON.")
            sys.exit(1)
            
        with open(json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        print(f"✅ Datos cargados correctamente del archivo {json_path}")
        return datos
    except Exception as e:
        print(f"❌ Error al cargar los datos: {str(e)}")
        sys.exit(1)

def generar_informe_markdown(datos):
    """Genera un informe en formato Markdown"""
    ahora = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    md = f"""# Informe de Análisis - Encuesta Cisco NetAcad

*Generado automáticamente el {ahora}*

## Resumen Ejecutivo

Este informe presenta los resultados del análisis de la encuesta sobre intereses en cursos de Cisco NetAcad
realizada a estudiantes de la carrera de Computación.

- **Total de respuestas**: {datos['meta']['total_respuestas']}
- **Fecha del análisis**: {datos['meta']['fecha_analisis']}

## Preferencias Generales

### Modalidad Preferida

La modalidad más solicitada es **{datos['resumen']['Modalidad más solicitada']}** con
{datos['resumen']['Número de estudiantes en modalidad preferida']} estudiantes.

| Modalidad | Cantidad | 
|-----------|----------|
"""
    
    # Agregar datos de modalidad
    for modalidad, cantidad in datos['preferencias']['modalidad'].items():
        md += f"| {modalidad} | {cantidad} |\n"
    
    md += """
### Disposición a Participar

| Disposición | Cantidad |
|-------------|----------|
"""

    # Agregar datos de disposición
    for disposicion, cantidad in datos['preferencias']['disposicion'].items():
        md += f"| {disposicion} | {cantidad} |\n"
    
    md += """
### Horarios Preferidos

| Horario | Cantidad |
|---------|----------|
"""

    # Agregar datos de horarios
    for horario, cantidad in list(datos['preferencias']['horarios'].items())[:5]:
        md += f"| {horario} | {cantidad} |\n"
    
    md += """
## Interés por Área Temática

El análisis muestra las siguientes preferencias por área temática:

| Área | Estudiantes Interesados |
|------|-------------------------|
"""

    # Agregar datos de interés por área
    for area, cantidad in datos['interes_por_area'].items():
        md += f"| {area} | {cantidad} |\n"
    
    md += """
## Cursos Más Populares

### Redes y Ciberseguridad

| Curso | Estudiantes Interesados |
|-------|-------------------------|
"""

    # Agregar datos de cursos de redes
    for curso, cantidad in list(datos['cursos_populares']['redes_ciberseguridad'].items())[:5]:
        md += f"| {curso} | {cantidad} |\n"
    
    md += """
### IA y Ciencia de Datos

| Curso | Estudiantes Interesados |
|-------|-------------------------|
"""

    # Agregar datos de cursos de IA
    for curso, cantidad in list(datos['cursos_populares']['ia_ciencia_datos'].items())[:5]:
        md += f"| {curso} | {cantidad} |\n"
    
    md += """
### Programación

| Curso | Estudiantes Interesados |
|-------|-------------------------|
"""

    # Agregar datos de cursos de programación
    for curso, cantidad in list(datos['cursos_populares']['programacion'].items())[:5]:
        md += f"| {curso} | {cantidad} |\n"
    
    md += """
### Hardware y Sistemas Operativos

| Curso | Estudiantes Interesados |
|-------|-------------------------|
"""

    # Agregar datos de cursos de hardware
    for curso, cantidad in list(datos['cursos_populares']['hardware_so'].items())[:5]:
        md += f"| {curso} | {cantidad} |\n"
    
    md += """
## Análisis por Ciclo Académico

### Modalidad Preferida por Ciclo

| Ciclo | Modalidad Preferida |
|-------|---------------------|
"""

    # Agregar datos de modalidad por ciclo
    for ciclo, modalidad in datos['analisis_por_ciclo']['modalidad_preferida'].items():
        md += f"| {ciclo} | {modalidad} |\n"
    
    md += """
## Experiencia Previa en Cisco NetAcad

| Experiencia | Cantidad |
|-------------|----------|
"""

    # Agregar datos de experiencia previa
    for exp, cantidad in datos['experiencia_previa'].items():
        md += f"| {exp} | {cantidad} |\n"
    
    md += """
## Sugerencias y Comentarios

Algunos de los comentarios y sugerencias más relevantes de los estudiantes:

"""

    # Agregar sugerencias (máximo 10)
    for i, sugerencia in enumerate(datos['sugerencias'][:10]):
        if sugerencia and sugerencia.strip() and sugerencia.lower() not in ["ninguna", "ninguno", "no", ""]:
            md += f"- {sugerencia}\n"
    
    md += f"""
## Conclusiones

Basados en el análisis de los datos, se recomienda:

1. Priorizar la modalidad de cursos más solicitada: **{datos['resumen']['Modalidad más solicitada']}**
2. Concentrarse en los cursos de mayor interés en cada área temática
3. Considerar los horarios preferidos por los estudiantes para maximizar la participación
4. Tomar en cuenta las sugerencias de los estudiantes para mejorar la experiencia de aprendizaje

---

*Informe generado automáticamente a partir de los datos de la encuesta el {ahora}*
"""

    # Guardar el archivo Markdown
    output_path = 'static/informe_cisco_netacad.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"✅ Informe Markdown generado exitosamente: {output_path}")
    return output_path

def main():
    """Función principal"""
    print("\n--- GENERANDO INFORME DE RESULTADOS ---\n")
    
    # Cargar datos
    datos = cargar_datos()
    
    # Generar informe Markdown
    md_path = generar_informe_markdown(datos)
    
    print(f"\nInforme generado exitosamente en: {md_path}")
    print("\nPuede convertir este archivo Markdown a otros formatos como PDF o HTML utilizando herramientas como Pandoc.")
    
    print("\n--- PROCESO COMPLETADO ---\n")

if __name__ == "__main__":
    main()
