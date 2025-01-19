from django.shortcuts import render

# Create your views here.
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import EstadoOperativoClienteSerializer
from datetime import date, timedelta
from operaciones.models import Datos_operativos, Documentos, Pagares
from clientes import models as ModeloCliente
from cobranzas.models import Cheques_protestados

from django.http import JsonResponse

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def estado_operativo_cliente_api(request, cliente_id):
    valor_linea = 0
    porc_disponible = 0
    dias_ultima_operacion = None
    estado_cliente = ''
    clase_cliente = ''
    nombre_cliente = ''
    color_estado = 1
    cartera = 0
    protestos = 0
    restructuracion = 0

    cliente = ModeloCliente.Datos_generales.objects.filter(id=cliente_id).first()
    if cliente:
        nombre_cliente = cliente.cxcliente.ctnombre

    linea = ModeloCliente.Linea_Factoring.objects.filter(cxcliente=cliente_id).first()
    if linea:
        valor_linea = linea.nvalor
        porc_disponible = linea.porcentaje_disponible()

    operativos = Datos_operativos.objects.filter(cxcliente=cliente_id).first()
    if operativos:
        estado_cliente = operativos.cxestado
        clase_cliente = operativos.cxclase
        if operativos.dultimanegociacion:
            dias_ultima_operacion = (date.today() - operativos.dultimanegociacion) / timedelta(days=1)

    if estado_cliente == 'A':
        estado_cliente = 'Activo'
        color_estado = 5
    elif estado_cliente == 'B':
        estado_cliente = 'Baja'
        color_estado = 2
    elif estado_cliente == 'I':
        estado_cliente = 'Inactivo'
        color_estado = 2
    elif estado_cliente == 'P':
        estado_cliente = 'Pre legal'
        color_estado = 3
    elif estado_cliente == 'L':
        estado_cliente = 'Legal'
        color_estado = 4
    elif estado_cliente == 'X':
        estado_cliente = 'Bloqueado'
        color_estado = 4

    total_cartera = Documentos.objects.TotalCarteraCliente(cliente_id)
    if total_cartera['Total']:
        cartera = total_cartera['Total']

    total_protesto = Cheques_protestados.objects.TotalProtestosCliente(cliente_id)
    if total_protesto['Total']:
        protestos = total_protesto['Total']

    total_reestructuracion = Pagares.objects.TotalPagaresCliente(cliente_id)
    if total_reestructuracion['Total']:
        restructuracion = total_reestructuracion['Total']

    data = {
        'cliente_id': cliente_id,
        'valor_linea': valor_linea,
        'porc_disponible': porc_disponible,
        'dias_ultima_operacion': dias_ultima_operacion,
        'nombre_cliente': nombre_cliente,
        'estado': estado_cliente,
        'clase': clase_cliente,
        'color_estado': color_estado,
        'total_cartera_protestos': cartera + protestos,
        'total_reestructuracion': restructuracion,
    }
    
    serializer = EstadoOperativoClienteSerializer(data)
    # return Response(serializer.data)
    return JsonResponse(serializer.data)
