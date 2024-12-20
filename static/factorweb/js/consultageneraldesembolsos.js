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
            url: "/operaciones/desembolsosjson/"+desde+"/" + hasta
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
}

window.operateEvents = {
    'click .revertir': function (e, value, row, index) {
        ReversarDesembolso(row.id, 
            row.TipoOperacion, 
            row.Operacion,
            row.Asiento)
      },
    };
      
function operateFormatter(value, row, index) {
    return [
        '<a class="revertir" href="javascript:void(0)" title="Reverso de desembolso">',
        '<i class="fa fa-rotate-left"></i>',
        '</a>  ',
      ].join('')
}
  