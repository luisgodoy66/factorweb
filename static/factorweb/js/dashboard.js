var $table = jQuery('#table')
var $tb_asgn = jQuery('#tb_asgn')

window.onload=function(){
  // inicializar el encabezado
  ActualizarHeader();
  $table.bootstrapTable({locale:"es-EC"});
  $tb_asgn.bootstrapTable({locale:"es-EC"});
  
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

