var $table = jQuery('#table')
var selections = []
var $btnliquidar = jQuery("#btnliquidar")

window.onload=function(){
  $table.bootstrapTable({locale:"es-EC"});
  
  // evento de marcar y desmarcar documentos
  $table.on('check.bs.table uncheck.bs.table ' +
    'check-all.bs.table uncheck-all.bs.table',
      function () {
      $btnliquidar.prop('disabled', !$table.bootstrapTable('getSelections').length)

      // save your data, here just save the current page
      selections = getIdSelections()
      // push or splice the selections if you want to save all data selections
      }
  )
    
  $table.on('all.bs.table', function (e, name, args) {
    console.log(name, args)
  })
  
  // acciones ejecutada sobre registros seleccionados
  $btnliquidar.click(function () {

    Liquidar();
    $btnliquidar.prop('disabled', true)
  })

}

window.operateEvents = {
  'click .revertir': function (e, value, row, index) {
    ReversaConfirmacion(row.id, row.TipoOperacion)
  },
  'click .condonar': function (e, value, row, index) {
    Condonar( row.id, row.TipoOperacion)
  },
  'click .imprimir': function (e, value, row, index) {
    ImprimirCobranza( row.id, row.TipoOperacion)
  },
};

function operateFormatter(value, row, index) {
return [
  '<a class="condonar" href="javascript:void(0)" title="Días a condonar">',
  '<i class="fa fa-gift"></i>',
  '</a>  ',
  '<a class="revertir" href="javascript:void(0)" title="Reverso de confirmación">',
  '<i class="fa fa-rotate-left"></i>',
  '</a>  ',
  '<a class="imprimir" href="javascript:void(0)" title="Imprimir cobranza">',
  '<i class="fa fa-print"></i>',
  '</a>  ',
].join('')
}

function ReversaConfirmacion(cobranza_id, tipo_operacion){
    MensajeConfirmacion("Reversa la confirmación de " +  cobranza_id +"?",function(){
      fetchProcesar("/cobranzas/reversaconfirmacioncobranza/"+cobranza_id+"/"+tipo_operacion, function(){
            location.reload();
          })
      })

  }

function Condonar(cobranza_id, tipo_operacion){
  window.location.href = "/cobranzas/cobranzaporcondonar/" + cobranza_id+"/"+tipo_operacion
}

function Liquidar(){
  var seleccion=  $table.bootstrapTable('getSelections')
  var ids = getIdSelections()
  var id_cliente = ''
  var error = false
  var tipo_factoring=''
  var tipo_operacion =''

  seleccion.map(function(row)  {
    // validar un solo cliente
    if (id_cliente==''){
      id_cliente=row.IdCliente
    }
    else{ if (id_cliente != row.IdCliente){
      error = true
    }}
    // validar un solo tipo de factoring. Aunque este campo no aparece en la bt, 
    // si está en el data con que se carga la bt
    if (tipo_factoring==''){
      tipo_factoring=row.IdTipoFactoring
    }
    else{ if (tipo_factoring != row.IdTipoFactoring){
        error = true
    }}
    // determinar si hay un solo comprador
    if (tipo_operacion==''){
      tipo_operacion=row.TipoOperacion
    }
    else{ if (tipo_operacion != row.TipoOperacion){
      error = true
    }}
  });

  // debe validar que correspondan al mismo cliente
  if (error ){
    alert("Ha seleccionado varios clientes o tipos de factoring o tipos de operaciones. No puede continuar")
  }
  else{

    url = '/cobranzas/liquidarcobranzas/'+ids+'/'+tipo_operacion 
    
    location.href=url
  }
  return false
}

