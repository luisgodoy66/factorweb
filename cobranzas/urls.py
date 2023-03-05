from django.urls import URLPattern, path
from .views import CobranzasDocumentosView, DetalleDocumentosFacturasPuras\
    , DocumentosPorVencerView, GeneraListaCarteraPorVencerJSON, DatosCobro\
    , AceptarCobranza, ChequesADepositarView, GeneraListaChequesADepositarJSON\
    , DepositoCheques, GeneraListaCobranzasJSON, CobranzasConsulta\
    , CobranzasPorConfirmarView, ConfirmarCobranza, CobranzasPendientesLiquidarView\
    , CobranzaPorCondonar, DetalleDocumentosCobrados, DatosDiasACondonar\
    , ReversaConfirmacionCobranza, GeneraListaCobranzasPendientesProcesarJSON\
    , LiquidarCobranzas, Liquidacion, LiquidacionesPendientesPagarView\
    , DesembolsarCobranzas, MotivosProtestoView, MotivoProtestoNew\
    , MotivoProtestoEdit, ProtestoCobranzaNew, AceptarProtesto, DocumentosVencidosView\
    , ProtestosPendientesView, GeneraListaProtestosPendientesJSON\
    , RecuperacionProtestoView, DetalleDocumentosProtesosJSON, DatosRecuperacion\
    , AceptarRecuperacion, ProtestoRecuperacionNew, ReversaLiquidacion\
    , ReversaCobranza, GeneraListaCobranzasRegistradasJSON, CobranzasCargosView\
    , LiquidacionesEnNegativoPendientesView, GeneraListaLiquidacionesEnNegativoPendientesJSON\
    , DetalleNotasDebitoPendientesJSON, DatosCobroNotaDebito, AceptarCobranzaNotasDebito\
    , GeneraListaLiquidacionesRegistradasJSON, GeneraListaCobranzasCargosRegistradasJSON\
    , ReversaProtesto, CanjeDeCheque

from .reportes import ImpresionCobranzaCartera, ImpresionLiquidacion\
    , ImpresionRecuperacionProtesto, ImpresionCobranzaCargos, ImpresionProtestosPendientes

