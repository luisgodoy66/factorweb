from django.urls import URLPattern, path

from .views import  AnexosNew, AsignacionesView, DatosOperativosView, \
    DatosOperativos, AsignacionesConsulta, PagaresView,\
    AceptarAsignacion, DetalleCargosAsignacion, MaestroMovimientosView, \
    SumaCargos, AceptarDocumentos,MaestroMovimientosView, MaestroMovimientoNew, \
    MaestroMovimientoEdit, CondicionesOperativasView, DatosCondicionesOperativas,\
    DetalleCondicionOperativa, EliminarDetalleCondicionOperativa, AnexosView, \
    EditarTasasDocumentoSolicitud, GeneraDetalleParaTabla1, AnexosEdit,\
    AsignacionesPendientesDesembolsarView, DesembolsarAsignacion, \
    ReversaAceptacionAsignacion, GeneraListaAsignacionesJSON, \
    GeneraListaAsignacionesRegistradasJSON, GeneraResumenAntigüedadCarteraJSON,\
    EstadosOperativosView, EstadoOperativoCliente, AntigüedadCarteraClienteJSON,\
    GeneraListaCarteraClienteJSON, GeneraListaChequesADepositarClienteJSON,\
    GeneraListaCargosPendientesClienteJSON, GeneraListaChequesQuitadosClienteJSON,\
    GeneraListaProtestosPendientesClienteJSON, GeneraListaCanjesClienteJSON,\
    CondicionesOperativasUpdate, DatosCondicionOperativaNueva, DesembolsosConsulta,\
    GeneraListaDesembolsosJSON, CondicionesOperativasInactivar,\
    ConsultaAnexosActivos, GenerarAnexo, GeneraResumenCarteraNegociadaJSON, \
    MarcarAnexoGenerado, IngresosGeneradosJSON, PedirArchivoXML, ImportarOperacion,\
    ReversaAceptacionPagare, ReversoDesembolsoAsignacion


from .reportes import ImpresionAsignacion, ImpresionAsignacionDesdeSolicitud,\
    ImpresionAntiguedadCartera, ImpresionFacturasPendientes, ImpresionPagare,\
    ImpresionAccesoriosPendientes, ImpresionResumenAsignaciones, ImpresionPagaresPendientes

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
    path('estadocondicionoperativa/<int:id>', CondicionesOperativasInactivar, \
         name='condicionesoerativas_estado'),
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
    # path("generaranexos/<int:asignacion_id>", GenerarAnexos, name="generaranexos"),
    path('listaanexos/',AnexosView.as_view(), name='listaanexos'),
    path('nuevoanexo/',AnexosNew.as_view(), name='anexo_nuevo'),
    path('editaranexo/<int:pk>',AnexosEdit.as_view(), name='anexo_editar'),
    path('reversaraceptacionasignacion/<int:pid_asignacion>',ReversaAceptacionAsignacion),
    path('asignacionesjson/<desde>/<hasta>/<clientes>',GeneraListaAsignacionesJSON
         , name="asignaciones_json"),
    path('asignacionesjson/<desde>/<hasta>/',GeneraListaAsignacionesJSON
         , name="asignaciones_json"),
    path('asignacionesregistradasjson/<desde>/<hasta>',GeneraListaAsignacionesRegistradasJSON
        , name="asignacionesregistradas_json"),
    path('impresioncarterapendiente/<clientes>', ImpresionFacturasPendientes
         , name='detalle_facturas_pendientes'),
    path('impresioncarterapendiente/', ImpresionFacturasPendientes
         , name='detalle_facturas_pendientes'),
    path('impresionchequespendientes/', ImpresionAccesoriosPendientes
         , name='detalle_cheques_pendientes'),
    path('impresionchequespendientes/<id_cliente>', ImpresionAccesoriosPendientes
         , name='detalle_cheques_pendientes'),
    path('impresionresumenasignaciones/<desde>/<hasta>/<clientes>'
         , ImpresionResumenAsignaciones, name='resumen_asignaciones'),
    path('impresionresumenasignaciones/<desde>/<hasta>/', ImpresionResumenAsignaciones
         , name='resumen_asignaciones'),
    path("anexosactivos/<tipo_cliente>", ConsultaAnexosActivos),
    path("generaranexo/<int:asignacion_id>/<anexo_id>", GenerarAnexo),
    path('marcaanexogenerado/<int:asignacion_id>', MarcarAnexoGenerado),
# dashboard
    path('antigüedadcartera', GeneraResumenAntigüedadCarteraJSON),
    path('carteranegociada/<int:año>', GeneraResumenCarteraNegociadaJSON),
    path('ingresosgenerados/<int:año>', IngresosGeneradosJSON),
    path('impresioncartera', ImpresionAntiguedadCartera
         , name='antigüedad_por_cliente'),
# desembolsos
    path('listaasignacionespendientesdesembolsar/',AsignacionesPendientesDesembolsarView.as_view(), \
        name='listaasignacionespendientesdesembolsar'),
    path('desembolsarasignaciones/<int:pk>/<cliente_id>',DesembolsarAsignacion, \
        name='desembolsarasignacion'),
    path('consultadesembolsos/',DesembolsosConsulta.as_view() \
        , name='consulta_desembolsos'),
    path('desembolsosjson/<desde>/<hasta>',GeneraListaDesembolsosJSON
        , name="desembolsos_json"),
    path('reversardesembolsoasignacion/<int:desembolso_id>'
         ,ReversoDesembolsoAsignacion,),
# pagares
    path('pagares/',PagaresView.as_view(), name="listapagares"),
    path('reversaraceptacionpagare/<int:pid_asignacion>',ReversaAceptacionPagare),
    path('importarxml',PedirArchivoXML, name='importar_xml'),
    path('importaroperacion',ImportarOperacion, name='importar_xml_pagare'),
    path("reportepagare/<int:pagare_id>",ImpresionPagare, 
        name='reporte_pagare'),
    path('impresionpagarespendientes/<clientes>', ImpresionPagaresPendientes
         , name='detalle_pagares_pendientes'),
]
