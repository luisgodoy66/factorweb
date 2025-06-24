from django.urls import path
from .views import estado_operativo_cliente_api, \
     ConfiguracionesSlackView, ConfiguracionSlackNew, \
     ConfiguracionSlackEdit, ConfiguracionesTwilioView, \
     ConfiguracionTwilioNew , ConfiguracionTwilioEdit
from .slack import enviar_solicitud_aprobacion, manejar_interactividad\
     , reenviar_solicitud_aprobacion
from .sri import obtener_datos_contribuyente
from .twilio_service import historial_mensajes_whatsapp,\
     enviar_mensaje_whatsapp, webhook_whatsapp_twilio

# app_name = 'api'

urlpatterns = [
    # Otras rutas...
    path('estado-operativo-cliente/<str:cliente_id>/'
         , estado_operativo_cliente_api, name='estado_operativo_cliente_api'),
     path('sri/obtener-datos-contribuyente/<ruc>', obtener_datos_contribuyente
         , name='obtener_datos_contribuyente'),
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
    path('listaconfiguracionestwilio/',ConfiguracionesTwilioView.as_view()
         , name='lista_configuraciones_twilio'),
    path('configuracionestwilonueva/',ConfiguracionTwilioNew.as_view()
         , name='configuraciones_twilio_nueva'),
    path('configuracionestwilioeditar/<int:pk>',ConfiguracionTwilioEdit.as_view()
         , name='configuraciones_twilio_editar'),
    path('enviarmensajewhatsapp/', enviar_mensaje_whatsapp
         , name='enviar_mensaje_whatsapp'),
     path('historialmensajewhatsapp/<int:gestion_cobro_id>/', historial_mensajes_whatsapp
         , name='historial_mensajes_whatsapp'),
   path('webhook_whatsapp_twilio/', webhook_whatsapp_twilio
        , name='webhook_whatsapp_twilio'),
]