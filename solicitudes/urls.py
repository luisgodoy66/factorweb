from django.urls import URLPattern, path
from solicitudes.views import SolicitudesView, DetalleSolicitudFacturasPuras , \
    DetalleSolicitudConAccesorios, EliminarDocumento, EliminarAsignacion, \
    DatosAsignacionConAccesorios,  DatosFacturasPuras, \
    AsignacionFacturasPurasView, DatosAsignacionFacturasPurasNueva, \
    DatosAsignacionConAccesoriosNueva, AsignacionConAccesoriosView, \
    ClienteCrearView, DatosAccesorioEditar, ImportarOperacion, PedirArchivoXML
# ,DatosChequeAccesorio

urlpatterns=[
    path('listasolicitudes/',SolicitudesView.as_view(), \
        name='listasolicitudes'),
    path('crearcliente/',ClienteCrearView.as_view(), \
        name='cliente_nuevo'),
    path('nuevasolicitud/',DatosAsignacionFacturasPurasNueva
        , name='asignacionfacturaspuras_nueva'),
    path('nuevasolicitudconaccesorios/',DatosAsignacionConAccesoriosNueva
        , name='asignacionconaccesorios_nueva'),
    path('editarsolicitud/<int:pk>',AsignacionFacturasPurasView.as_view()
        , name='asignacionfacturaspuras_editar'),
    path('editarsolicitudconaccesorios/<int:pk>',AsignacionConAccesoriosView.as_view(), \
        name='asignacionconaccesorios_editar'),
    path('editarsolicitudfacturaspuras/<int:asignacion_id>/<int:cliente_id>/<tipo_factoring_id>',\
        DatosFacturasPuras, name='facturaspuras_editar'),
    path('nuevasolicitudfacturaspuras/<int:cliente_id>/<tipo_factoring_id>',\
        DatosFacturasPuras, name="facturaspuras_nueva"),
    path('editardocumentofacturaspuras/<int:asignacion_id>/<int:cliente_id>/<tipo_factoring_id>/<int:doc_id>',\
        DatosFacturasPuras, name='facturaspuras_editar'),
    path('editardocumentoconaccesorios/<int:asignacion_id>/<int:cliente_id>/<tipo_factoring_id>',\
        DatosAsignacionConAccesorios, name='documentoconaccesorios_editar'),
    path('nuevodocumentoconaccesorios/<int:cliente_id>/<tipo_factoring_id>/<cliente_nombre>',\
        DatosAsignacionConAccesorios),
    path('detallesolicitud/<int:asignacion_id>',DetalleSolicitudFacturasPuras, \
        name='detallesolicitudfacturaspuras'),
    path('detallesolicitudconaccesorios/<int:asignacion_id>',DetalleSolicitudConAccesorios
        ,name='detallesolicitudconaccesorios'),
    path('eliminarasignacion/<int:asignacion_id>',EliminarAsignacion),
    path('editarchequeaccesorio/<tipo_factoring_id>',DatosAccesorioEditar
        , name="editarchequeaccesorio"),
    path('editarchequeaccesorio/<int:accesorio_id>/<tipo_factoring_id>',DatosAccesorioEditar
        , name="editarchequeaccesorio"),
    path('eliminardetalleasignacion/<int:asignacion_id>/<int:documento_id>/<tipo_asignacion>'
        ,EliminarDocumento),
    path('importarxml',PedirArchivoXML, name='importar_xml'),
    path('importaroperacion',ImportarOperacion, name='importar_xml_facturaspuras'),

]