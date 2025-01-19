from django.urls import URLPattern, path
from .views import BancosView, BancosNew , BancosEdit, \
    FeriadosView, FeriadosNew, FeriadosEdit

urlpatterns = [
    path('listabancos/',BancosView.as_view(), name='listabancos'),
    path('listaferiados/',FeriadosView.as_view(), name='listaferiados'),
    path('banconuevo/',BancosNew.as_view(), name='banco_nuevo'),
    path('feriadonuevo/',FeriadosNew.as_view(), name='feriado_nuevo'),
    path('editarbanco/<int:pk>',BancosEdit.as_view(), name='banco_editar'),
    path('editarferiado/<int:pk>',FeriadosEdit.as_view(), name='feriado_editar'),
]