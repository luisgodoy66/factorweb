var $table = jQuery('#table')
const tipo_deuda = capturaValor("tipo_deuda")

window.onload=function(){
    inicializaValor("id_nvalor",capturaValor("total_cargos"))

    jQuery('#id_nvalor').change(function(){
        calcular_sobrepago();
    });

    $table.bootstrapTable({locale:"es-EC"});

    // inicializar tabla
    initTable();

};

window.operateEvents = {
    'click .cobrar': function (e, value, row, index) {
        DatosCobro( row.id, row.SaldoActual, row.Cobro)
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
      height: 300,
      locale: "es-EC",
      columns: [
        [{  title: 'Ref.', field: 'id', rowspan: 2
        , align: 'center', valign: 'middle', sortable: true,
          }, {title: 'ND', field: 'ND'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Emisión', field: 'Emision'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
        }, {title: 'Operación', field: 'Operacion'
        , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
        }, {title: 'Saldo actual', field: 'SaldoActual'
          , rowspan: 2, align: 'right', valign: 'middle', sortable: true,
          }, {field: 'Cobro', title: 'Recibido', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }, {title: 'Saldo', field: 'SaldoFinal',rowspan: 2, align: 'center'
          }, {field: 'operate', title: 'Acción',rowspan: 2
          , align: 'center', clickToSelect: false, 
          events: window.operateEvents, formatter: operateFormatter
          }],
        [
    ]
      ]
      
    })

  }

function DatosCobro(index, sdo, cobro){
  
    AbrirModal('/cobranzas/datoscobronotadedebito/'+index+'/'+sdo+'/'+cobro )

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

  var JSONcheque = JSON.stringify(Object.fromEntries(mp_cheque));
  var JSONdeposito = JSON.stringify(Object.fromEntries(mp_deposito));
  var JSONdocumentos= JSON.stringify($table.bootstrapTable('getData'));

  if (forma_de_cobro =='CHE' | forma_de_cobro =='TRA'){

    cuenta_bancaria = capturaValor("cuenta_cliente")
  }

  MensajeConfirmacion("Grabar cobranza del " + capturaValor("id_dcobranza") +"?"
    ,function(){

    var objeto={
      "id_cliente":capturaValor("id_cliente"),
      "tipo_factoring":capturaValor("tipo_factoring"),
      "forma_cobro":forma_de_cobro,
      "fecha_cobro":capturaValor("id_dcobranza"),
      "valor_recibido": capturaValor("id_nvalor"), 
      "sobrepago":capturaValor("id_nsobrepago"), 
      "cuenta_bancaria": cuenta_bancaria,
      "arr_documentos_cobrados": JSONdocumentos,
      "arr_cheque": JSONcheque,
      "arr_deposito": JSONdeposito,
      "tipo_deuda":tipo_deuda,
    }

    fetchPostear("/cobranzas/aceptarcobranzanotasdebito/", objeto, function(data){
        // // regresar a la lista de NOTAS DE DEBITO o AMPLIACIONES
        if (capturaValor("tipo_deuda") == 'ND'){
          window.location.href = "/cobranzas/listaliquidacionesennegativopendientes";
        }
        else{
          window.location.href = "/cobranzas/listafacturaspendientespagar";
        }


        // en una nueva ventana abrir el reporte de cobranza
        // hay que saber el id de la cobranza
         url = window.location.origin
         url = url + "/cobranzas/reportecobranzacargos/"+data;
         window.open( url);
      })
  })
     
}
 
