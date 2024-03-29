var $btnFiltrar = jQuery("#btnFiltrar")
var $table = jQuery('#table')
var selections = []
var $deposito_empresa = jQuery("#deposito")
var $deposito_cliente = jQuery("#deposito_cc")
var $ampliar_plazo = jQuery("#ampliarplazo")

window.onload=function(){
    $table.bootstrapTable({locale:"es-EC"});
    
    // boton de refrescar filtro
    $btnFiltrar.click(function () {

        fecha = capturaValor("fechacorte");

        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/cobranzas/chequesadepositarjson/" + fecha
        })
    })

    // evento de marcar y desmarcar documentos
    $table.on('check.bs.table uncheck.bs.table ' +
      'check-all.bs.table uncheck-all.bs.table',
        function () {
        $deposito_empresa.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $deposito_cliente.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $ampliar_plazo.prop('disabled', !$table.bootstrapTable('getSelections').length)

        // save your data, here just save the current page
        selections = getIdSelections()
        // push or splice the selections if you want to save all data selections
        }
    )

    $table.on('all.bs.table', function (e, name, args) {
      console.log(name, args)
    })

    // acciones ejecutada sobre registros seleccionados
    $deposito_empresa.click(function () {
      DepositoDeCheques();
      $deposito_empresa.prop('disabled', true)
    })

    $deposito_cliente.click(function () {
      DepositoCuentaCliente();
      $deposito_cliente.prop('disabled', true)
    })

    $ampliar_plazo.click(function () {
      AmpliacionDePlazo('A');
      $ampliar_plazo.prop('disabled', true)
    })

};
    
function DepositoDeCheques(){
  // validar que los elementos seleccionados sean del mismo cliente
  // y del mismo tipo de factoring

  var seleccion=  $table.bootstrapTable('getSelections')
  var ids = getIdSelections()

    // calcular el total de saldos de documentos para llevarlo a siguiente pantalla
    const total_cartera = seleccion.map(function(row) {
      return +row.Valor.substring(0);
        }).reduce(function (sum, i) {
          return Math.round((sum + i + Number.EPSILON) * 100) / 100;
      }, 0)
    url = '/cobranzas/depositodecheques/'+ids+'/'+total_cartera+'/CE/None'
    
    location.href=url
  return false
}

function DepositoCuentaCliente(){
  var seleccion=  $table.bootstrapTable('getSelections')
  var ids = getIdSelections()
  var id_cliente = ''
  var error = false

  seleccion.map(function(row)  {
    // validar un solo cliente
    if (id_cliente==''){
      id_cliente=row.IdCliente
    }
    else{ if (id_cliente != row.IdCliente){
      error = true
    }}
  });
  // cargar forma de cobro de documentos seleccionados

  if (error ){
    alert("Ha seleccionado varios clientes. No puede continuar")
  }
  else{
    // calcular el total de saldos de documentos para llevarlo a siguiente pantalla
    const total_cartera = seleccion.map(function(row) {
      return +row.Valor.substring(0);
        }).reduce(function (sum, i) {
          return Math.round((sum + i + Number.EPSILON) * 100) / 100;
      }, 0)
    url = '/cobranzas/depositodecheques/'+ids+'/'+total_cartera+'/CC/'+id_cliente
    
    location.href=url
    
  }

}

window.operateEvents = {
  'click .canjear': function (e, value, row, index) {
    CanjearCheque(row.id, row.IdCliente, row.IdComprador)
  },
  'click .quitar': function (e, value, row, index) {
    QuitarAccesorio( row.id, row.IdCliente)
  },
  'click .prorroga': function (e, value, row, index) {
    if(row.Anticipa100){
      alert("No puede ejecutar la prorroga de un documento al que se ha anticipado el 100 %. Debe realizar una ampliación de plazo")
    }else{
      Prorroga( row.id, 'A', row.Vencimiento, row.Documento)
    }
  },
};

function operateFormatter(value, row, index) {
return [
  '<a class="canjear" href="javascript:void(0)" title="Canjear">',
  '<i class="fa fa-exchange"></i>',
  '</a>  ',
  '<a class="quitar" href="javascript:void(0)" title="Quitar accesorio">',
  '<i class="fa fa-unlink"></i>',
  '</a>  ',
  '<a class="prorroga" href="javascript:void(0)" title="Prorroga">',
  '<i class="fa fa-mail-forward"></i>',
  '</a>  ',
].join('')
}

function CanjearCheque(cheque_id, cliente_id, deudor_id){
  AbrirModal("/cobranzas/canjearchequeaccesorio/"+ cheque_id + '/' + cliente_id + '/' + deudor_id)
}

function QuitarAccesorio(cheque_id, cliente_id){
  AbrirModal("/cobranzas/quitaraccesorio/"+ cheque_id + '/' + cliente_id)
}
