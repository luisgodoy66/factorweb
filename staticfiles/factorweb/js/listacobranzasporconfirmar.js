function ConfirmarCobranza(cobranza_id, tipo_operacion){
    MensajeConfirmacion("Confirmar la cobranza " +  cobranza_id +"?",function(){
      fetchProcesar("/cobranzas/confirmarcobranza/"+cobranza_id+"/"+tipo_operacion, function(){
            location.reload();
          })
      })
      
  }