from django.urls import path
from .views import CuentasView, CuentasBancariasNew, CuentasBancariasEdit\
    , CobranzasPorConfirmarView, ConfirmarCobranza, AceptarConfirmacion\
    , CargosPendientesView, DebitoBancarioEdit, DebitoBancarioSinCobranza\
    , EliminarNotaDebito, TransferenciasView, TansferenciaEdit\
    , DatosTransferencia, EliminarTransferencia

urlpatterns = [
    # cobranzas
    path('listacuentas/',CuentasView.as_view(), name="listacuentasconjuntas"),
    path('cuentabancarianueva/',CuentasBancariasNew.as_view()
         , name="cuentabancaria_nueva"),
    path('datoscuentaeditar/<int:pk>',CuentasBancariasEdit.as_view()
         , name="cuentabancaria_editar"),
    path('listacobranzasporconfirmar/',CobranzasPorConfirmarView.as_view()
        , name="listacobranzasporconfirmar"),
    path('confirmarcobranza/<int:cobranza_id>/<tipo_operacion>/<int:cuenta_conjunta>'
        ,ConfirmarCobranza, name="confirmarcobranza"),
    path('aceptarconfirmacion/', AceptarConfirmacion),
    path('listacargospendientes/',CargosPendientesView.as_view()
        , name="listacargospendientes"),
    path('datosdebitoeditar/<int:pk>',DebitoBancarioEdit.as_view()
         , name="debitobancario_editar"),
    path('debitoeliminar/<int:pk>',EliminarNotaDebito, name="debitobancario_eliminar"),
    path('datosdebitonuevo',DebitoBancarioSinCobranza, name="debitobancario_nuevo"),
    path('listatransferencias/',TransferenciasView.as_view()
        , name="listatransferencias"),
    path('transferencianueva/',DatosTransferencia, name="transferencia_nueva"),
    path('transferenciaeditar/<int:pk>',TansferenciaEdit.as_view()
         , name="transferencia_editar"),
    path('eliminartransferencia/<int:pk>',EliminarTransferencia
        , name='transferencia_eliminar'),
]