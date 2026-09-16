from django.urls import path
from .views import ConsultarFacturaAI, estado_operativo_cliente_api, \
     ConfiguracionesSlackView, ConfiguracionSlackNew, \
     ConfiguracionSlackEdit, ConfiguracionesTwilioView, \
     ConfiguracionTwilioNew , ConfiguracionTwilioEdit
from .slack import enviar_solicitud_aprobacion, manejar_interactividad\
     , reenviar_solicitud_aprobacion
from .sri import obtener_datos_contribuyente, \
     consulta_estado_comprobante_sri
from .twilio_service import historial_mensajes_whatsapp,\
     enviar_mensaje_whatsapp, webhook_whatsapp_twilio
from .google import oauth2callback, google_login, \
     crear_evento_recordatorio_cobranza, \
     google_session_active
from .whatsapp import enviar_mensaje, webhook_whatsapp
from .views import InvoiceAIAnalysisView

urlpatterns = [
    # Otras rutas...
    path('estado-operativo-cliente/<str:cliente_id>/'
         , estado_operativo_cliente_api, name='estado_operativo_cliente_api'),
     # Rutas para SRI
     path('sri/obtener-datos-contribuyente/<ruc>', obtener_datos_contribuyente
         , name='obtener_datos_contribuyente'),
     path('sri/consulta-estado-comprobante/<access_key>', consulta_estado_comprobante_sri
         , name='consulta_estado_comprobante_sri'),
     # Rutas para Slack
    path('slack/enviar-solicitud-aprobacion/<int:id_solicitud>'
         , enviar_solicitud_aprobacion, name='enviar_solicitud_aprobacion'),
    path('slack/reenviar-solicitud-aprobacion/<int:id_solicitud>'
         , reenviar_solicitud_aprobacion, name='reenviar_solicitud_aprobacion'),
    path('slack/interactive-endpoint/', manejar_interactividad
         , name='manejar_interactividad'),
    path('listaconfiguracionesslack/',ConfiguracionesSlackView.as_view()
         , name='lista_configuraciones_slack'),
    path('configuracionesslacknueva/',ConfiguracionSlackNew.as_view()
         , name='configuraciones_slack_nueva'),
    path('configuracionesslackeditar/<int:pk>',ConfiguracionSlackEdit.as_view()
         , name='configuraciones_slack_editar'),
     # Rutas para Twilio
    path('listaconfiguracionestwilio/',ConfiguracionesTwilioView.as_view()
         , name='lista_configuraciones_twilio'),
    path('configuracionestwilonueva/',ConfiguracionTwilioNew.as_view()
         , name='configuraciones_twilio_nueva'),
    path('configuracionestwilioeditar/<int:pk>',ConfiguracionTwilioEdit.as_view()
         , name='configuraciones_twilio_editar'),
    path('twilio/enviarmensajewhatsapp/<whatsapp_destino>', enviar_mensaje_whatsapp
         , name='enviar_mensaje_twilio_whatsapp'),
     path('historialmensajewhatsapp/<int:gestion_cobro_id>/', historial_mensajes_whatsapp
         , name='historial_mensajes_whatsapp'),
     path('twilio/webhook_whatsapp_twilio/', webhook_whatsapp_twilio
        , name='webhook_whatsapp_twilio'),
     # Rutas para Google
     path('google/logingoogle/', google_login, name='google_login'),
     path('google/oauth2callback/', oauth2callback, name='oauth2callback'),
     path('google/crear_evento_recordatorio_cobranza/<cliente>', crear_evento_recordatorio_cobranza
           , name='crear_evento_recordatorio_cobranza'),
     path('google/session/active/', google_session_active, name='google_session_active'),
     # Rutas para WhatsApp
     path('whatsapp/enviar_mensaje/<str:numero_destino>', enviar_mensaje
          , name='enviar_mensaje_whatsapp'),
     path('whatsapp/webhook/', webhook_whatsapp, name='webhook_whatsapp'),
    path("invoices/<int:id>/analyze-ai/", InvoiceAIAnalysisView.as_view(),
        name="invoice-ai-analysis"
    ),
    path("invoices/<int:id>/consultar-ai/", ConsultarFacturaAI, name="consultar-factura-ai"    ),
]
