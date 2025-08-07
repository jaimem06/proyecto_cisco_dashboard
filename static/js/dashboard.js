/**
 * Dashboard.js - Funciones para manejo de datos JSON y visualización adicional
 */

// Función para cargar los datos JSON y mostrarlos en formato legible
function cargarDatosJSON() {
    fetch('/api/results')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar los datos JSON');
            }
            return response.json();
        })
        .then(data => {
            // Mostrar datos en formato legible
            mostrarDatosFormateados(data);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('json-viewer').innerHTML = 
                `<div class="alert alert-danger">Error al cargar los datos: ${error.message}</div>`;
        });
}

// Función para mostrar los datos en formato legible
function mostrarDatosFormateados(data) {
    const container = document.getElementById('json-viewer');
    if (!container) return;
    
    // Limpiar contenedor
    container.innerHTML = '';
    
    // Crear elementos para las secciones principales
    const secciones = [
        { titulo: 'Información General', clave: 'meta', icono: 'info-circle' },
        { titulo: 'Resumen Estadístico', clave: 'resumen', icono: 'chart-pie' },
        { titulo: 'Preferencias', clave: 'preferencias', icono: 'sliders-h' },
        { titulo: 'Interés por Área', clave: 'interes_por_area', icono: 'project-diagram' },
        { titulo: 'Cursos Populares', clave: 'cursos_populares', icono: 'star' },
        { titulo: 'Análisis por Ciclo', clave: 'analisis_por_ciclo', icono: 'users' }
    ];
    
    // Crear tabs para navegar entre secciones
    const tabsNav = document.createElement('ul');
    tabsNav.className = 'nav nav-tabs mb-3';
    
    const tabContent = document.createElement('div');
    tabContent.className = 'tab-content';
    
    // Crear cada tab y su contenido
    secciones.forEach((seccion, index) => {
        // Crear tab
        const tabItem = document.createElement('li');
        tabItem.className = 'nav-item';
        
        const tabLink = document.createElement('a');
        tabLink.className = `nav-link ${index === 0 ? 'active' : ''}`;
        tabLink.href = `#tab-${seccion.clave}`;
        tabLink.setAttribute('data-bs-toggle', 'tab');
        tabLink.innerHTML = `<i class="fas fa-${seccion.icono} me-2"></i>${seccion.titulo}`;
        
        tabItem.appendChild(tabLink);
        tabsNav.appendChild(tabItem);
        
        // Crear contenido del tab
        const tabPane = document.createElement('div');
        tabPane.className = `tab-pane fade ${index === 0 ? 'show active' : ''}`;
        tabPane.id = `tab-${seccion.clave}`;
        
        // Formatear los datos según la sección
        let contenido = '';
        
        if (seccion.clave === 'meta') {
            contenido = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Metadatos del Análisis</h5>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Fecha: ${data.meta.fecha_analisis}</li>
                            <li class="list-group-item">Versión: ${data.meta.version}</li>
                            <li class="list-group-item">Total de respuestas: ${data.meta.total_respuestas}</li>
                        </ul>
                    </div>
                </div>
            `;
        } else if (seccion.clave === 'resumen') {
            contenido = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Resumen</h5>
                        <ul class="list-group list-group-flush">
                            ${Object.entries(data.resumen).map(([k, v]) => 
                                `<li class="list-group-item">${k}: ${v}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        } else if (seccion.clave === 'preferencias') {
            contenido = `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">Modalidad</h5>
                        <ul class="list-group list-group-flush">
                            ${Object.entries(data.preferencias.modalidad).map(([k, v]) => 
                                `<li class="list-group-item d-flex justify-content-between align-items-center">
                                    ${k}
                                    <span class="badge bg-primary rounded-pill">${v}</span>
                                </li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">Disposición</h5>
                        <ul class="list-group list-group-flush">
                            ${Object.entries(data.preferencias.disposicion).map(([k, v]) => 
                                `<li class="list-group-item d-flex justify-content-between align-items-center">
                                    ${k}
                                    <span class="badge bg-success rounded-pill">${v}</span>
                                </li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        } else if (seccion.clave === 'interes_por_area') {
            contenido = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Interés por Área</h5>
                        <ul class="list-group list-group-flush">
                            ${Object.entries(data.interes_por_area).map(([k, v]) => 
                                `<li class="list-group-item d-flex justify-content-between align-items-center">
                                    ${k}
                                    <span class="badge bg-info rounded-pill">${v}</span>
                                </li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        } else if (seccion.clave === 'cursos_populares') {
            contenido = `
                <div class="accordion" id="accordionCursos">
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#collapseRedes">
                                Redes y Ciberseguridad
                            </button>
                        </h2>
                        <div id="collapseRedes" class="accordion-collapse collapse show" 
                             data-bs-parent="#accordionCursos">
                            <div class="accordion-body">
                                <ul class="list-group">
                                    ${Object.entries(data.cursos_populares.redes_ciberseguridad).map(([k, v]) => 
                                        `<li class="list-group-item d-flex justify-content-between align-items-center">
                                            ${k}
                                            <span class="badge bg-primary rounded-pill">${v}</span>
                                        </li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Más secciones de acordeón para otras áreas -->
                </div>
            `;
        } else if (seccion.clave === 'analisis_por_ciclo') {
            contenido = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Modalidad Preferida por Ciclo</h5>
                        <ul class="list-group list-group-flush">
                            ${Object.entries(data.analisis_por_ciclo.modalidad_preferida).map(([k, v]) => 
                                `<li class="list-group-item d-flex justify-content-between align-items-center">
                                    Ciclo ${k}
                                    <span class="badge bg-warning text-dark">${v}</span>
                                </li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }
        
        tabPane.innerHTML = contenido;
        tabContent.appendChild(tabPane);
    });
    
    // Agregar tabs y contenido al container
    container.appendChild(tabsNav);
    container.appendChild(tabContent);
}

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Si existe el contenedor para visualizar JSON, cargar los datos
    if (document.getElementById('json-viewer')) {
        cargarDatosJSON();
    }
});
