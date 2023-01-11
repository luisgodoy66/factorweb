// funciones operativas
function EliminarDocumentoDeSolicitudAsignacion(asignacion_id, documento_id, tipo_asignacion, documento){
    MensajeConfirmacion("Eliminar documento " + documento
        + " con referencia " + documento_id +"?",function(){

      fetchProcesar("/solicitudes/eliminardetalleasignacion/"
        + asignacion_id + "/" + documento_id+"/"+tipo_asignacion, function(){
        // $table.bootstrapTable('remove', {
        //   field: 'id',
        //   values: [documento_id]
        // });
        location.reload();
      })
  })
}

function ImprimirCobranza(cobranza_id, tipo_operacion){
    // en una nueva ventana abrir el reporte de asignación
    url = window.location.origin
    if (tipo_operacion[0]=="C"){
      url = url + "/cobranzas/reportecobranzacartera/"+cobranza_id;
     }
     else{
      url = url + "/cobranzas/reporterecuperacion/"+cobranza_id;
     }
  window.open( url);
  
  }

function ReversarCobranza(cobranza_id, tipo_operacion){
    // este proceso a diferencia de aceptar no se ejecuta desde un
    // formulario por eso no usa fetchPostear

    MensajeConfirmacion("Reversar cobranza " +  cobranza_id +"?",function(){
        fetchProcesar("/cobranzas/reversarcobranza/" +  cobranza_id + "/"
          + tipo_operacion,  function(){
            location.reload();
        })
    })
      
}