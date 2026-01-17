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
# factoring/api/views.py

from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework import status

from .models import  InvoiceAIAnalysis
# from solicitudes.models import Documentos as Invoice, Asignacion
from .servicios import analyze_invoice_with_ai
from .servicios import parse_ai_response

from datetime import date, timedelta

from operaciones.models import Datos_operativos, Documentos, Pagares
from cobranzas.models import Cheques_protestados
from bases.models import Usuario_empresa, Empresas
from solicitudes import models as ModelosSolicitud
from clientes import models as ModeloCliente
from .models import Configuracion_slack, Configuracion_twilio_whatsapp
from cobranzas.models import Documentos_detalle as CobranzasDocumentosDetalle

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from bases.views import SinPrivilegios

from .forms import SlackForm, Twilio_whatsapp_Form

class ConfiguracionesSlackView(SinPrivilegios, generic.ListView):
    model = Configuracion_slack
    template_name = "slack/listaconfiguracionesslack.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="api.view_configuracion_slack"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Configuracion_slack.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ConfiguracionesSlackView, self).get_context_data(**kwargs)
        sp = ModelosSolicitud.Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class ConfiguracionSlackNew(SinPrivilegios, generic.CreateView):
    model = Configuracion_slack
    template_name="slack/datosconfiguracionslack_form.html"
    context_object_name = "configuracion"
    login_url = 'bases:login'
    form_class=SlackForm
    success_url=reverse_lazy("api:lista_configuraciones_slack")
    success_message="Configuración creada satisfactoriamente"
    permission_required="api.add_configuracion_slack"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ConfiguracionSlackNew, self).get_context_data(**kwargs)
        sp = ModelosSolicitud.Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context
    
class ConfiguracionSlackEdit(SinPrivilegios, generic.UpdateView):
    model = Configuracion_slack
    template_name="slack/datosconfiguracionslack_form.html"
    context_object_name = "configuracion"
    form_class=SlackForm
    success_url=reverse_lazy("api:lista_configuraciones_slack")
    success_message="Configuración actualizada satisfactoriamente"
    permission_required="api.change_configuracion_slack"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ConfiguracionSlackEdit, self).get_context_data(**kwargs)
        sp = ModelosSolicitud.Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class ConfiguracionesTwilioView(SinPrivilegios, generic.ListView):
    model = Configuracion_twilio_whatsapp
    template_name = "twilio/listaconfiguracionestwilio.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="api.view_configuracion_twilio_whatsapp"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Configuracion_twilio_whatsapp.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ConfiguracionesTwilioView, self).get_context_data(**kwargs)
        sp = ModelosSolicitud.Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class ConfiguracionTwilioNew(SinPrivilegios, generic.CreateView):
    model = Configuracion_twilio_whatsapp
    template_name="twilio/datosconfiguraciontwiliowhatsapp_form.html"
    context_object_name = "configuracion"
    login_url = 'bases:login'
    form_class=Twilio_whatsapp_Form
    success_url=reverse_lazy("api:lista_configuraciones_twilio")
    success_message="Configuración creada satisfactoriamente"
    permission_required="api.add_configuracion_twilio_whatsapp"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ConfiguracionTwilioNew, self).get_context_data(**kwargs)
        sp = ModelosSolicitud.Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context
    
class ConfiguracionTwilioEdit(SinPrivilegios, generic.UpdateView):
    model = Configuracion_twilio_whatsapp
    template_name="twilio/datosconfiguraciontwiliowhatsapp_form.html"
    context_object_name = "configuracion"
    form_class=Twilio_whatsapp_Form
    success_url=reverse_lazy("api:lista_configuraciones_twilio")
    success_message="Configuración actualizada satisfactoriamente"
    permission_required="api.change_configuracion_twilio_whatsapp"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ConfiguracionTwilioEdit, self).get_context_data(**kwargs)
        sp = ModelosSolicitud.Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

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

