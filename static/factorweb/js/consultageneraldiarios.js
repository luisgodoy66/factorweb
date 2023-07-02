var $table = jQuery('#table')
var $btnFiltrar = jQuery('#btnFiltrar')

window.onload=function(){

    inicializaValor("fechadesde", capturaValor("id_desde"))
    inicializaValor("fechahasta", capturaValor("id_hasta"))

    $table.bootstrapTable({locale:"es-EC"});

    // boton de refrescar filtro
    $btnFiltrar.click(function () {

        desde = capturaValor("fechadesde");
        hasta = capturaValor("fechahasta");

        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/contabilidad/asientosdiariojson/"+desde+"/" + hasta
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
};
window.operateEvents = {
    'click .revertir': function (e, value, row, index) {
        ReversarAsientoDiario(row.id, row.Diario)
      },
      'click .imprimir': function (e, value, row, index) {
        ImprimirAsientoDiario( row.id, row.Tipo)
      },
    };
      
function operateFormatter(value, row, index) {
    return [
        '<a class="revertir" href="javascript:void(0)" title="Reverso de asiento">',
        '<i class="fa fa-rotate-left"></i>',
        '</a>  ',
        '<a class="imprimir" href="javascript:void(0)" title="Imprimir asiento">',
        '<i class="fa fa-print"></i>',
        '</a>  ',
      ].join('')
}
    