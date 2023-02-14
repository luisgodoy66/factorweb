var $btnFiltrar = jQuery('#btnFiltrar')
var $table = jQuery('#table')
var selections = []
var $cobroconcheque = jQuery("#deposito")

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();
    $table.bootstrapTable({locale:"es-EC"});
    
    // // objeto_fechas("#fechacorte")
    // let hoy = new Date();
    // alert(hoy)
    // inicializaValor("fechacorte", hoy.toISOString())

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
        $cobroconcheque.prop('disabled', !$table.bootstrapTable('getSelections').length)

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

      DepositoDeCheques();
      $cobroconcheque.prop('disabled', true)
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

    url = '/cobranzas/depositodecheques/'+ids+'/'+total_cartera+'/'
    
    location.href=url
  return false
}
