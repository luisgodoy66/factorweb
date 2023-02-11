from django.urls import path
from .views import CuentasView, CuentasBancariasNew, CuentasBancariasEdit\
    , CobranzasPorConfirmarView, ConfirmarCobranza, AceptarConfirmacion\
    , CargosPendientesView, DebitoBancarioEdit, DebitoBancarioSinCobranza

urlpatterns = [
    # cobranzas
    path('listacuentas/',CuentasView.as_view(), name="listacuentasconjuntas"),
    path('cuentabancarianueva/',CuentasBancariasNew.as_view(), name="cuentabancaria_nueva"),
    path('datoscuentaeditar/<int:pk>',CuentasBancariasEdit.as_view(), name="cuentabancaria_editar"),
    path('listacobranzasporconfirmar/',CobranzasPorConfirmarView.as_view()
        , name="listacobranzasporconfirmar"),
    path('confirmarcobranza/<int:cobranza_id>/<tipo_operacion>/<int:cuenta_conjunta>'
        ,ConfirmarCobranza, name="confirmarcobranza"),
    path('aceptarconfirmacion/', AceptarConfirmacion),
    path('listacargospendientes/',CargosPendientesView.as_view()
        , name="listacargospendientes"),
    path('datosdebitoeditar/<int:pk>',DebitoBancarioEdit.as_view(), name="debitobancario_editar"),
    path('datosdebitonuevo',DebitoBancarioSinCobranza, name="debitobancario_nuevo"),
]