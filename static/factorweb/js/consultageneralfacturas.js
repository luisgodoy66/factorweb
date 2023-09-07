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
            url: "/contabilidad/facturasjson/"+desde+"/" + hasta
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
}

window.operateEvents = {
    'click .xml': function (e, value, row, index) {
      ImprimirCobranza(row.id, row.TipoOperacion, row.Cliente)
      },
    };
      
function operateFormatter(value, row, index) {
    return [
        '<a class="xml" href="javascript:void(0)" title="Genera XML ">',
        '<i class="fa fa-rotate-left"></i>',
        '</a>  ',
      ].join('')
}
  