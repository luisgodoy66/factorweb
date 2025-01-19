function EliminarAsignacion(asignacion_id, nombre_cliente){
  MensajeConfirmacion("Eliminar solicitud de " +  nombre_cliente +"?",function(){
    fetchProcesar("/solicitudes/eliminarasignacion/"+asignacion_id, function(){
          location.reload();
        })
    })
    
}