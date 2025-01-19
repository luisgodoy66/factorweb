from django.urls import path
from .views import estado_operativo_cliente_api

urlpatterns = [
    # Otras rutas...
    path('estado-operativo-cliente/<str:cliente_id>/'
         , estado_operativo_cliente_api, name='estado_operativo_cliente_api'),
]