from django.urls import path
from .views import CuentasView, CuentasEspecialesEdit, BuscarCuentasEspeciales\
    , CuentasEspecialesNew, CuentasBancosView, CuentaBancoNew, CuentaBancoEdit\
    , CuentasTiposFactoringView, CuentaTipoFactoringNew, CuentaTipoFactoringEdit\
    , CuentasTasasFactoringView, CuentasTasaTiposFactoringView\
     , CuentaTasaTipoFactoringNew, CuentaTasaTipoFactoringEdit,PendientesGenerarFacturaView\
     , GenerarFactura, ObtenerSecuenciaFactura, DesembolsosPendientesView
from .reportes import ImpresionDiarioContable

urlpatterns = [
    path('listacuentascontables/',CuentasView.as_view()
         , name="listacuentascontables"),
    path('buscarcuentasespeciales/',BuscarCuentasEspeciales
         , name="buscarcuentasespeciales"),
    path('asignarcuentascontables/',CuentasEspecialesNew.as_view()
         , name="asignarcuentascontables_nueva"),
    path('asignarcuentascontables/<pk>',CuentasEspecialesEdit.as_view()
         , name="asignarcuentascontables_editar"),
    path('listacuentasbancos/',CuentasBancosView.as_view()
         , name="listacuentasbancos"),
    path('cuentabanconueva/<banco>/<banco_id>',CuentaBancoNew.as_view()
         , name="cuentabanco_nueva"),
    path('cuentabancoeditar/<banco>/<banco_id>/<int:pk>',CuentaBancoEdit.as_view()
         , name="cuentabanco_editar"),
    path('listacuentastiposfactoring/',CuentasTiposFactoringView.as_view()
         , name="listacuentastiposfactoring"),
    path('cuentatipofactoringnueva/<tipofactoring>/<tipofactoring_id>'
         ,CuentaTipoFactoringNew.as_view(), name="cuentatipofactoring_nueva"),
    path('cuentatipofactoringeditar/<tipofactoring>/<tipofactoring_id>/<int:pk>'
         ,CuentaTipoFactoringEdit.as_view(), name="cuentatipofactoring_editar"),
    path('listacuentastasasfactoring/',CuentasTasasFactoringView.as_view()
         , name="listacuentastasasfactoring"),
    path('listacuentastasatiposfactoring/<int:tasa>/<nombre_tasa>'
         ,CuentasTasaTiposFactoringView.as_view(), name="listacuentastasatiposfactoring"),
    path('cuentatasatipofactoringnueva/<tipofactoring>/<tipofactoring_id>/<tasafactoring>/<tasafactoring_id>'
         ,CuentaTasaTipoFactoringNew.as_view(), name="cuentatasatipofactoring_nueva"),
    path('cuentatasatipofactoringeditar/<tipofactoring>/<tipofactoring_id>/<tasafactoring>/<tasafactoring_id>/<int:pk>'
         ,CuentaTasaTipoFactoringEdit.as_view(), name="cuentatasatipofactoring_editar"),
    path('listapendientesgenerarfactura',PendientesGenerarFacturaView.as_view()
         , name="listapendientesgenerarfactura"),
    path('generarfactura/<int:pk>/<tipo>/<operacion>',GenerarFactura, name="generar_factura"),
    path('obtenersecuenciafactura/<int:punto_emision>',ObtenerSecuenciaFactura,),
    path('imprimirdiariocontable/<int:diario_id>',ImpresionDiarioContable,),
    path('listadesembolsospendientes',DesembolsosPendientesView.as_view()
         , name="listadesembolsospendientes"),
]