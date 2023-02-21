var $table = jQuery('#table')
var $tb_asgn = jQuery('#tb_asgn')
var $tb_liqcob = jQuery('#tb_liqcob')
var $tb_cobcar = jQuery('#tb_cobcar')

window.onload=function(){
  // inicializar el encabezado
  ActualizarHeader();

  // configuracin de las tablas
  $table.bootstrapTable({locale:"es-EC"});
  $tb_asgn.bootstrapTable({locale:"es-EC"});
  $tb_liqcob.bootstrapTable({locale:"es-EC"});
  $tb_cobcar.bootstrapTable({locale:"es-EC"});

  // chart antigüedad de la cartera
  var ctx = document.getElementById( "singelBarChart" );
  ctx.height = 150;
  var myChart = new Chart( ctx, {
      type: 'bar',
      data: {
          labels: [ "Sun", "Mon", "Tu", "Wed", "Th", "Fri", "Sat" ],
          datasets: [
              {
                  label: "My First dataset",
                  data: [ 40, 55, 75, 81, 56, 55, 40 ],
                  borderColor: "rgba(0, 123, 255, 0.9)",
                  borderWidth: "0",
                  backgroundColor: "rgba(0, 123, 255, 0.5)"
                          }
                      ]
      },
      options: {
          scales: {
              yAxes: [ {
                  ticks: {
                      beginAtZero: true
                  }
                              } ]
          }
      }
  } );
  
  
}

window.operateEvents = {
  'click .revertir': function (e, value, row, index) {
    ReversarCobranza(row.id, row.TipoOperacion)
  },
  'click .imprimir': function (e, value, row, index) {
    ImprimirCobranza( row.id, row.TipoOperacion)
  },
};

function operateFormatter(value, row, index) {
return [
  '<a class="revertir" href="javascript:void(0)" title="Reverso de cobranza">',
  '<i class="fa fa-rotate-left"></i>',
  '</a>  ',
  '<a class="imprimir" href="javascript:void(0)" title="Imprimir cobranza">',
  '<i class="fa fa-print"></i>',
  '</a>  ',
].join('')
}

window.operateEventsAsgn = {
  'click .revertir': function (e, value, row, index) {
    ReversarAceptacionAsignacion(row.id, )
  },
  'click .imprimir': function (e, value, row, index) {
    ImprimirAsignacion( row.id, )
  },
};

function operateFormatterAsgn(value, row, index) {
return [
  '<a class="revertir" href="javascript:void(0)" title="Reverso de asignación">',
  '<i class="fa fa-rotate-left"></i>',
  '</a>  ',
  '<a class="imprimir" href="javascript:void(0)" title="Imprimir asignación">',
  '<i class="fa fa-print"></i>',
  '</a>  ',
].join('')
}

window.operateEventsLiqCob = {
  'click .revertir': function (e, value, row, index) {
    ReversarliquidacionCobranza(row.id, )
  },
  'click .imprimir': function (e, value, row, index) {
    ImprimirLiquidacionCobranza( row.id, )
  },
};

function operateFormatterLiqCob(value, row, index) {
return [
  '<a class="revertir" href="javascript:void(0)" title="Reverso de asignación">',
  '<i class="fa fa-rotate-left"></i>',
  '</a>  ',
  '<a class="imprimir" href="javascript:void(0)" title="Imprimir asignación">',
  '<i class="fa fa-print"></i>',
  '</a>  ',
].join('')
}

window.operateEventsCobCar = {
  'click .revertir': function (e, value, row, index) {
    ReversarCobranzaCargos(row.id, row.Operacion, row.TipoOperacion)
  },
  'click .imprimir': function (e, value, row, index) {
    ImprimirCobranzaCargos( row.id, )
  },
};

function operateFormatterCobCar(value, row, index) {
return [
  '<a class="revertir" href="javascript:void(0)" title="Reverso de asignación">',
  '<i class="fa fa-rotate-left"></i>',
  '</a>  ',
  '<a class="imprimir" href="javascript:void(0)" title="Imprimir asignación">',
  '<i class="fa fa-print"></i>',
  '</a>  ',
].join('')
}

