from django.urls import URLPattern, path
from solicitudes.views import SolicitudesView, DetalleSolicitudFacturasPuras , \
    DetalleSolicitudConAccesorios, EliminarDocumento, EliminarAsignacion, \
    DatosAsignacionConAccesorios,  DatosFacturasPuras, RecuperarDocumento,\
    AsignacionFacturasPurasView, DatosAsignacionFacturasPurasNueva, \
    DatosAsignacionConAccesoriosNueva, AsignacionConAccesoriosView, \
    ClienteCrearView, DatosAccesorioEditar, ImportarOperacion, PedirArchivoXML,\
    GeneraListaSolicitudesRegistradasJSON, NivelesAprobacionView, \
    NivelAprobacionCrearView, NivelAprobacionEditarView, \
    ExcesosTemporalesView, AceptarExcesoTemporal, RechazarExcesoTemporal, \
    InstruccionDePagoView

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
    path('recuperardetalleasignacion/<int:asignacion_id>/<int:documento_id>/<tipo_asignacion>'
        ,RecuperarDocumento),
    path('importarxml',PedirArchivoXML, name='importar_xml'),
    path('importaroperacion',ImportarOperacion, name='importar_xml_facturaspuras'),
    path('asignacionesregistradasjson/<desde>/<hasta>',GeneraListaSolicitudesRegistradasJSON
        , name="asignacionesregistradas_json"),
    path('listanivelesaprobacion/',NivelesAprobacionView.as_view()
         , name='listanivelesaprobacion'),
    path('nivelaprobacionnuevo/',NivelAprobacionCrearView.as_view(), name='nivelaprobacion_nuevo'),
    path('nivelaprobacioneditar/<int:pk>',NivelAprobacionEditarView.as_view(), name='nivelaprobacion_editar'),
    path('listaexcesostemporales/',ExcesosTemporalesView.as_view(), \
        name='lista_excesos_temporales'),
    path('listaexcesostemporales/<filtro>',ExcesosTemporalesView.as_view(), \
        name='lista_excesos_temporales'),
    path('aceptarexcesotemporal/<int:exceso_id>',AceptarExcesoTemporal, \
        name='aceptar_exceso_temporal'),
    path('rechazarexcesotemporal/<int:exceso_id>',RechazarExcesoTemporal, \
        name='rechazar_exceso_temporal'),
    path('instruccion_de_pago/<int:pk>', InstruccionDePagoView.as_view(), \
        name='instruccion_de_pago'),
]