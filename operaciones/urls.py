from django.urls import URLPattern, path

from .views import  AnexosNew, AsignacionesView, DatosOperativosView, \
    DatosOperativos, AsignacionesConsulta, \
    AceptarAsignacion, DetalleCargosAsignacion, MaestroMovimientosView, \
    SumaCargos, AceptarDocumentos,MaestroMovimientosView, MaestroMovimientoNew, \
    MaestroMovimientoEdit, CondicionesOperativasView, CondicionesOperativas,\
    DetalleCondicionOperativa, EliminarDetalleCondicionOperativa, AnexosView, \
    EditarTasasDocumentoSolicitud, GeneraDetalleParaTabla1, AnexosEdit,\
    AsignacionesPendientesDesembolsarView, DesembolsarAsignacion, GenerarAnexos, \
    ReversaAceptacionAsignacion, GeneraListaAsignacionesJSON, \
    GeneraListaAsignacionesRegistradasJSON, GeneraResumenAntigüedadCarteraJSON,\
    EstadosOperativosView, EstadoOperativoCliente, AntigüedadCarteraClienteJSON,\
    GeneraListaCarteraClienteJSON, GeneraListaChequesADepositarClienteJSON,\
    GeneraListaCargosPendientesClienteJSON, GeneraListaProtestosPendientesClienteJSON


from .reportes import ImpresionAsignacion, ImpresionAsignacionDesdeSolicitud,\
    ImpresionAntiguedadCartera, ImpresionFacturasPendientes

urlpatterns = [
# datos operativos
    path('listadatosoperativos/',DatosOperativosView.as_view(), \
        name='listadatosoperativos'),
    path('editardatooperativo/<cliente_ruc>',DatosOperativos, \
        name='datosoperativos_editar'),
    path('listaestadosoperativos',EstadosOperativosView.as_view(), \
         name='listaestadosoperativos'),
    path('estadosoperativocliente/<cliente_id>/<nombre_cliente>'
         ,EstadoOperativoCliente, name='estadooperativocliente'),
    path('antigüedadcarteracliente/<cliente_id>', AntigüedadCarteraClienteJSON),
    path('carteraclientejson/<cliente_id>/<fecha_corte>',GeneraListaCarteraClienteJSON, 
        name="carteracliente_json"),
    path('chequesadepositarclientejson/<cliente_id>/<fecha_corte>'
         ,GeneraListaChequesADepositarClienteJSON, name="chequesadepositarcliente_json"),
    path('listacargospendientesclientejson/<cliente_id>',\
         GeneraListaCargosPendientesClienteJSON, name="listacargospendientescliente_json"),
    path('protestospendientesjson/<cliente_id>',GeneraListaProtestosPendientesClienteJSON, 
        name="protestospendientescliente_json"),
# movimientos
    path('listamaestromovimientos/',MaestroMovimientosView.as_view(), \
        name='listamaestromovimientos'),
    path('nuevomovimiento/',MaestroMovimientoNew.as_view(), \
        name='movimiento_nuevo'),
    path('editarmovimiento/<int:pk>/',MaestroMovimientoEdit.as_view(), \
        name='movimiento_editar'),
# condiciones operativas
    path('listacondicionesoperativas/',CondicionesOperativasView.as_view(), \
        name='listacondicionesoperativas'),
    path('condicionesoperativas/',CondicionesOperativas, \
        name='condicionesoperativas_nueva'),
    path('editarcondicionesoperativas/<int:condicion_id>',\
        CondicionesOperativas, \
        name='condicionesoperativas_editar'),
    path('detallecondicionoperativa/<int:condicion_id>',\
        DetalleCondicionOperativa, \
        name='detallecondicionoperativa'),
    path('eliminardetallecondicionoperativa/<int:detalle_id>',\
        EliminarDetalleCondicionOperativa, \
        name='eliminardetallecondicionoperativa'),
# asignaciones
    path('listaasignaciones/',AsignacionesView.as_view(), \
        name='listaasignaciones'),
    path('consultaasignaciones/',AsignacionesConsulta.as_view(), \
        name='consulta_asignaciones'),
    path('listaasignacionespendientesdesembolsar/',AsignacionesPendientesDesembolsarView.as_view(), \
        name='listaasignacionespendientesdesembolsar'),
    path('desembolsarasignaciones/<int:pk>/<cliente_ruc>',DesembolsarAsignacion, \
        name='desembolsarasignacion'),
    path('aceptarasignacion/<int:asignacion_id>',AceptarAsignacion, \
        name='aceptarasignacion'),
    path('sumacargos/<int:asignacion_id>/<gao_carga_iva>/<dc_carga_iva>/<carga_gao>/<carga_dc>/<int:porcentaje_iva>',\
        SumaCargos),
    path('detallecargosasignacion/<int:asignacion_id>/<fecha_desembolso>/',\
        DetalleCargosAsignacion, name='detallecargosasignacion'),
    path('detallecargosasignacion/<int:asignacion_id>/<fecha_desembolso>/<int:condicion_id>',\
        DetalleCargosAsignacion, name='detallecargosasignacion'),
    path('refrescadetallesolicitud/<int:asignacion_id>',\
        GeneraDetalleParaTabla1,),
    path('aceptardocumentos/',AceptarDocumentos),
    path('editartasasdocumento/<int:documento_id>/<fecha_desembolso>/<int:asignacion_id>'\
        , EditarTasasDocumentoSolicitud, name="editartasasdocumento"),
    path("reporteasignacion/<int:asignacion_id>",ImpresionAsignacion, \
        name='reporteasignacion'),
    path("reporteasignaciondesdesolicitud/<int:asignacion_id>",\
        ImpresionAsignacionDesdeSolicitud ),
    path("generaranexos/<int:asignacion_id>", GenerarAnexos, name="generaranexos"),
    path('listaanexos/',AnexosView.as_view(), name='listaanexos'),
    path('nuevoanexo/',AnexosNew.as_view(), name='anexo_nuevo'),
    path('editaranexo/<int:pk>',AnexosEdit.as_view(), name='anexo_editar'),
    path('reversaraceptacionasignacion/<int:pid_asignacion>',ReversaAceptacionAsignacion),
    path('asignacionesjson/<desde>/<hasta>',GeneraListaAsignacionesJSON, name="asignaciones_json"),
    path('asignacionesregistradasjson/<desde>/<hasta>',GeneraListaAsignacionesRegistradasJSON
        , name="asignacionesregistradas_json"),
    path('antigüedadcartera', GeneraResumenAntigüedadCarteraJSON),
    path('impresioncartera', ImpresionAntiguedadCartera, name='antigüedad_por_cliente'),
    path('impresioncarterapendiente', ImpresionFacturasPendientes, name='detalle_facturas_pendientes'),
    ]
