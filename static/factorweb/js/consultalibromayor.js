var $table = jQuery('#table')
var $btnFiltrar = jQuery('#btnFiltrar')

window.onload=function(){

    jQuery(".standardSelect").chosen({
        disable_search_threshold: 10,
        no_results_text: "Oops, cuenta no encontrada!",
        width: "100%"
    });

    inicializaValor("fechadesde", capturaValor("id_desde"))
    inicializaValor("fechahasta", capturaValor("id_hasta"))

    $table.bootstrapTable({locale:"es-EC"});

    // boton de refrescar filtro
    $btnFiltrar.click(function () {

        desde = capturaValor("fechadesde");
        hasta = capturaValor("fechahasta");
        cuentas = capturaValor("id_cuentas")
        // capturar los valores de un select multiple ?
        var x = [];
        var options = document.getElementById("id_cuentas").selectedOptions;
        for (var i = 0; i < options.length; i++) {
          x.push(options[i].value);
        }
        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/contabilidad/libromayorjson/"+desde+"/" + hasta +"/" + x
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
};
window.operateEvents = {
      'click .imprimir': function (e, value, row, index) {
        ImprimirAsientoDiario( row.Diario, row.Tipo)
      },
    };
      
function operateFormatter(value, row, index) {
    return [
        '<a class="imprimir" href="javascript:void(0)" title="Imprimir asiento">',
        '<i class="fa fa-print"></i>',
        '</a>  ',
      ].join('')
}
    