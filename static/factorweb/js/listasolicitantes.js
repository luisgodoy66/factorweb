function EliminarSolicitante(solicitante_id, nombre_solicitante){
  MensajeConfirmacion("Eliminar al solicitante " +  nombre_solicitante +"?",function(){
    fetchProcesar("/solicitudes/eliminarsolicitante/"+solicitante_id, function(){
          location.reload();
        })
    })
    
}
