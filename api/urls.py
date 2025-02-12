from django.urls import path
from .views import estado_operativo_cliente_api, \
     ConfiguracionesSlackView, ConfiguracionSlackNew, ConfiguracionSlackEdit
from .slack import enviar_solicitud_aprobacion, manejar_interactividad\
     , reenviar_solicitud_aprobacion

urlpatterns = [
    # Otras rutas...
    path('estado-operativo-cliente/<str:cliente_id>/'
         , estado_operativo_cliente_api, name='estado_operativo_cliente_api'),
    path('slack/enviar-solicitud-aprobacion/<int:id_solicitud>', enviar_solicitud_aprobacion
         , name='enviar_solicitud_aprobacion'),
    path('slack/reenviar-solicitud-aprobacion/<int:id_solicitud>', reenviar_solicitud_aprobacion
         , name='reenviar_solicitud_aprobacion'),
    path('slack/interactive-endpoint/', manejar_interactividad
         , name='manejar_interactividad'),
    path('listaconfiguracionesslack/',ConfiguracionesSlackView.as_view(), \
        name='lista_configuraciones_slack'),
    path('configuracionesslacknueva/',ConfiguracionSlackNew.as_view(), \
        name='configuraciones_slack_nueva'),
    path('configuracionesslackeditar/<int:pk>',ConfiguracionSlackEdit.as_view(), \
        name='configuraciones_slack_editar'),
]