class InvoiceAIAnalysisView(APIView):
    """
    POST /api/invoices/<id>/analyze-ai/
    """

    def post(self, request, id):
        try:
            invoice = ModelosSolicitud.Documentos.objects.select_related(
                 'comprador', 'cxasignacion__cxcliente',
            ).get(id=id)
        except ModelosSolicitud.Documentos.DoesNotExist:
            return Response(
                {"error": "Factura no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(invoice, 'ai_analysis'):
            return Response(
                {"error": "La factura ya fue analizada"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Construir historial resumido del solciitante/cliente
        solicitante = invoice.cxasignacion.cxcliente
        facturas_previas = ModelosSolicitud.Documentos.objects\
            .filter( leliminado=False,
                    cxasignacion__cxestado = 'A',
                    cxasignacion__cxcliente=solicitante.id
                    ).count()
        
        # determinar si es cliente
        es_cliente = ModelosSolicitud.Asignacion.objects\
            .filter(
                cxcliente=solicitante, cliente__isnull = False, leliminado=False
                )\
            .first().cliente
        if es_cliente:
            cliente = ModeloCliente.Datos_generales.objects\
                .filter(
                    id=es_cliente.id
                    )\
                .first()
            
            total_negociado = cliente.monto_total_negociado()
            promedio_demora_pago = cliente.npromediodemoradepago
            actividad_economica = cliente.cxcliente.actividad.ctactividad if cliente.cxcliente.actividad.ctactividad else 'N/A'
            inicio_actividades = cliente.cxcliente.dinicioactividades.strftime("%Y-%m-%d") if cliente.cxcliente.dinicioactividades else 'N/A'

            # relacion cliente 
            promedio_demora_pago_deudor = CobranzasDocumentosDetalle.objects\
                .promedio_ponderado_demora_por_deudor(cliente.id, invoice.comprador.id)
        else:
            promedio_demora_pago = 'N/A'
            inicio_actividades = solicitante.dinicioactividades.strftime("%Y-%m-%d") if solicitante.dinicioactividades else 'N/A'
            actividad_economica = solicitante.ctgirocomercial if solicitante.ctgirocomercial  else 'N/A'


        client_history = f"""
- Cliente: {solicitante.ctnombre}
- Facturas previas: {facturas_previas - 1}
- Monto total negociado: {total_negociado if total_negociado else 'N/A'}
- Promedio demora de pago: {promedio_demora_pago}
- Actividad económica: {actividad_economica}
- Inicio de actividades: {inicio_actividades}
"""

        # 🔹 Construir historial del deudor/comprador
        debtor_history = f"""
- Comprador: {invoice.ctcomprador}
- Ultimas cobranzas: {invoice.comprador.reporte_ultimas_cobranzas() if invoice.comprador else 'N/A'}
- Actividad económica: {invoice.comprador.cxcomprador.actividad.ctactividad if invoice.comprador.cxcomprador.actividad else 'N/A'}
- Inicio de actividades: {invoice.comprador.cxcomprador.dinicioactividades.strftime("%Y-%m-%d") if invoice.comprador.cxcomprador.dinicioactividades else 'N/A'}
- Promedio demora de pago con el cliente: {promedio_demora_pago_deudor if es_cliente else 'N/A'}
"""

        ai_raw = analyze_invoice_with_ai(
            invoice,
            client_history,
            debtor_history
        )

        parsed = parse_ai_response(ai_raw)

        analysis = InvoiceAIAnalysis.objects.create(
            invoice=invoice,
            risk_level=parsed["risk_level"],
            analysis_text=parsed["analysis"],
            recommendation=parsed["recommendation"],
            raw_response=parsed["raw"],
            cxusuariocrea=request.user,
            empresa = Usuario_empresa.objects.filter(user=request.user).first().empresa
        )

        return Response(
            {
                "invoice_id": invoice.id,
                "risk_level": analysis.risk_level,
                "analysis": analysis.analysis_text,
                "recommendation": analysis.recommendation,
                "created_at": analysis.dregistro.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_201_CREATED
        )

def ConsultarFacturaAI(request, id):
    try:
        analysis = InvoiceAIAnalysis.objects.get(invoice__id=id)
        return JsonResponse(
            {
                "invoice_id": analysis.invoice.id,
                "risk_level": analysis.risk_level,
                "analysis": analysis.analysis_text,
                "recommendation": analysis.recommendation,
                "created_at": analysis.dregistro.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    except InvoiceAIAnalysis.DoesNotExist:
        return JsonResponse(
            {"error": "Análisis de IA no encontrado para esta factura"},
            status=404
        )