from django import template
from datetime import datetime
import calendar

register = template.Library()

# Diccionarios para traducir días y meses al español
DIAS_SEMANA = {
    'Monday': 'lunes',
    'Tuesday': 'martes', 
    'Wednesday': 'miércoles',
    'Thursday': 'jueves',
    'Friday': 'viernes',
    'Saturday': 'sábado',
    'Sunday': 'domingo'
}

MESES = {
    'January': 'enero',
    'February': 'febrero',
    'March': 'marzo',
    'April': 'abril',
    'May': 'mayo',
    'June': 'junio',
    'July': 'julio',
    'August': 'agosto',
    'September': 'septiembre',
    'October': 'octubre',
    'November': 'noviembre',
    'December': 'diciembre'
}

@register.filter
def fecha_espanol(fecha):
    """
    Convierte una fecha al formato en español: 'lunes, 1 de enero de 2024'
    """
    if not fecha:
        return ''
    
    try:
        # Si es string, convertir a datetime
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
        
        # Obtener componentes de la fecha
        dia_semana_ingles = fecha.strftime('%A')
        dia = fecha.day
        mes_ingles = fecha.strftime('%B')
        año = fecha.year
        
        # Traducir al español
        dia_semana = DIAS_SEMANA.get(dia_semana_ingles, dia_semana_ingles)
        mes = MESES.get(mes_ingles, mes_ingles)
        
        return f"{dia_semana}, {dia} de {mes} de {año}"
        
    except Exception as e:
        # Si hay error, devolver formato simple
        return fecha.strftime('%d/%m/%Y') if fecha else ''

@register.filter
def fecha_corta_espanol(fecha):
    """
    Convierte una fecha al formato corto en español: '1 de enero de 2024'
    """
    if not fecha:
        return ''
    
    try:
        # Si es string, convertir a datetime
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
        
        # Obtener componentes de la fecha
        dia = fecha.day
        mes_ingles = fecha.strftime('%B')
        año = fecha.year
        
        # Traducir al español
        mes = MESES.get(mes_ingles, mes_ingles)
        
        return f"{dia} de {mes} de {año}"
        
    except Exception as e:
        # Si hay error, devolver formato simple
        return fecha.strftime('%d/%m/%Y') if fecha else ''