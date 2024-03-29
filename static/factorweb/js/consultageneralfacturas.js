var $table = jQuery('#table')
var $btnFiltrar = jQuery('#btnFiltrar')
const ambiente = capturaValor('ambiente')

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
      generarXMLFactura(row.id, ambiente)
      },
    };
      
function operateFormatter(value, row, index) {
    return [
        '<a class="xml" href="javascript:void(0)" title="Genera XML ">',
        '<i class="fa fa-download"></i>',
        '</a>  ',
      ].join('')
}
  