window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();

    }

function ReversarAceptacionAsignacion(asignacion_id){
    // este proceso a diferencia de aceptar no se ejecuta desde un
    // formulario por eso no usa fetchPostear

    MensajeConfirmacion("Reversar aceptación " +  asignacion_id +"?",function(){
        fetchProcesar("/operaciones/reversaraceptacionasignacion/"+  asignacion_id,  function(){
            location.reload();
        })
    })
      
}