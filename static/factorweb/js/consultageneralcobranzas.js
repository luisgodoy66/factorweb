var $table = jQuery('#table')
var $btnFiltrar = jQuery('#btnFiltrar')

window.onload=function(){
    
    objeto_fechas("#fechadesde")
    objeto_fechas("#fechahasta")
    let hoy = new Date();
    inicializaValor("fechadesde", hoy.toISOString())
    inicializaValor("fechahasta", hoy.toISOString())

    $table.bootstrapTable({locale:"es-EC"});

    // boton de refrescar filtro
    $btnFiltrar.click(function () {

        desde = capturaValor("fechadesde");
        hasta = capturaValor("fechahasta");

        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/cobranzas/cobranzasjson/"+desde+"/" + hasta
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
};
  