var $table = jQuery('#table')
var $btnFiltrar = jQuery('#btnFiltrar')

window.onload=function(){
    
    objeto_fechas("#fechadesde")
    objeto_fechas("#fechahasta")

    inicializaValor("fechadesde", capturaValor("id_desde"))
    inicializaValor("fechahasta", capturaValor("id_hasta"))

    $table.bootstrapTable({locale:"es-EC"});

    // boton de refrescar filtro
    $btnFiltrar.click(function () {

        desde = capturaValor("fechadesde");
        hasta = capturaValor("fechahasta");

        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/operaciones/asignacionesjson/"+desde+"/" + hasta
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
};
window.operateEvents = {
    'click .revertir': function (e, value, row, index) {
        ReversarAceptacionAsignacion(row.id, )
      },
      'click .imprimir': function (e, value, row, index) {
        ImprimirAsignacion( row.id)
      },
    };
      
function operateFormatter(value, row, index) {
    return [
        '<a class="revertir" href="javascript:void(0)" title="Reverso de confirmación">',
        '<i class="fa fa-rotate-left"></i>',
        '</a>  ',
        '<a class="imprimir" href="javascript:void(0)" title="Imprimir asignación">',
        '<i class="fa fa-print"></i>',
        '</a>  ',
      ].join('')
}
    