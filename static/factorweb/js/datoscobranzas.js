var $table = jQuery('#table')

window.onload=function(){

    inicializaValor("id_nvalor",capturaValor("total_cartera"))

    jQuery('#id_nvalor').change(function(){
        calcular_sobrepago();
    });

    jQuery('input[type=radio][name="pagadopor"]').change(function() {
      mostrar_cuentas_origen();
    });

    jQuery('input[type=radio][name="depositaren"]').change(function() {
      mostrar_cuentas_destino();
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
          , row.SaldoActual, row.Cobro, row.Retenido, row.Bajas)
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
          }, {title: 'Deudor', field: 'Comprador', rowspan: 2
          , align: 'center', valign: 'middle', sortable: true
          }, {title: 'Asignación', field: 'Asignacion'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Documento', field: 'Documento'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Vencimiento', field: 'Vencimiento'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Saldo actual', field: 'SaldoActual'
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
          }, {field: 'Retenido', title: 'Retenciones', sortable: true, align: 'right'
          ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }, {field: 'Bajas', title: 'Bajas', sortable: true, align: 'right'
            ,footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }]
      ]
      
    })

  }

function DatosCobro(index, asgn, doc, sdo, cobro, ret, bajas){
    AbrirModal('/cobranzas/datoscobro/'+index+'/'+asgn 
      +'/'+doc +'/'+sdo+'/'+cobro+'/'+ret+'/'+bajas )
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

function mostrar_cuentas_origen(){
// obtener el valor de radio button cliente
// si es on, esconder las cuentas del deudor, mostrar la del cliente
// si es off, esconder la cuentas del cliente, mostrar la del deudor
  const div_c = document.querySelector('#div_cuentas_cliente');
  const div_d = document.querySelector('#div_cuentas_deudor');

  let recibido_por = document.querySelector('input[name="pagadopor"]:checked');

  if (recibido_por.id == "porcliente"){
    div_d.setAttribute('hidden',true);
    div_c.removeAttribute('hidden');
    }
  else{
    div_d.removeAttribute('hidden');
    div_c.setAttribute('hidden',true);
  }
}

function mostrar_cuentas_destino(){
  const div_e = document.querySelector('#div_cuentas_empresa');
  const div_c = document.querySelector('#div_cuentas_conjuntas');

  let deposito_en = document.querySelector('input[name="depositaren"]:checked');

  if (deposito_en.id == "cuentacliente"){
    div_e.setAttribute('hidden',true);
    div_c.removeAttribute('hidden');
    }
  else{
    div_e.removeAttribute('hidden');
    div_c.setAttribute('hidden',true);
  }
}

function AceptarCobranza(){
  const recibido_por = document.querySelector('input[name="pagadopor"]:checked');
  const destino_deposito = document.querySelector('input[name="depositaren"]:checked');
  const forma_de_cobro = capturaValor("forma_cobro")
  const pagado_por_cliente =  (recibido_por.id == "porcliente")
  const deposito_cuenta_conjunta =  (destino_deposito.id == "cuentacliente")
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

  MensajeConfirmacion("Grabar cobranza del " + capturaValor("id_dcobranza") +"?"
    ,function(){

    var objeto={
      "id_cliente":capturaValor("id_cliente"),
      "tipo_factoring":capturaValor("tipo_factoring"),
      "forma_cobro":forma_de_cobro,
      "fecha_cobro":capturaValor("id_dcobranza"),
      "valor_recibido": capturaValor("id_nvalor"), 
      "pagador_por_cliente":pagado_por_cliente,
      "sobrepago":capturaValor("id_nsobrepago"), 
      "cuenta_bancaria": cuenta_bancaria,
      "arr_documentos_cobrados": JSONdocumentos,
      "arr_cheque": JSONcheque,
      "arr_deposito": JSONdeposito,
      "id_deudor":capturaValor("id_deudor"),
    }

    fetchPostear("/cobranzas/aceptarcobranza/", objeto, function(data){
        // regresar a la lista de solicitudes
        window.location.href = "/cobranzas/listadocumentosporvencer";
        // en una nueva ventana abrir el reporte de cobranza
        // hay que saber el id de la cobranza
         url = window.location.origin
         url = url + "/cobranzas/reportecobranzacartera/"+data;
         window.open( url);
      })
  })
     
}
 
