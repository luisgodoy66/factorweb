var $table = jQuery('#table')

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();

    $table.bootstrapTable({"locale" : 'es-EC' });
}

window.operateEvents = {
        'click .edit': function (e, value, row, index) {
            EditarDiasACondonar(row.id, row.DiasCondonados)
          }
};
      
function operateFormatter(value, row, index) {
      return [
        '<a class="edit" href="javascript:void(0)" title="Días a condonar">',
        '<i class="fa fa-edit"></i>',
      ].join('')
}

function EditarDiasACondonar(cobro_id, dias){
    // abrir modal para grabar días condonados
    id_cobranza = capturaValor("id_cobranza")
    tipo_operacion = capturaValor("tipo_operacion")
    AbrirModal("/cobranzas/datosdiascondonar/"+cobro_id+"/"+dias+"/"+id_cobranza+"/"+tipo_operacion)
}