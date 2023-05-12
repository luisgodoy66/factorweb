from django.urls import URLPattern, path
from .views import  ClientesView,  DatosClientes, DatosClienteNatural \
    , LineasView, LineaNew, LineaEdit, CompradoresView\
    , CuposCompradoresView, CuposCompradoresEdit, DatosCompradores\
    , CuposCompradoresNew, CuentasBancariasView, CuentasBancariasCliente\
    , DetalleCuentasBancarias, CuentasBancariasNew, EliminarCuentaBancaria\
    , ActualizarCuentaTransferencia,  DatosClienteJuridico, CuentasBancariasDeudoresView\
    , CuentasBancariasDeudorNew, CuentasBancariasDeudorEdit, ClientesSolicitudesView\
    , CompradorEdit,CuentasBancariasEdit

urlpatterns = [
    path('listaclientessolicitudes/',ClientesSolicitudesView.as_view()
        , name='listaclientessolicitudes'),
    path('listaclientes/',ClientesView.as_view(), name='listaclientes'),
    path('listacompradores/',CompradoresView.as_view(), name='listacompradores'),
    path('clientenuevo/',DatosClientes, name='datoscliente_nuevo'),
    path('edit/<cliente_id>',DatosClientes, name='cliente_editar'),
    path('clientenuevo/<solicitante_id>',DatosClientes, name='solicitante_nuevo'),
    path('compradornuevo/',DatosCompradores, name='comprador_nuevo'),
    path('editcomprador/<comprador_id>',DatosCompradores, name='comprador_editar'),
    path('editnatural/<cliente_id>',DatosClienteNatural
        , name='clientenatural_editar'),
    path('editjuridico/<cliente_id>',DatosClienteJuridico
        , name='clientejuridico_editar'),
    # línea factoring
    path('listalineas/',LineasView.as_view(), name='listalineas'),
    path('lineafactoringnueva/<cliente>/<cliente_id>',LineaNew.as_view()
        , name='lineafactoring_nueva'),
    path('editlineafactoring/<cliente>/<cliente_id>/<int:pk>',LineaEdit.as_view()
        , name='lineafactoring_editar'),
    # cupos
    path('listacupos/',CuposCompradoresView.as_view(), name='listacupos'),
    path('cuponuevo/',CuposCompradoresNew.as_view(), name='cupo_nuevo'),
    path('editcupo/<int:pk>',CuposCompradoresEdit.as_view(), name='cupo_editar'),
    # cuentas
    path('listacuentasbancarias/',CuentasBancariasView.as_view()
    , name='listacuentasbancarias'),
    path('listacuentasbancariasdeudores/',CuentasBancariasDeudoresView.as_view()
        , name='listacuentasbancarias_deudores'),
    path('listacuentasbancariascliente/<cliente_id>/',CuentasBancariasCliente
        , name='listacuentasbancariascliente'),
    path('detallecuentasbancariascliente/<cliente_id>/',DetalleCuentasBancarias
        , name='detallecuentasbancariascliente'),
    path('cuentabancarianueva/<cliente_id>',CuentasBancariasNew.as_view()
        , name='cuentabancaria_nueva'),
    path('editcuentabancaria/<cliente_id>/<int:pk>',CuentasBancariasEdit.as_view()
    , name='cuentabancaria_editar'),
    path('cuentabancariadeudornueva/',CuentasBancariasDeudorNew.as_view()
        , name='cuentabancariadeudor_nueva'),
    path('cuentabancariadeudoreditar/<int:pk>',CuentasBancariasDeudorEdit.as_view()
        , name='cuentabancariadeudor_editar'),
    path('eliminarcuentabancaria/<int:pk>',EliminarCuentaBancaria
        , name='cuentabancaria_eliminar'),
    path('actualizarcuentatransferencia/<int:pk>/<cliente_ruc>',ActualizarCuentaTransferencia
        , name='cuentatransferencia_actualizar'),
    # estado operativo
    path('editestadoclasecomprador/<int:pk>',CompradorEdit.as_view()
        , name='estadoclasecomprador_editar'),
]
