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

        var x = [];
        var options = document.getElementById("id_clientes").selectedOptions;
        for (var i = 0; i < options.length; i++) {
          x.push(options[i].value);
        }
        $table.bootstrapTable('refreshOptions', {
            showRefresh: true,
            url: "/cobranzas/cobranzasjson/"+desde+"/" + hasta+"/"+x
        })
    })


    // cerrar side bar
    CerrarSideBar();
  
}

window.operateEvents = {
  'click .revertir': function (e, value, row, index) {
    ReversarCobranza(row.id, row.TipoOperacion, row.Cliente)
    },
    'click .imprimir': function (e, value, row, index) {
      ImprimirCobranza( row.id, row.TipoOperacion)
    },
    'click .editar': function (e, value, row, index) {
      ModificarCobranza( row.id, row.TipoOperacion, row.Contabilizada)
    },
  };
    
function operateFormatter(value, row, index) {
    return [
        '<a class="editar" href="javascript:void(0)" title="modificar cobranza">',
        '<i class="fa fa-edit"></i>',
        '</a>  ',
        '<a class="revertir" href="javascript:void(0)" title="Reverso de cobranza">',
        '<i class="fa fa-rotate-left"></i>',
        '</a>  ',
        '<a class="imprimir" href="javascript:void(0)" title="Imprimir cobranza">',
        '<i class="fa fa-print"></i>',
        '</a>  ',
      ].join('')
}
  
function imprimeCobranzas(){
  desde = capturaValor("fechadesde");
  hasta = capturaValor("fechahasta");
  var x = [];
  var options = document.getElementById("id_clientes").selectedOptions;
  for (var i = 0; i < options.length; i++) {
    x.push(options[i].value);
  }
  // en una nueva ventana abrir el reporte de asignación
  url = window.location.origin
  url = url + "/cobranzas/detallecobranzas/"+desde+"/"+hasta+"/"+x;
  window.open( url);
}

function imprimeFacturasPendientes(){
  var x = [];
  var options = document.getElementById("id_clientes").selectedOptions;
  for (var i = 0; i < options.length; i++) {
    x.push(options[i].value);
  }
  // en una nueva ventana abrir el reporte de asignación
  url = window.location.origin
  url = url + "/operaciones/impresioncarterapendiente/"+x;
  window.open( url);
}