var $table = jQuery('#table')
var $btnFiltrar = jQuery('#btnFiltrar')

window.onload=function(){

    jQuery(".standardSelect").chosen({
        disable_search_threshold: 10,
        no_results_text: "Oops, cliente no encontrado!",
        width: "100%"
    });

    inicializaValor("fechadesde", capturaValor("id_desde"))
    inicializaValor("fechahasta", capturaValor("id_hasta"))

    $table.bootstrapTable({locale:"es-EC"});

    // boton de refrescar filtro
    $btnFiltrar.click(function () {

        desde = capturaValor("fechadesde");
        hasta = capturaValor("fechahasta");

        var x = [];
        var options = document.getElementById("id_clientes").selectedOptions;
        for (var i = 0; i < options.length; i++) {
          x.push(options[i].value);
        }
        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/operaciones/asignacionesjson/"+desde+"/" + hasta+"/"+x
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
};
window.operateEvents = {
    'click .revertir': function (e, value, row, index) {
        ReversarAceptacionAsignacion(row.id, row.Asignacion)
      },
      'click .imprimir': function (e, value, row, index) {
        ImprimirAsignacion( row.id)
      },
    };
      
function operateFormatter(value, row, index) {
    return [
        '<a class="revertir" href="javascript:void(0)" title="Reverso de asignación">',
        '<i class="fa fa-rotate-left"></i>',
        '</a>  ',
        '<a class="imprimir" href="javascript:void(0)" title="Imprimir asignación">',
        '<i class="fa fa-print"></i>',
        '</a>  ',
      ].join('')
}
function imprimeOperacionesNegociadas(){
  desde = capturaValor("fechadesde");
  hasta = capturaValor("fechahasta");
  var x = [];
  var options = document.getElementById("id_clientes").selectedOptions;
  for (var i = 0; i < options.length; i++) {
    x.push(options[i].value);
  }
  // en una nueva ventana abrir el reporte de asignación
  url = window.location.origin
  url = url + "/operaciones/impresionresumenasignaciones/"+desde+"/"+hasta+"/"+x;
  window.open( url);
  }