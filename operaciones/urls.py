from django.urls import URLPattern, path

from .views import  AnexosNew, AsignacionesView, DatosOperativosView, \
    DatosOperativos, AsignacionesConsulta, PagaresView,SumaCargos, \
    DetalleCargosAsignacion, GeneraResumenCarteraNegociadaJSON, \
    AceptarDocumentos,MaestroMovimientosView, AnexosEdit, \
    CondicionesOperativasView, DatosCondicionesOperativas,\
    DetalleCondicionOperativa, EliminarDetalleCondicionOperativa, \
    EditarTasasDocumentoSolicitud, DesembolsarAsignacion, \
    GeneraDetalleParaTabla1, AsignacionesPendientesDesembolsarView, \
    ReversaAceptacionAsignacion, GeneraListaAsignacionesJSON, \
    GeneraListaAsignacionesRegistradasJSON, EstadoOperativoCliente, \
    GeneraResumenAntigüedadCarteraJSON, EstadosOperativosView, \
    AntigüedadCarteraClienteJSON, GeneraListaCarteraClienteJSON, \
    GeneraListaChequesADepositarClienteJSON, AnexosView, PagareDatos,\
    GeneraListaCargosPendientesClienteJSON, MaestroMovimientoNew, \
    GeneraListaChequesQuitadosClienteJSON, MaestroMovimientoEdit, \
    GeneraListaProtestosPendientesClienteJSON, DesembolsosConsulta,\
    GeneraListaCanjesClienteJSON, CondicionesOperativasUpdate, \
    DatosCondicionOperativaNueva, GeneraListaDesembolsosJSON, \
    CondicionesOperativasInactivar, ConsultaAnexosActivos, \
    GenerarAnexo, MarcarAnexoGenerado, IngresosGeneradosJSON, \
    PedirArchivoXML, ImportarOperacion, ReversaAceptacionPagare, \
    AceptarAsignacion, ReversoDesembolsoAsignacion, \
    MaestroMovimientosView, GeneraListaCuotasPagareJSON, \
    ModificarCuota, GeneraResumenNegociadPorActividadJSON, \
    AnexosClienteView, GeneraListaMovimientosClienteJSON, \
    GeneraListaClientesValoresPendientes, NuevaRevisionCarteraJSON,\
    RevisionCartera, RevisionCarteraJSON, RevisionCarteraClienteEdit,\
    estadisticas_mes, CortesHistoricoView, CorteHistoricoEdit, \
    GuardarCorteHistorico, corteHistorico, GeneraListaCarteraClienteJSON,\
    GeneraResumenAntigüedadCarteraCorteJSON, AnexosCesionFacturasView,\
    GeneraResumenCarteraNegociadaClienteJSON, CarteraPorClienteConsulta, \
    GeneraListaCarteraDeudorJSON, CarteraPorDeudorConsulta, \
    RevisionCarteraDetalle
    
