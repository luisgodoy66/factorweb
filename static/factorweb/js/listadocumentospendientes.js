var $btnFiltrar = jQuery('#btnFiltrar')
var $table = jQuery('#table')
var selections = []
var $cobroconcheque = jQuery("#cobroconcheque")
var $cobroconefectivo = jQuery("#cobroconefectivo")
var $cobroconmovimiento = jQuery("#cobroconmovimiento")
var $cobrocontransferencia = jQuery("#cobrocontransferencia")
const filtro = capturaValor("filtro")

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();

    // si la lista es de cartera vencida no debe mostrar filtro
    if (filtro=='Si'){
      document.querySelector('#filtro_por_vencer').removeAttribute('hidden');
    }
  
    $table.bootstrapTable({locale:"es-EC"});
    
    // // objeto_fechas("#fechacorte")
    // let hoy = new Date();
    // let semanaEnMilisegundos = 1000 * 60 * 60 * 24 * 7;
    // let suma = hoy.getTime() + semanaEnMilisegundos; //getTime devuelve milisegundos de esa fecha
    // let fechaDentroDeUnaSemana = new Date(suma);
    // inicializaValor("fechacorte", fechaDentroDeUnaSemana.toISOString())

    // boton de refrescar filtro
    $btnFiltrar.click(function () {
        fecha = capturaValor("fechacorte");
        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/cobranzas/carteraporvencerjson/" + fecha
        })
    })

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

      CobroDeDocumentos('CHE');
      $cobroconcheque.prop('disabled', true)
    })

    $cobroconefectivo.click(function () {

      CobroDeDocumentos('EFE');
      $cobroconefectivo.prop('disabled', true)
    })

    $cobroconmovimiento.click(function () {

      CobroDeDocumentos('MOV');
      $cobroconmovimiento.prop('disabled', true)
    })

    $cobrocontransferencia.click(function () {

      CobroDeDocumentos('TRA');
      $cobrocontransferencia.prop('disabled', true)
    })

};
    
function CobroDeDocumentos(forma){
  // validar que los elementos seleccionados sean del mismo cliente
  // y del mismo tipo de factoring

  var seleccion=  $table.bootstrapTable('getSelections')
  var ids = getIdSelections()
  var id_cliente = ''
  var error = false
  var tipo_factoring=''
  var id_comprador =''
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
    // determinar si hay un solo comprador
    if (id_comprador=='')  {
      id_comprador=row.IdComprador
    }
    else{ if (id_comprador != row.IdComprador){
      un_solo_comprador = "No"
    }}
  });
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

    url = '/cobranzas/cobrodedocumentos/'+ids+'/'+total_cartera+'/'+forma+'/'
      +id_cliente+'/'+un_solo_comprador+'/'+id_comprador+'/'+tipo_factoring;
    
    location.href=url
  }
  return false
}
