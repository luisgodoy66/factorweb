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
    // en una nueva ventana abrir el reporte de cobranza
    // eliminar espacios al final de string ?
    tipo = tipo_operacion.substr(0,2).trim()
    
    url = window.location.origin
    if (tipo=="CC"){
      url = url + "/cobranzas/reportecobranzacargos/"+cobranza_id;
     }
    if (tipo=="C"){
      url = url + "/cobranzas/reportecobranzacartera/"+cobranza_id;
     }
     if (tipo=="R"){
      url = url + "/cobranzas/reporterecuperacion/"+cobranza_id;
     }
     if (tipo=="L"){
      url = url + "/cobranzas/reporteliquidacion/"+cobranza_id;
     }
  window.open( url);
  
}

function ReversarCobranza(operacion_id, tipo_operacion, nombre_cliente = null){
    // este proceso a diferencia de aceptar no se ejecuta desde un
    // formulario por eso no usa fetchPostear
  if (nombre_cliente){
    id_operacion = "de " + nombre_cliente
  }
  else{
    id_operacion =  operacion_id
  }
    if (tipo_operacion!= 'L'){
      MensajeConfirmacion("Reversar cobranza " +  id_operacion +"?",function(){
          fetchProcesar("/cobranzas/reversarcobranza/" +  operacion_id + "/"
            + tipo_operacion,  function(){
              location.reload();
          })
      })
    }else{
      ReversarliquidacionCobranza(operacion_id)
    }
      
}

function ImprimirAsignacion(id, ){
  // en una nueva ventana abrir el reporte de asignación
  url = window.location.origin
  url = url + "/operaciones/reporteasignacion/"+id;
window.open( url);

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

function ImprimirCobranzaCargos(cobranza_id){
  // en una nueva ventana abrir el reporte de cobranza
  url = window.location.origin
  url = url + "/cobranzas/reportecobranzacargos/"+cobranza_id;
window.open( url);

}

function ImprimirLiquidacionCobranza(id, ){
  // en una nueva ventana abrir el reporte de asignación
  url = window.location.origin
  url = url + "/cobranzas/reporteliquidacion/"+id;
window.open( url);

}

function ReversarliquidacionCobranza(liquidacion_id,){
  // este proceso a diferencia de aceptar no se ejecuta desde un
  // formulario por eso no usa fetchPostear

  MensajeConfirmacion("Reversar liquidación " +  liquidacion_id +"?",function(){
      fetchProcesar("/cobranzas/reversarliquidacion/"+liquidacion_id, function(){
          location.reload();
      })
  })
    
}

function ImprimirCobranzaCargos(cobranza_id){
  // en una nueva ventana abrir el reporte de cobranza
  url = window.location.origin
  url = url + "/cobranzas/reportecobranzacargos/"+cobranza_id;
  window.open( url);

}

function AmpliacionDePlazo(tipo_asignacion){
  // la ampliacion sólo aplica a documentos que se han anticipado el 100%
  var seleccion=  $table.bootstrapTable('getSelections')
  var ids = getIdSelections()
  var id_cliente = ''
  var error = false
  var tipo_factoring=''

  seleccion.map(function(row)  {
    // validar un solo cliente
    if (id_cliente==''){
      id_cliente=row.IdCliente
    }
    else{ if (id_cliente != row.IdCliente){
      error = true
    }}
    // validar un solo tipo de factoring. Aunque este campo no aparece en la bt, 
    // si está en el data con que se carga la bt
    if (tipo_factoring==''){
      tipo_factoring=row.IdTipoFactoring
    }
    else{ if (tipo_factoring != row.IdTipoFactoring){
        error = true
    }}
    // solo los tipos de factoring que anticipan el 100%
    if ( !row.Anticipa100){
      error = true
    }
  });

  if (error ){
    alert("Ha seleccionado varios clientes o tipos de factoring que no aplican a ampliaciones. No puede continuar")
  }
  else{
    url = '/cobranzas/ampliaciondeplazo/'+ids+'/'+tipo_factoring+'/'
      +tipo_asignacion+'/'+id_cliente
    
    location.href=url
  }
  return false
}

function Prorroga(id, tipo_asignacion, vencimiento, documento){
  // si el id es negativo es un accesorio quitado que aparece en la cartera vencida
  if (id < 0){
    id = -id
    tipo_asignacion='A'
  }
  AbrirModal("/cobranzas/prorroga/"+ id + '/' + tipo_asignacion
    +'/'+vencimiento+'/'+documento)
}

function ImprimirAmpliacionPlazo(ampliacion_id){
  // en una nueva ventana abrir el reporte de cobranza
  url = window.location.origin
  url = url + "/cobranzas/reporteampliacion/"+ampliacion_id;
  window.open( url);

}
