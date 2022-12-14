from django.urls import URLPattern, path
from .views import  ClientesView,  DatosClientes, DatosClienteNatural \
    , LineasView, LineaNew, LineaEdit, CompradoresView\
    , CuposCompradoresView, CuposCompradoresEdit, DatosCompradores\
    , CuposCompradoresNew, CuentasBancariasView, CuentasBancariasCliente\
    , DetalleCuentasBancarias, CuentasBancariasNew, EliminarCuentaBancaria\
    , ActualizarCuentaTransferencia,  DatosClienteJuridico, CuentasBancariasDeudoresView\
    , CuentasBancariasDeudorNew, CuentasBancariasDeudorEdit

urlpatterns = [
    path('listaclientes/',ClientesView.as_view(), name='listaclientes'),
    path('listacompradores/',CompradoresView.as_view(), name='listacompradores'),
    path('listalineas/',LineasView.as_view(), name='listalineas'),
    path('listacuentasbancarias/',CuentasBancariasView.as_view()
    , name='listacuentasbancarias'),
    path('listacuentasbancariasdeudores/',CuentasBancariasDeudoresView.as_view()
    , name='listacuentasbancarias_deudores'),
    path('listacuentasbancariascliente/<cliente_ruc>/',CuentasBancariasCliente
    , name='listacuentasbancariascliente'),
    path('detallecuentasbancariascliente/<cliente_ruc>/',DetalleCuentasBancarias
    , name='detallecuentasbancariascliente'),
    path('listacupos/',CuposCompradoresView.as_view(), name='listacupos'),
    path('clientenuevo/',DatosClientes, name='datoscliente_nuevo'),
    path('edit/<cliente_id>',DatosClientes, name='cliente_editar'),
    path('compradornuevo/',DatosCompradores, name='comprador_nuevo'),
    path('editcomprador/<comprador_id>',DatosCompradores, name='comprador_editar'),
    path('editnatural/<cliente_ruc>',DatosClienteNatural
    , name='clientenatural_editar'),
    path('editjuridico/<cliente_ruc>',DatosClienteJuridico
    , name='clientejuridico_editar'),
    path('lineafactoringnueva/<cliente>/<cliente_ruc>',LineaNew.as_view()
    , name='lineafactoring_nueva'),
    path('editlineafactoring/<cliente>/<cliente_ruc>/<int:pk>',LineaEdit.as_view()
    , name='lineafactoring_editar'),
    path('cuponuevo/',CuposCompradoresNew.as_view(), name='cupo_nuevo'),
    path('editcupo/<int:pk>',CuposCompradoresEdit.as_view(), name='cupo_editar'),
    path('cuentabancarianueva/<cliente_ruc>',CuentasBancariasNew.as_view()
    , name='cuentabancaria_nueva'),
    path('cuentabancariadeudornueva/',CuentasBancariasDeudorNew.as_view()
    , name='cuentabancariadeudor_nueva'),
    path('cuentabancariadeudoreditar/<int:pk>',CuentasBancariasDeudorEdit.as_view()
    , name='cuentabancariadeudor_editar'),
    # path('editcuentabancaria/<int:pk>',CuentasBancariasNew.as_view()
    # , name='cuentabancaria_editar'),
    path('eliminarcuentabancaria/<int:pk>',EliminarCuentaBancaria
    , name='cuentabancaria_eliminar'),
    path('actualizarcuentatransferencia/<int:pk>/<cliente_ruc>',ActualizarCuentaTransferencia
    , name='cuentatransferencia_actualizar'),
]
