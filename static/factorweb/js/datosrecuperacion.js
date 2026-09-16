window.operateEvents = {
    'click .cobrar': function (e, value, row, index) {
        DatosCobro( row.id, row.Asignacion, row.Documento
          , row.SaldoActual, row.Cobro, row.Bajas)
    }
  };
  
function DatosCobro(index, asgn, doc, sdo, cobro, bajas){
    AbrirModal('/cobranzas/datosrecuperacion/'+index+'/'+asgn 
      +'/'+doc +'/'+sdo+'/'+cobro+'/'+bajas )
  }

function initTable() {
    $table.bootstrapTable('destroy').bootstrapTable({
      locale: "es-EC",
        footerStyle: function() {
            return {
                css: {
                    'background-color': '#f8f9fa',
                    'color': '#000000',
                    'border-top': '2px solid #dee2e6',
                    'font-weight': 'bold'
                }
            }
        },
      columns: [
        [{  title: 'Ref.', field: 'id', rowspan: 2
        , align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Deudor', field: 'Comprador', rowspan: 2
          , align: 'center', valign: 'middle', sortable: true
          }, {title: 'Asignación', field: 'Asignacion'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Documento', field: 'Documento'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Saldo actual', field: 'SaldoActual',formatter: numberFormatter
          , rowspan: 2, align: 'right', valign: 'middle', sortable: true,
          }, {title: 'Baja de cobranza', field: 'BajaCobranza'
          , rowspan: 2, align: 'right', valign: 'middle', sortable: true,
          }, {title: 'Valores cobrados', colspan: 3, align: 'center',
          }, {title: 'Saldo', field: 'SaldoFinal',rowspan: 2, align: 'center'
            ,formatter: numberFormatter
          }, {field: 'operate', title: 'Acción',rowspan: 2
          , align: 'center', clickToSelect: false, 
          events: window.operateEvents, formatter: operateFormatter
          }],
        [
          {field: 'Cobro', title: 'Recibido', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla,formatter: numberFormatter
        }, {field: 'BajaCobranza', title: 'Bajas de cobranza', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla,formatter: numberFormatter
        }, {field: 'Bajas', title: 'Otras bajas', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla,formatter: numberFormatter
        }]
      ]
      
    })

  }

function AceptarCobranza(){
  const recibido_por = document.querySelector('input[name="pagadopor"]:checked');
  const destino_deposito = document.querySelector('input[name="depositaren"]:checked');
  // const forma_de_cobro = capturaValor("forma_cobro")
  const pagado_por_cliente = recibido_por != null
  const deposito_cuenta_conjunta =  destino_deposito != null
  var cuenta_bancaria = null 

  mp_deposito = new Map()
  mp_cheque = new Map()

  if (forma_de_cobro !='MOV'){
    mp_deposito.set("deposito_cuenta_conjunta",deposito_cuenta_conjunta);    
    mp_deposito.set("cuenta_deposito",capturaValor("id_cxcuentadeposito"));    
    mp_deposito.set("fecha_deposito",capturaValor("id_ddeposito"));    
    mp_deposito.set("cuenta_conjunta",capturaValor("cuenta_conjunta"));    
  }

  if (forma_de_cobro =="CHE"){
    mp_cheque.set("numero_cheque", capturaValor("id_ctcheque"));
    mp_cheque.set("girador", capturaValor("id_ctgirador"));
  }

  var JSONcheque = JSON.stringify(Object.fromEntries(mp_cheque));
  var JSONdeposito = JSON.stringify(Object.fromEntries(mp_deposito));
  var JSONdocumentos= JSON.stringify($table.bootstrapTable('getData'));

  if (forma_de_cobro =='CHE' | forma_de_cobro =='TRA'){
    if (pagado_por_cliente){cuenta_bancaria = capturaValor("cuenta_cliente")}
    else {cuenta_bancaria = capturaValor("cuenta_deudor")}
  }

  MensajeConfirmacion("Grabar recuperación del " + capturaValor("id_dcobranza") +"?"
    ,function(){

    var objeto={
      "id_cliente": id_cliente,
      "tipo_factoring":tipo_factoring,
      "forma_cobro":forma_de_cobro,
      "fecha_cobro":capturaValor("id_dcobranza"),
      "valor_recibido": capturaValor("id_nvalor"), 
      // "sobrepago":capturaValor("id_nsobrepago"), 
      "sobrepago":document.getElementById('divSobrepago').innerText, 
      "cuenta_bancaria": cuenta_bancaria,
      "arr_documentos_cobrados": JSONdocumentos,
      "arr_cheque": JSONcheque,
      "arr_deposito": JSONdeposito,
      "pagador_por_cliente":pagado_por_cliente,
      "id_deudor":id_deudor,
      "comentario": capturaValor("id_ctcomentario"),
    }
    fetchPostear("/cobranzas/aceptarrecuperacion/", objeto, function(data){
        // en una nueva ventana abrir el reporte de cobranza
        // hay que saber el id de la cobranza
         url = window.location.origin
         url = url + "/cobranzas/reporterecuperacion/"+data;
         window.open( url);
        // regresar a la lista de solicitudes
        window.location.href = "/cobranzas/listaprotestospendientes";
      })
  })
     
}
 
