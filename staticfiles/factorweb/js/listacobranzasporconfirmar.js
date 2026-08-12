function ConfirmarCobranza(codigo_cobranza, cobranza_id, tipo_operacion){
    MensajeConfirmacion("Confirmar la cobranza " +  codigo_cobranza +"?",function(){
      fetchProcesar("/cobranzas/confirmarcobranza/"+cobranza_id+"/"+tipo_operacion, function(){
            location.reload();
          })
      })
      
  }