function EliminarTransferencia( documento_id){
    MensajeConfirmacion("Eliminar transferencia " + documento_id + "?",function(){
  
      fetchProcesar("/cuentasconjuntas/eliminartransferencia/"+ documento_id, function(){
        // $table.bootstrapTable('remove', {
        //   field: 'id',
        //   values: [documento_id]
        // });
        location.reload();
      })
  })
  }
  
  