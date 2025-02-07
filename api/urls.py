from django.urls import path
from .views import estado_operativo_cliente_api
from .slack import enviar_solicitud_aprobacion, manejar_interactividad

urlpatterns = [
    # Otras rutas...
    path('estado-operativo-cliente/<str:cliente_id>/'
         , estado_operativo_cliente_api, name='estado_operativo_cliente_api'),
    path('slack/enviar-solicitud-aprobacion/', enviar_solicitud_aprobacion
         , name='enviar_solicitud_aprobacion'),
    path('slack/interactive-endpoint/', manejar_interactividad
         , name='manejar_interactividad'),
]