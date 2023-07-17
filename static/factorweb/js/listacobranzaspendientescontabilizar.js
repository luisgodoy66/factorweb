var $btnFiltrar = jQuery('#btnFiltrar')
var $table = jQuery('#table')
var selections = []
var $generar = jQuery("#generar")
var $ampliar_plazo = jQuery("#ampliarplazo")

window.onload=function(){

 
    $table.bootstrapTable({locale:"es-EC"});
    
    // boton de refrescar filtro
    $btnFiltrar.click(function () {
        desde = capturaValor("desde");
        hasta = capturaValor("hasta");
        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/contabilidad/cobranzaspendientesjson/" + desde + "/" + hasta
        })
    })

    // evento de marcar y desmarcar cobranzas
    $table.on('check.bs.table uncheck.bs.table ' +
      'check-all.bs.table uncheck-all.bs.table',
        function () {
        $generar.prop('disabled', !$table.bootstrapTable('getSelections').length)

        // save your data, here just save the current page
        selections = getIdSelections()
        // push or splice the selections if you want to save all data selections
        }
    )

    $table.on('all.bs.table', function (e, name, args) {
      console.log(name, args)
    })

    // acciones ejecutada sobre registros seleccionados
    $generar.click(function () {
      GenerarAsientosCobranzas();
      $generar.prop('disabled', true)
    })
};
    
function GenerarAsientosCobranzas(){
  // validar que los elementos seleccionados sean del mismo cliente
  // y del mismo tipo de factoring

  var ids = getIdSelections()

  fetchProcesar('/contabilidad/generarasientoscobranzas/'+ids,function(){
    MensajeOK("Asientos generados. Revíselos en Contabilidad/Asientos/Registros de asientos")
      url = '/contabilidad/listacobranzaspendientescontabilizar/';
      location.href=url
    
  })
    
  return false
}

