from django.urls import path
from .views import CuentasView, CuentasBancariasNew, CuentasBancariasEdit

urlpatterns = [
    # cobranzas
    path('listadocuentas/',CuentasView.as_view(), name="listadocuentasconjuntas"),
    path('cuentabancarianueva/',CuentasBancariasNew.as_view(), name="cuentabancaria_nueva"),
    path('datoscuentaeditar/<pk>',CuentasBancariasEdit.as_view(), name="cuentabancaria_editar"),
]