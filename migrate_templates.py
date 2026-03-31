#!/usr/bin/env python3
"""
Script para migrar automáticamente templates de DataTables a Bootstrap Table
Uso: python migrate_templates.py
"""

import os
import re
import glob

# Patrón para encontrar tablas DataTables
DATATABLE_PATTERN = r'<table class="([^"]*)" id="bootstrap-data-table-export">\s*<thead>\s*(.*?)\s*</thead>'

# Template de Bootstrap Table
BOOTSTRAP_TABLE_TEMPLATE = '''<table class="{classes}" 
       id="bootstrap-data-table-export"
       data-search="true"
       data-show-columns="true"
       data-show-export="true"
       data-show-refresh="true"
       data-pagination="true"
       data-page-size="10"
       data-page-list="[10, 25, 50, 100, all]"
       data-locale="es-EC">
    <thead class="thead-light">
        <tr>
{columns}
        </tr>
    </thead>'''

def extract_columns(thead_content):
    """Extrae las columnas del thead y las convierte al formato Bootstrap Table"""
    # Buscar <th> tags
    th_pattern = r'<th(?:[^>]*)>(.*?)</th>'
    columns = re.findall(th_pattern, thead_content, re.IGNORECASE | re.DOTALL)
    
    bootstrap_columns = []
    for i, column in enumerate(columns):
        # Limpiar el contenido de la columna
        column = column.strip()
        field_name = f"campo{i+1}"
        
        # Determinar si es sortable (todas excepto acciones)
        is_sortable = "acciones" not in column.lower() and "acción" not in column.lower()
        sortable_attr = "true" if is_sortable else "false"
        
        bootstrap_column = f'            <th data-field="{field_name}" data-sortable="{sortable_attr}">{column}</th>'
        bootstrap_columns.append(bootstrap_column)
    
    return '\n'.join(bootstrap_columns)

def migrate_template(file_path):
    """Migra un template individual"""
    print(f"Procesando: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el patrón DataTables
    match = re.search(DATATABLE_PATTERN, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        classes = match.group(1)
        thead_content = match.group(2)
        
        # Extraer columnas
        columns = extract_columns(thead_content)
        
        # Crear el nuevo HTML de Bootstrap Table
        new_table = BOOTSTRAP_TABLE_TEMPLATE.format(
            classes=classes,
            columns=columns
        )
        
        # Reemplazar en el contenido
        old_pattern = match.group(0)
        new_content = content.replace(old_pattern, new_table)
        
        # Escribir archivo de respaldo
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Escribir archivo actualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ Migrado exitosamente (backup en {backup_path})")
        return True
    else:
        print(f"  ⚠️  No se encontró patrón DataTables")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando migración de templates DataTables → Bootstrap Table")
    
    # Buscar todos los templates HTML en el proyecto
    templates_path = "**/*templates/**/*.html"
    template_files = glob.glob(templates_path, recursive=True)
    
    migrated = 0
    total = 0
    
    for file_path in template_files:
        # Verificar si el archivo contiene bootstrap-data-table-export
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'bootstrap-data-table-export' in content:
            total += 1
            if migrate_template(file_path):
                migrated += 1
    
    print(f"\n📊 Resumen:")
    print(f"Templates procesados: {total}")
    print(f"Templates migrados: {migrated}")
    print(f"Templates sin cambios: {total - migrated}")
    
    if migrated > 0:
        print(f"\n✅ Migración completada!")
        print(f"Nota: Se crearon archivos .backup para restaurar si es necesario")
    else:
        print("\n⚠️  No se migraron templates. Verifica los patrones de búsqueda.")

if __name__ == "__main__":
    main()