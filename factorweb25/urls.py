"""
URL configuration for factorweb25 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('',include(('bases.urls','bases'),namespace='bases')),
    path('clientes/',include(('clientes.urls','clientes'),namespace='clientes')),
    path('empresa/',include(('empresa.urls','empresa'),namespace='empresa')),
    path('operaciones/',include(('operaciones.urls','operaciones'),namespace='operaciones')),
    path('pais/',include(('pais.urls','pais'),namespace='pais')),
    path('solicitudes/',include(('solicitudes.urls','solicitudes'),namespace='solicitudes')),
    path('cobranzas/',include(('cobranzas.urls','cobranzas'),namespace='cobranzas')),
    path('cuentasconjuntas/',include(('cuentasconjuntas.urls','cuentasconjuntas'),namespace='cuentasconjuntas')),
    path('contabilidad/',include(('contabilidad.urls','contabilidad'),namespace='contabilidad')),
    path('api/', include(('api.urls','api'),namespace='api')),
    
    path('admin/', admin.site.urls),
]
