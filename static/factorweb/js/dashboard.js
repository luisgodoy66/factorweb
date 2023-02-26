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

  antigüedadcartera();

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

function antigüedadcartera(){
  // chart antigüedad de la cartera
  fetchRecuperar("/operaciones/antigüedadcartera",function(data){
    var ctx = document.getElementById( "singelBarChart" );
    ctx.height = 150;

    v90m = data["facturas"]["vencido_mas_90"]
    v90 = data["facturas"]["vencido_90"]
    v60 = data["facturas"]["vencido_60"]
    v30 = data["facturas"]["vencido_30"]
    p30 = data["facturas"]["porvencer_30"]
    p60 = data["facturas"]["porvencer_60"]
    p90 = data["facturas"]["porvencer_90"]
    p90m = data["facturas"]["porvencer_mas_90"]
    
    av90m = data["accesorios"]["vencido_mas_90"]
    av90 = data["accesorios"]["vencido_90"]
    av60 = data["accesorios"]["vencido_60"]
    av30 = data["accesorios"]["vencido_30"]
    ap30 = data["accesorios"]["porvencer_30"]
    ap60 = data["accesorios"]["porvencer_60"]
    ap90 = data["accesorios"]["porvencer_90"]
    ap90m = data["accesorios"]["porvencer_mas_90"]
    
    pv90m = data["protestos"]["vencido_mas_90"]
    pv90 = data["protestos"]["vencido_90"]
    pv60 = data["protestos"]["vencido_60"]
    pv30 = data["protestos"]["vencido_30"]
    pp30 = data["protestos"]["porvencer_30"]
    pp60 = data["protestos"]["porvencer_60"]
    pp90 = data["protestos"]["porvencer_90"]
    pp90m = data["protestos"]["porvencer_mas_90"]
    
    var myChart = new Chart( ctx, {
        type: 'bar',
        data: {
            labels: [ "v+90", "v90", "v60", "v30", "x30", "x60", "x90", "x+90" ],
            datasets: [
                {
                    label: "Facturas",
                    data: [ v90m, v90, v60, v30, p30, p60, p90, p90m ],
                    borderColor: "rgba(0, 123, 255, 0.9)",
                    borderWidth: "0",
                    backgroundColor: "rgba(0, 123, 255, 0.5)"
                            },
                {
                    label: "Accesorios",
                    data: [ av90m, av90, av60, av30, ap30, ap60, ap90, ap90m ],
                    borderColor: "rgba(0, 123, 255, 0.9)",
                    borderWidth: "0",
                    backgroundColor: "rgba(0, 255, 255, 0.5)"
                            },
                {
                    label: "Protestos",
                    data: [ pv90m, pv90, pv60, pv30, pp30, pp60, pp90, pp90m ],
                    borderColor: "rgba(0, 123, 255, 0.9)",
                    borderWidth: "0",
                    backgroundColor: "rgba(255, 0, 0, 0.5)"
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

  })
}