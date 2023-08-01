var $table = jQuery('#table')
var selections = []
var $cobroconcheque = jQuery("#cobroconcheque")
var $cobroconefectivo = jQuery("#cobroconefectivo")
var $cobroconmovimiento = jQuery("#cobroconmovimiento")
var $cobrocontransferencia = jQuery("#cobrocontransferencia")
// const tipo_nd = capturaValor("tipo_nd")

window.onload=function(){
    $table.bootstrapTable({locale:"es-EC"});
    
    // evento de marcar y desmarcar documentos
    $table.on('check.bs.table uncheck.bs.table ' +
      'check-all.bs.table uncheck-all.bs.table',
        function () {
        $cobroconcheque.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $cobroconefectivo.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $cobroconmovimiento.prop('disabled', !$table.bootstrapTable('getSelections').length)
        $cobrocontransferencia.prop('disabled', !$table.bootstrapTable('getSelections').length)

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

      CobroDeCargos('CHE');
      $cobroconcheque.prop('disabled', true)
    })

    $cobroconefectivo.click(function () {

      CobroDeCargos('EFE');
      $cobroconefectivo.prop('disabled', true)
    })

    $cobroconmovimiento.click(function () {

      CobroDeCargos('MOV');
      $cobroconmovimiento.prop('disabled', true)
    })

    $cobrocontransferencia.click(function () {

      CobroDeCargos('TRA');
      $cobrocontransferencia.prop('disabled', true)
    })
};
window.operateEvents = {
    'click .imprimir': function (e, value, row, index) {
      if (row.Tipo=='A'){
          ImprimirAmpliacionPlazo(row.id)    
      }
    },
  };
  
  function operateFormatter(value, row, index) {
  return [
    '<a class="imprimir" href="javascript:void(0)" title="Imprimir cargos">',
    '<i class="fa fa-print"></i>',
    '</a>  ',
  ].join('')
  }
      
function CobroDeCargos(forma){
  // validar que los elementos seleccionados sean del mismo cliente
  // y del mismo tipo de factoring

  var seleccion=  $table.bootstrapTable('getSelections')
  var ids = getIdSelections()
  var id_cliente = ''
  var error = false
  var tipo_factoring=''

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
  });
  // cargar forma de cobro de documentos seleccionados

  if (error ){
    alert("Ha seleccionado varios clientes o tipos de factoring. No puede continuar")
  }
  else{
    // calcular el total de saldos de documentos para llevarlo a siguiente pantalla
    const total_cargos = seleccion.map(function(row) {
      return +row.Saldo.substring(0);
        }).reduce(function (sum, i) {
          return Math.round((sum + i + Number.EPSILON) * 100) / 100;
      }, 0)

    url = '/cobranzas/cobrodefacturasdeventa/'+ids+'/'+total_cargos+'/'+forma+'/'
      +id_cliente+'/'+tipo_factoring+'/FV';
    
    location.href=url
  }
  return false
}