urlpatterns = [
    # cobranzas
    path('listadocumentosvencidos/',DocumentosVencidosView.as_view(), 
        name="listadocumentosvencidos"),
    path('listadocumentosporvencer/',DocumentosPorVencerView.as_view(), 
        name="listadocumentosporvencer"),
    path('listachequesadepositar/',ChequesADepositarView.as_view(), 
        name="listachequesadepositar"),
    path('listacobranzasporconfirmar/',CobranzasPorConfirmarView.as_view(), 
        name="listacobranzasporconfirmar"),
    path('carteraporvencerjson/<fecha_corte>',GeneraListaCarteraPorVencerJSON, 
        name="carteraporvencer_json"),
    path('chequesadepositarjson/<fecha_corte>',GeneraListaChequesADepositarJSON, 
        name="chequesadepositar_json"),
    path('cobrodedocumentos/<ids_documentos>/<total_cartera>/<forma_cobro>'\
         '/<cliente_ruc>/<un_comprador>/<deudor_id>/<tipo_factoring>/<por_vencer>', 
        CobranzasDocumentosView.as_view(), name='cobro_documentos'),
    path('depositodecheques/<ids_cheques>/<total_cartera>/<cuenta_destino>/<id_cliente>', 
        DepositoCheques, name='deposito_cheques'),
    path('detalledocumentos/<ids_documentos>', DetalleDocumentosFacturasPuras
        , name='detalle_documentos'),
    path('datoscobro/<int:id>/<asgn>/<doc>/<sdo>/<cobro>/<retenido>/<baja>'
        , DatosCobro ,name='datos_cobro'),
    path('aceptarcobranza/',AceptarCobranza),
    path('reportecobranzacartera/<int:cobranza_id>',ImpresionCobranzaCartera
        , name='reporte_cobranza_cartera'),
    path('consultacobranzas/',CobranzasConsulta.as_view() \
        , name='consulta_cobranzas'),
    path('cobranzasjson/<desde>/<hasta>',GeneraListaCobranzasJSON
        , name="cobranzas_json"),
    path('cobranzasregistradasjson/<desde>/<hasta>',GeneraListaCobranzasRegistradasJSON
        , name="cobranzasregistradas_json"),
    path('reversarcobranza/<int:pid_cobranza>/<tipo_operacion>',ReversaCobranza),
    path('canjearchequeaccesorio/<int:cheque_id>/<cliente_ruc>/<deudor_id>'
         , CanjeDeCheque, name='canjearchequeaccesorio'),
    
    # liquidaciones
    path('confirmarcobranza/<int:cobranza_id>/<tipo_operacion>',ConfirmarCobranza),
    path('reversaconfirmacioncobranza/<int:cobranza_id>/<tipo_operacion>'
        ,ReversaConfirmacionCobranza),
    path('listacobranzaspendientesliquidar/',CobranzasPendientesLiquidarView.as_view()
        , name="listacobranzaspendientesliquidar"),
    path('listaliquidacionespendientespagar/',LiquidacionesPendientesPagarView.as_view()
        , name="listaliquidacionespendientespagar"),
    path('listacobranzaspendientesliquidarjson/',GeneraListaCobranzasPendientesProcesarJSON\
        , name="listacobranzaspendientesliquidar_json"),
    path('cobranzaporcondonar/<int:pk>/<tipo_operacion>',CobranzaPorCondonar
        , name="cobranzaporcondonar"),
    path('detalledocumentoscobrados/<int:cobranza_id>/<tipo_operacion>',DetalleDocumentosCobrados
        , name="detalledocumentoscobrados"),
    path('datosdiascondonar/<int:id>/<int:dias>/<int:cobranza_id>/<tipo_operacion>'
        ,DatosDiasACondonar, name="datos_diascondonar"),
    path('liquidarcobranzas/<ids_cobranzas>/<tipo_operacion>/', LiquidarCobranzas),
    path('liquidacion/<tipo_operacion>', Liquidacion),
    path('desembolsarliquidaciones/<int:pk>/<cliente_ruc>',DesembolsarCobranzas, \
        name='desembolsarliquidacion'),
    path('reporteliquidacion/<int:liquidacion_id>',ImpresionLiquidacion
        , name='reporte_liquidacion'),
    path('reversarliquidacion/<int:pid_liquidacion>/',ReversaLiquidacion),
    path('liquidacionesregistradasjson/<desde>/<hasta>',GeneraListaLiquidacionesRegistradasJSON
        , name="liquidacionesregistradas_json"),

    # protestos
    path('listamotivosprotesto/',MotivosProtestoView.as_view()
        , name="listamotivosprotesto"),
    path('motivoprotestonuevo/', MotivoProtestoNew.as_view()
        , name='motivoprotesto_nuevo'),
    path('motivoprotestoeditar/<int:pk>', MotivoProtestoEdit.as_view()
        , name='motivoprotesto_editar'),
    path('protestocobranza/<int:id_cheque>/<int:id_cobranza>/<lista_deposito>'
        ,ProtestoCobranzaNew.as_view(), name='protestocobranza'),
    path('aceptarprotesto/',AceptarProtesto),
    path('listaprotestospendientes/',ProtestosPendientesView.as_view(), 
        name="listaprotestospendientes"),
    path('protestospendientesjson/',GeneraListaProtestosPendientesJSON, 
        name="protestospendientes_json"),
    path('recuperaciondeprotesto/<ids_protestos>/<total_cartera>/<forma_cobro>/<cliente_ruc>/<un_comprador>/<deudor_id>/<tipo_factoring>', 
        RecuperacionProtestoView.as_view(), name='recuperacion_protesto'),
    path('detalledocumentosprotestosjson/<ids_protestos>', DetalleDocumentosProtesosJSON
        , name='detalle_documentos_protestos'),
    path('datosrecuperacion/<int:id>/<asgn>/<doc>/<sdo>/<cobro>/<baja>'
        , DatosRecuperacion ,name='datos_recuperacion'),
    path('aceptarrecuperacion/',AceptarRecuperacion),
    path('reporterecuperacion/<int:cobranza_id>',ImpresionRecuperacionProtesto
        , name='reporte_recuperacion_protesto'),
    path('protestorecuperacion/<int:id_cheque>/<int:id_cobranza>/<lista_deposito>'
        ,ProtestoRecuperacionNew.as_view(), name='protestorecuperacion'),
    path('reversaprotesto/<int:id_cobranza>/<tipo_operacion>/<int:id_protesto>/<cobranza>/<cliente_id>/<factoring_id>'
         ,ReversaProtesto),
    path('impresionprotestos', ImpresionProtestosPendientes, name='protestos_pendientes'),

    # notas de debito
    path('listaliquidacionesennegativopendientes/',LiquidacionesEnNegativoPendientesView.as_view()
        , name="listaliquidacionesennegativopendientes"),
    path('listaliquidacionesennegativopendientesjson/',GeneraListaLiquidacionesEnNegativoPendientesJSON\
        , name="listaliquidacionesennegativopendientes_json"),
    path('cobrodecargos/<ids_documentos>/<total_cargos>/<forma_cobro>/<cliente_ruc>/<tipo_factoring>', 
        CobranzasCargosView.as_view(), name='cobro_cargos'),
    path('detallenotasdebitojson/<ids_documentos>', DetalleNotasDebitoPendientesJSON
        , name='detallenotasdebito_json'),
    path('datoscobronotadedebito/<int:id>/<sdo>/<cobro>'
        , DatosCobroNotaDebito ,name='datosnotasdebito_cobro'),
    path('aceptarcobranzanotasdebito/',AceptarCobranzaNotasDebito),
    path('reportecobranzacargos/<int:cobranza_id>',ImpresionCobranzaCargos
        , name='reporte_cobranza_cargos'),
    path('cobranzascargosregistradasjson/<desde>/<hasta>',GeneraListaCobranzasCargosRegistradasJSON
        , name="cobranzascargosregistradas_json"),
]