from .reportes import ImpresionAsignacion, ImpresionAntiguedadCartera, \
    ImpresionAsignacionDesdeSolicitud, ImpresionFacturasPendientes, \
    ImpresionPagare, ImpresionAccesoriosPendientes, \
    ImpresionResumenAsignaciones, ImpresionPagaresPendientes, \
    ImpresionLiquidacion, ImpresionRevisionCartera, \
    ImpresionAntiguedadCarteraCorte, ImpresionFacturasPendientesCorte,\
    ImpresionAccesoriosPendientesCorte, ImpresionAntiguedadCarteraPorDeudor,\
    ImpresionFacturasPendientesDeudores, ImpresionCarteraPendientePorCliente,\
    ImpresionCarteraPendientePorDeudor

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
    path('antigüedadcarteracliente/<cliente_id>'
         , AntigüedadCarteraClienteJSON),
    path('carteraclientejson/<cliente_id>/<fecha_corte>'
         ,GeneraListaCarteraClienteJSON, name="carteracliente_json"),
    path('chequesadepositarclientejson/<cliente_id>/<fecha_corte>'
         ,GeneraListaChequesADepositarClienteJSON
         , name="chequesadepositarcliente_json"),
    path('listacargospendientesclientejson/<cliente_id>',\
         GeneraListaCargosPendientesClienteJSON, name="listacargospendientescliente_json"),
    path('protestospendientesjson/<cliente_id>'
         ,GeneraListaProtestosPendientesClienteJSON, name="protestospendientescliente_json"),
    path('canjesclientejson/<cliente_id>',GeneraListaCanjesClienteJSON, 
        name="listacanjescliente_json"),
    path('chequesquitadosclientejson/<cliente_id>',GeneraListaChequesQuitadosClienteJSON, 
        name="listachequesquitadoscliente_json"),
    path('movimientosclientejson/<cliente_id>/<int:registros>',GeneraListaMovimientosClienteJSON,
        name='movimientoscliente_json'),
    path('carteranegociadacliente/<cliente_id>/<int:año>', GeneraResumenCarteraNegociadaClienteJSON),
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
    path('sumacargos/<int:asignacion_id>/<gao_carga_iva>/<dc_carga_iva>/<carga_gao>/<carga_dc>/<porcentaje_iva>',\
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
    path("reporteliquidacion/<int:solicitud_id>",ImpresionLiquidacion, 
        name='reporteliquidacion'),
    path("reporteliquidacion/<int:solicitud_id>/<crear_pdf>",ImpresionLiquidacion, 
        name='reporteliquidacion'),
    path("reporteasignaciondesdesolicitud/<int:asignacion_id>",
        ImpresionAsignacionDesdeSolicitud ),
    path('listaanexos/',AnexosView.as_view(), name='listaanexos'),
    path('nuevoanexo/',AnexosNew.as_view(), name='anexo_nuevo'),
    path('editaranexo/<int:pk>',AnexosEdit.as_view(), name='anexo_editar'),
    path('reversaraceptacionasignacion/<int:pid_asignacion>/<desde_desembolso>',ReversaAceptacionAsignacion
         , name='reversar_liquidacion_asignacion'),
    path('reversaraceptacionasignacion/<int:pid_asignacion>',ReversaAceptacionAsignacion
         , name='reversar_liquidacion_asignacion'),
    path('asignacionesjson/<desde>/<hasta>/<clientes>',GeneraListaAsignacionesJSON
         , name="asignaciones_json"),
    path('asignacionesjson/<desde>/<hasta>/',GeneraListaAsignacionesJSON
         , name="asignaciones_json"),
    path('asignacionesregistradasjson/<desde>/<hasta>',GeneraListaAsignacionesRegistradasJSON
        , name="asignacionesregistradas_json"),
    path('impresionchequespendientes/', ImpresionAccesoriosPendientes
         , name='detalle_cheques_pendientes'),
    path('impresionchequespendientes/<id_cliente>', ImpresionAccesoriosPendientes
         , name='detalle_cheques_pendientes'),
    path('impresionresumenasignaciones/<desde>/<hasta>/<clientes>'
         , ImpresionResumenAsignaciones, name='resumen_asignaciones'),
    path('impresionresumenasignaciones/<desde>/<hasta>/'
         , ImpresionResumenAsignaciones, name='resumen_asignaciones'),
#  anexos
    path("anexosactivos/<tipo_cliente>", ConsultaAnexosActivos),
    path('anexoscliente/<cliente_id>/<solicitud_id>'
         , AnexosClienteView.as_view(), name='anexos_cliente'),
    path('anexoscesioncliente/<solicitud_id>/<anexo_id>'
         , AnexosCesionFacturasView.as_view(), name='anexos_cesion_cliente'),
    path("generaranexo/<int:asignacion_id>/<anexo_id>"
         , GenerarAnexo, name='generar_anexo'),
    path("generaranexo/<int:asignacion_id>/<anexo_id>/<deudor_id>"
         , GenerarAnexo, name='generar_anexo_cesion'),
    path('marcaanexogenerado/<int:asignacion_id>', MarcarAnexoGenerado),
# dashboard
    path('antigüedadcartera', GeneraResumenAntigüedadCarteraJSON),
    path('carteranegociada/<int:año>', GeneraResumenCarteraNegociadaJSON),
    path('ingresosgenerados/<int:año>', IngresosGeneradosJSON),
    path('impresioncartera', ImpresionAntiguedadCartera
         , name='antigüedad_por_cliente'),
    path('negociadoporactividad', GeneraResumenNegociadPorActividadJSON),
    path('clientesvalorespendientes/<int:porcentaje>', GeneraListaClientesValoresPendientes),
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
    path("reportepagare/<int:pagare_id>",ImpresionPagare
         , name='reporte_pagare'),
    path('impresionpagarespendientes/<clientes>', ImpresionPagaresPendientes
         , name='detalle_pagares_pendientes'),
    path('editarpagare/<int:pk>', PagareDatos.as_view()
         , name='pagare_editar'),
    path('detallepagarejson/<pagare_id>', GeneraListaCuotasPagareJSON
         , name="detallepagare_json"),
    path('editarcuota/<int:cuota_id>', ModificarCuota
         , name='modificar_cuota'),
# cartera
    path('revisioncartera/',RevisionCartera.as_view()
         , name='revision_cartera'),
    path('nuevarevisioncarterajson/',NuevaRevisionCarteraJSON
         , name='nueva_revision_cartera_json'),
    path('revisioncarterajson/<int:pk>',RevisionCarteraJSON
         , name='revision_cartera_json'),
    path('revisioncarteracliente/<int:pk>/<int:revision>/<cliente>'
         ,RevisionCarteraClienteEdit.as_view()
         , name='revision_cartera_cliente'),
    path('impresionrevisioncartera/<int:revision_id>',ImpresionRevisionCartera
         , name='impresion_revision_cartera'),
    path('negociaciones/', estadisticas_mes
         , name='negociaciones_mes'),
    path('negociaciones/<int:año>/<int:mes>/', estadisticas_mes
         , name='negociaciones_mes'),
    path('listacorteshistorico',CortesHistoricoView.as_view(), \
        name='lista_corteshistorico'),
    path('editarcortehistorico/<int:pk>', CorteHistoricoEdit.as_view(), \
        name='cortehistorico_editar'),
    path('guardarcorteshistorico', GuardarCorteHistorico, ),\
    path('cortehistorico/<int:corte_id>', corteHistorico
         , name='corte_historico'),
    path('antigüedadcarteracorte/<int:corte_id>'
         , GeneraResumenAntigüedadCarteraCorteJSON),
    path('impresionantigüedadcarteracorte/<int:corte_id>'
         , ImpresionAntiguedadCarteraCorte
         , name='antigüedad_por_cliente_corte'),
    path('impresioncarterapendientecorte/<int:corte_id>'
         , ImpresionFacturasPendientesCorte
         , name='detalle_facturas_pendientes_corte'),
    path('impresionchequespendientescorte/<int:corte_id>'
         , ImpresionAccesoriosPendientesCorte
         , name='detalle_cheques_pendientes_corte'),
    path('impresioncarterapordeudor/<id_cliente>/<cliente>', ImpresionAntiguedadCarteraPorDeudor
         , name='antigüedad_por_deudor'),
    path('consultacarteraporcliente', CarteraPorClienteConsulta.as_view()
         , name='consulta_cartera_por_cliente'),
    path('carteraclientesjson/<clientes>',GeneraListaCarteraClienteJSON
        , name="carteraclientes_json"),
    path('carteraclientesjson/',GeneraListaCarteraClienteJSON
        , name="carteraclientes_json"),
    path('consultacarterapordeudor', CarteraPorDeudorConsulta.as_view()
         , name='consulta_cartera_por_deudor'),
    path('carteradeudoresjson/',GeneraListaCarteraDeudorJSON
        , name="carteradeudores_json"),
    path('carteradeudoresjson/<deudores>',GeneraListaCarteraDeudorJSON
        , name="carteradeudores_json"),
    path('impresioncarterapendienteclientes/<clientes>', ImpresionFacturasPendientes
         , name='detalle_facturas_pendientes'),
    path('impresioncarterapendienteclientes/', ImpresionFacturasPendientes
         , name='detalle_facturas_pendientes'),
    path('impresioncarterapendientedeudores/<deudores>', ImpresionFacturasPendientesDeudores
         , name='detalle_facturas_pendientes_deudores'),
    path('impresioncarterapendientedeudores/', ImpresionFacturasPendientesDeudores
         , name='detalle_facturas_pendientes_deudores'),
    path('reportecarterapendienteclientes/<clientes>', ImpresionCarteraPendientePorCliente
         , name='detalle_cartera_pendiente'),
    path('reportecarterapendienteclientes/', ImpresionCarteraPendientePorCliente
         , name='detalle_cartera_pendiente'),
    path('reportecarterapendientedeudores/<deudores>', ImpresionCarteraPendientePorDeudor
         , name='detalle_cartera_pendiente_deudores'),
    path('reportecarterapendientedeudores/', ImpresionCarteraPendientePorDeudor
         , name='detalle_cartera_pendiente_deudores'),
    path('obtenerdetallerevisioncarteracliente/<int:cliente_id>/<int:revision_id>', RevisionCarteraDetalle
         , name='obtener_detalle_revision_cartera_cliente'),
]
