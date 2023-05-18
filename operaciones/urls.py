from django.urls import URLPattern, path

from .views import  AnexosNew, AsignacionesView, DatosOperativosView, \
    DatosOperativos, AsignacionesConsulta, \
    AceptarAsignacion, DetalleCargosAsignacion, MaestroMovimientosView, \
    SumaCargos, AceptarDocumentos,MaestroMovimientosView, MaestroMovimientoNew, \
    MaestroMovimientoEdit, CondicionesOperativasView, DatosCondicionesOperativas,\
    DetalleCondicionOperativa, EliminarDetalleCondicionOperativa, AnexosView, \
    EditarTasasDocumentoSolicitud, GeneraDetalleParaTabla1, AnexosEdit,\
    AsignacionesPendientesDesembolsarView, DesembolsarAsignacion, GenerarAnexos, \
    ReversaAceptacionAsignacion, GeneraListaAsignacionesJSON, \
    GeneraListaAsignacionesRegistradasJSON, GeneraResumenAntigüedadCarteraJSON,\
    EstadosOperativosView, EstadoOperativoCliente, AntigüedadCarteraClienteJSON,\
    GeneraListaCarteraClienteJSON, GeneraListaChequesADepositarClienteJSON,\
    GeneraListaCargosPendientesClienteJSON, GeneraListaChequesQuitadosClienteJSON,\
    GeneraListaProtestosPendientesClienteJSON, GeneraListaCanjesClienteJSON,\
    CondicionesOperativasUpdate, DatosCondicionOperativaNueva, DesembolsosConsulta,\
    GeneraListaDesembolsosJSON


from .reportes import ImpresionAsignacion, ImpresionAsignacionDesdeSolicitud,\
    ImpresionAntiguedadCartera, ImpresionFacturasPendientes, ImpresionAccesoriosPendientes

urlpatterns = [
# datos operativos
    path('listadatosoperativos/',DatosOperativosView.as_view(), \
        name='listadatosoperativos'),
    path('editardatooperativo/<cliente_id>',DatosOperativos, \
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
    path('canjesclientejson/<cliente_id>',GeneraListaCanjesClienteJSON, 
        name="listacanjescliente_json"),
    path('chequesquitadosclientejson/<cliente_id>',GeneraListaChequesQuitadosClienteJSON, 
        name="listachequesquitadoscliente_json"),
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
    path('editarcondicionesoperativas/<int:pk>', CondicionesOperativasUpdate.as_view(),\
         name='condicionesoperativas_editar'),
    path('nuevacondicionesoperativas/',DatosCondicionOperativaNueva, \
        name='condicionesoperativas_nueva'),
    path('editarcondicionoperativa/<int:condicion_id>/<tipo_factoring_id>',\
        DatosCondicionesOperativas, name='condicionoperativa_editar'),
    path('nuevacondicionoperativa/<tipo_factoring_id>',
        DatosCondicionesOperativas, name='condicionoperativa_nueva'),
    path('detallecondicionoperativa/<int:condicion_id>',\
        DetalleCondicionOperativa, name='detallecondicionoperativa'),
    path('eliminardetallecondicionoperativa/<int:detalle_id>',\
        EliminarDetalleCondicionOperativa, name='eliminardetallecondicionoperativa'),
# asignaciones
    path('listaasignaciones/',AsignacionesView.as_view(), \
        name='listaasignaciones'),
    path('consultaasignaciones/',AsignacionesConsulta.as_view(), \
        name='consulta_asignaciones'),
    path('aceptarasignacion/<int:asignacion_id>',AceptarAsignacion, \
        name='aceptarasignacion'),
    path('sumacargos/<int:asignacion_id>/<gao_carga_iva>/<dc_carga_iva>/<carga_gao>/<carga_dc>/<int:porcentaje_iva>',\
        SumaCargos),
    path('detallecargosasignacion/<int:asignacion_id>/<fecha_desembolso>/',
        DetalleCargosAsignacion, name='detallecargosasignacion'),
    path('detallecargosasignacion/<int:asignacion_id>/<fecha_desembolso>/<int:condicion_id>',\
        DetalleCargosAsignacion, name='detallecargosasignacion'),
    path('refrescadetallesolicitud/<int:asignacion_id>',
        GeneraDetalleParaTabla1,),
    path('aceptardocumentos/',AceptarDocumentos),
    path('editartasasdocumento/<int:documento_id>/<fecha_desembolso>/<int:asignacion_id>'\
        , EditarTasasDocumentoSolicitud, name="editartasasdocumento"),
    path("reporteasignacion/<int:asignacion_id>",ImpresionAsignacion, 
        name='reporteasignacion'),
    path("reporteasignaciondesdesolicitud/<int:asignacion_id>",
        ImpresionAsignacionDesdeSolicitud ),
    path("generaranexos/<int:asignacion_id>", GenerarAnexos, name="generaranexos"),
    path('listaanexos/',AnexosView.as_view(), name='listaanexos'),
    path('nuevoanexo/',AnexosNew.as_view(), name='anexo_nuevo'),
    path('editaranexo/<int:pk>',AnexosEdit.as_view(), name='anexo_editar'),
    path('reversaraceptacionasignacion/<int:pid_asignacion>',ReversaAceptacionAsignacion),
    path('asignacionesjson/<desde>/<hasta>',GeneraListaAsignacionesJSON
         , name="asignaciones_json"),
    path('asignacionesregistradasjson/<desde>/<hasta>',GeneraListaAsignacionesRegistradasJSON
        , name="asignacionesregistradas_json"),
    path('antigüedadcartera', GeneraResumenAntigüedadCarteraJSON),
    path('impresioncartera', ImpresionAntiguedadCartera
         , name='antigüedad_por_cliente'),
    path('impresioncarterapendiente', ImpresionFacturasPendientes
         , name='detalle_facturas_pendientes'),
    path('impresionchequespendientes', ImpresionAccesoriosPendientes
         , name='detalle_cheques_pendientes'),
# desembolsos
    path('listaasignacionespendientesdesembolsar/',AsignacionesPendientesDesembolsarView.as_view(), \
        name='listaasignacionespendientesdesembolsar'),
    path('desembolsarasignaciones/<int:pk>/<cliente_id>',DesembolsarAsignacion, \
        name='desembolsarasignacion'),
    path('consultadesembolsos/',DesembolsosConsulta.as_view() \
        , name='consulta_desembolsos'),
    path('desembolsosjson/<desde>/<hasta>',GeneraListaDesembolsosJSON
        , name="desembolsos_json"),
        
    ]
