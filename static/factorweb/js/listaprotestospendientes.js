var $table = jQuery('#table')
var selections = []
var $cobroconcheque = jQuery("#cobroconcheque")
var $cobroconefectivo = jQuery("#cobroconefectivo")
var $cobroconmovimiento = jQuery("#cobroconmovimiento")
var $cobrocontransferencia = jQuery("#cobrocontransferencia")
var $liquidacionencero = jQuery("#liquidacionencero")

window.onload=function(){

    // si la lista es de cartera vencida no debe mostrar filtro
    $table.bootstrapTable({locale:"es-EC"});
    
    // evento de marcar y desmarcar documentos
    $table.on('check.bs.table uncheck.bs.table ' +
      'check-all.bs.table uncheck-all.bs.table',
        function () {
        $cobroconcheque.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $cobroconefectivo.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $cobroconmovimiento.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $cobrocontransferencia.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $liquidacionencero.prop('disabled', !$table.bootstrapTable('getSelections').length)

        // save your data, here just save the current page
        selections = getIdSelections()
        // push or splice the selections if you want to save all data selections
        }
    )

    $table.on('all.bs.table', function (e, name, args) {
      console.log(name, args)
    })

    // acciones ejecutada sobre registros seleccionados
    $cobroconcheque.click(function () {
      RecuperacionDeProtesto('CHE');
      $cobroconcheque.prop('disabled', true)
    })

    $cobroconefectivo.click(function () {
      RecuperacionDeProtesto('EFE');
      $cobroconefectivo.prop('disabled', true)
    })

    $cobroconmovimiento.click(function () {
      RecuperacionDeProtesto('MOV');
      $cobroconmovimiento.prop('disabled', true)
    })

    $cobrocontransferencia.click(function () {
      RecuperacionDeProtesto('TRA');
      $cobrocontransferencia.prop('disabled', true)
    })

    $liquidacionencero.click(function () {
      LiquidacionEnCero('Recuperación', 'No');
      $liquidacionencero.prop('disabled', true)
    })

};

window.operateEvents = {
  'click .revertir': function (e, value, row, index) {
    ReversaProtesto(row.IdCobranza, row.id, row.TipoOperacion, row.Cobranza
      , row.IdCliente, row.IdTipoFactoring)
  },
  'click .imprimir': function (e, value, row, index) {
    ImprimirCobranza(row.IdCobranza, row.TipoOperacion)
  },
};

function operateFormatter(value, row, index) {
return [
  '<a class="revertir" href="javascript:void(0)" title="Reverso de protesto">',
  '<i class="fa fa-rotate-left"></i>',
  '</a>  ',
  '<a class="imprimir" href="javascript:void(0)" title="Imprimir cobranza">',
  '<i class="fa fa-print"></i>',
  '</a>  ',
].join('')
}
    
function RecuperacionDeProtesto(forma){
  // validar que los elementos seleccionados sean del mismo cliente
  // y del mismo tipo de factoring

  var seleccion=  $table.bootstrapTable('getSelections')
  var ids = getIdSelections()
  var id_cliente = ''
  var error = false
  var tipo_factoring=''
  var id_comprador ='nulo'
  var un_solo_comprador = "Si"

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
    if (id_comprador=='nulo')  {
      id_comprador=row.IdComprador
    }
    else{ if (id_comprador != row.IdComprador){
      un_solo_comprador = "No"
    }}
});
  if (id_comprador==''){
    un_solo_comprador = "No"
    id_comprador='0'
  }
  // cargar forma de cobro de documentos seleccionados
  if (error ){
    alert("Ha seleccionado varios clientes o tipos de factoring. No puede continuar")
  }
  else{
    // calcular el total de saldos de documentos para llevarlo a siguiente pantalla
    const total_cartera = seleccion.map(function(row) {
      return +row.Saldo.substring(0);
        }).reduce(function (sum, i) {
          return Math.round((sum + i + Number.EPSILON) * 100) / 100;
      }, 0)

    url = '/cobranzas/recuperaciondeprotesto/'+ids+'/'+total_cartera+'/'+forma+'/'
    +id_cliente+'/'+un_solo_comprador+'/'+id_comprador+'/'+tipo_factoring;
    
    location.href=url
  }
  return false
}

function ReversaProtesto(cobranza_id, protesto_id, tipo_operacion, cobranza
    , id_cliente, id_factoring){
    MensajeConfirmacion("Reversa el protesto de " +  cobranza_id +"?",function(){
      fetchProcesar("/cobranzas/reversaprotesto/"+cobranza_id+"/"+tipo_operacion
        +"/"+protesto_id+"/"+cobranza+"/"+id_cliente+"/"+id_factoring, function(){
            location.reload();
          })
      })
  }
