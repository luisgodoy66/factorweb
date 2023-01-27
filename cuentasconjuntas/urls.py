from django.urls import path
from .views import CuentasView, CuentasBancariasNew, CuentasBancariasEdit\
    , CobranzasPorConfirmarView, ConfirmarCobranza, AceptarConfirmacion\
    , CargosPendientesView, DebitoBancarioEdit

urlpatterns = [
    # cobranzas
    path('listadocuentas/',CuentasView.as_view(), name="listadocuentasconjuntas"),
    path('cuentabancarianueva/',CuentasBancariasNew.as_view(), name="cuentabancaria_nueva"),
    path('datoscuentaeditar/<int:pk>',CuentasBancariasEdit.as_view(), name="cuentabancaria_editar"),
    path('listadocobranzasporconfirmar/',CobranzasPorConfirmarView.as_view()
        , name="listadocobranzasporconfirmar"),
    path('confirmarcobranza/<int:cobranza_id>/<tipo_operacion>/<int:cuenta_conjunta>'
        ,ConfirmarCobranza, name="confirmarcobranza"),
    path('aceptarconfirmacion/', AceptarConfirmacion),
    path('listadocargospendientes/',CargosPendientesView.as_view()
        , name="listadocargospendientes"),
    path('datosdebitoeditar/<int:pk>',DebitoBancarioEdit.as_view(), name="debitobancario_editar"),
]