var $table = jQuery('#table')

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();
    
    objeto_fechas("#id_dcobranza")
    objeto_fechas("#id_ddeposito")

    inicializaValor("id_nvalor",capturaValor("total_cartera"))

    jQuery('#id_nvalor').change(function(){
        calcular_sobrepago();
    });

    $table.bootstrapTable({locale:"es-EC"});

    // inicializar tabla
    initTable();


    // // cerrar side bar
    // CerrarSideBar();
  
};

window.operateEvents = {
    'click .cobrar': function (e, value, row, index) {
        DatosCobro( row.id, row.Asignacion, row.Documento
          , row.SaldoActual, row.Cobro, row.Bajas)
    }
  };
  
function operateFormatter(value, row, index) {
    return [
        '<a class="cobrar" href="javascript:void(0)" title="Cobro">',
        '<i class="fa fa-edit"></i>',
        '</a>'
    ].join('')
    }

function initTable() {
    $table.bootstrapTable('destroy').bootstrapTable({
      locale: "es-EC",
      columns: [
        [{  title: 'Ref.', field: 'id', rowspan: 2
        , align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Comprador', field: 'Comprador', rowspan: 2
          , align: 'center', valign: 'middle', sortable: true
          }, {title: 'Asignación', field: 'Asignacion'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Documento', field: 'Documento'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Saldo actual', field: 'SaldoActual'
          , rowspan: 2, align: 'right', valign: 'middle', sortable: true,
          }, {title: 'Baja de cobranza', field: 'BajaCobranza'
          , rowspan: 2, align: 'right', valign: 'middle', sortable: true,
          }, {title: 'Valores cobrados', colspan: 3, align: 'center',
          }, {title: 'Saldo', field: 'SaldoFinal',rowspan: 2, align: 'center'
          }, {field: 'operate', title: 'Acción',rowspan: 2
          , align: 'center', clickToSelect: false, 
          events: window.operateEvents, formatter: operateFormatter
          }],
        [
          {field: 'Cobro', title: 'Recibido', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }, {field: 'BajaCobranza', title: 'Bajas de cobranza', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }, {field: 'Bajas', title: 'Otras bajas', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }]
      ]
      
    })

  }

function DatosCobro(index, asgn, doc, sdo, cobro, bajas){
    AbrirModal('/cobranzas/datosrecuperacion/'+index+'/'+asgn 
      +'/'+doc +'/'+sdo+'/'+cobro+'/'+bajas )
  }

function calcular_sobrepago(){
  var seleccion=  $table.bootstrapTable('getData')
  
  const total_cobrado = seleccion.map(function(row) {
      return +row.Cobro.substring(0);
      }).reduce(function (sum, i) {
          return Math.round((sum + i + Number.EPSILON) * 100) / 100;
          }, 0)
          
  var sobrepago = capturaValor('id_nvalor') - total_cobrado

  inicializaValor('id_nsobrepago',sobrepago);

}

function AceptarCobranza(){
  const forma_de_cobro = capturaValor("forma_cobro")
  var cuenta_bancaria = null 

  mp_deposito = new Map()
  mp_cheque = new Map()

  if (forma_de_cobro !='MOV'){
    mp_deposito.set("cuenta_deposito",capturaValor("id_cxcuentadeposito"));    
    mp_deposito.set("fecha_deposito",capturaValor("id_ddeposito"));    
  }

  if (forma_de_cobro =="CHE"){
    mp_cheque.set("numero_cheque", capturaValor("id_ctcheque"));
    mp_cheque.set("girador", capturaValor("id_ctgirador"));
  }

  var JSONdocumentos= JSON.stringify($table.bootstrapTable('getData'));
  var JSONcheque = JSON.stringify(Object.fromEntries(mp_cheque));
  var JSONdeposito = JSON.stringify(Object.fromEntries(mp_deposito));

  if (forma_de_cobro =='CHE' | forma_de_cobro =='TRA'){
    cuenta_bancaria = capturaValor("cuenta_cliente")
  }

  MensajeConfirmacion("Grabar recuperación del " + capturaValor("id_dcobranza") +"?"
    ,function(){

    var objeto={
      "id_cliente":capturaValor("id_cliente"),
      "tipo_factoring":capturaValor("tipo_factoring"),
      "forma_cobro":forma_de_cobro,
      "fecha_cobro":capturaValor("id_dcobranza"),
      "valor_recibido": capturaValor("id_nvalor"), 
      "modalidad_factoring":capturaValor("modalidad_factoring"), 
      "sobrepago":capturaValor("id_nsobrepago"), 
      "cuenta_bancaria": cuenta_bancaria,
      "arr_documentos_cobrados": JSONdocumentos,
      "arr_cheque": JSONcheque,
      "arr_deposito": JSONdeposito,
    }

    fetchPostear("/cobranzas/aceptarrecuperacion/", objeto, function(data){
        // regresar a la lista de solicitudes
        window.location.href = "/cobranzas/listaprotestospendientes";
        // en una nueva ventana abrir el reporte de cobranza
        // hay que saber el id de la cobranza
         url = window.location.origin
         url = url + "/cobranzas/reporterecuperacion/"+data;
         window.open( url);
      })
  })
     
}
 
