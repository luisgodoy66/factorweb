function EliminarAsignacion(asignacion_id){
  MensajeConfirmacion("Eliminar solicitud " +  asignacion_id +"?",function(){
    fetchProcesar("/solicitudes/eliminarasignacion/"+asignacion_id, function(){
          location.reload();
        })
    })
    
}