window.onload=function(){

    }

function ReversarLiquidacion(liquidacion_id, codigo_liquidacion, tipo_operacion){
    // este proceso a diferencia de aceptar no se ejecuta desde un
    // formulario por eso no usa fetchPostear

    MensajeConfirmacion("Reversar liquidación " +  liquidacion_id +"?",function(){
        fetchProcesar("/cobranzas/reversarliquidacion/"+  liquidacion_id, function(){
                location.reload();
        })
    })
      
}