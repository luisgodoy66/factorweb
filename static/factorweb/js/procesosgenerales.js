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

function ImprimirAsientoDiario(id, tipo){
  // en una nueva ventana abrir el reporte de asignación
  url = window.location.origin
  if (tipo == 'D')
    url = url + "/contabilidad/imprimirdiariocontable/"+id;
  else
    url = url + "/contabilidad/imprimircomprobanteegreso/"+id;
  
  window.open( url);

}

function antigüedadcartera(url){
  // chart antigüedad de la cartera
  fetchRecuperar(url,function(data){
      var ctx = document.getElementById( "singelBarChart" );
      ctx.height = 150;

      if (data["facturas"]){
          v90m = data["facturas"]["fvencido_mas_90"]
          v90 = data["facturas"]["fvencido_90"]
          v60 = data["facturas"]["fvencido_60"]
          v30 = data["facturas"]["fvencido_30"]
          p30 = data["facturas"]["fporvencer_30"]
          p60 = data["facturas"]["fporvencer_60"]
          p90 = data["facturas"]["fporvencer_90"]
          p90m = data["facturas"]["fporvencer_mas_90"]
      }
      else{
          v90m=0;v90=0;v60=0;v30=0; p30=0; p60=0; p90=0; p90m=0
      }

      if (data["accesorios"]){
          av90m = data["accesorios"]["vencido_mas_90"]
          av90 = data["accesorios"]["vencido_90"]
          av60 = data["accesorios"]["vencido_60"]
          av30 = data["accesorios"]["vencido_30"]
          ap30 = data["accesorios"]["porvencer_30"]
          ap60 = data["accesorios"]["porvencer_60"]
          ap90 = data["accesorios"]["porvencer_90"]
          ap90m = data["accesorios"]["porvencer_mas_90"]
      }
      else{
          av90m=0;av90=0;av60=0;av30=0; ap30=0; ap60=0; ap90=0; ap90m=0
      }
      
      if (data["protestos"]){
          pv90m = data["protestos"]["pvencido_mas_90"]
          pv90 = data["protestos"]["pvencido_90"]
          pv60 = data["protestos"]["pvencido_60"]
          pv30 = data["protestos"]["pvencido_30"]
          pp30 = data["protestos"]["pporvencer_30"]
          pp60 = data["protestos"]["pporvencer_60"]
          pp90 = data["protestos"]["pporvencer_90"]
          pp90m = data["protestos"]["pporvencer_mas_90"]
  }
      else{
          pv90m=0;pv90=0;pv60=0;pv30=0; pp30=0; pp60=0; pp90=0; pp90m=0
      }
      
      var myChart = new Chart( ctx, {
          type: 'bar',
          data: {
              labels: [ "v+90", "v90", "v60", "v30", "x30", "x60", "x90", "x+90" ],
              datasets: [
                  {
                      label: "Facturas",
                      data: [ v90m, v90, v60, v30, p30, p60, p90, p90m ],
                      borderColor: "rgba(0, 123, 255, 0.9)",
                      borderWidth: "0",
                      backgroundColor: "rgba(0, 123, 255, 0.5)"
                              },
                  {
                      label: "Accesorios",
                      data: [ av90m, av90, av60, av30, ap30, ap60, ap90, ap90m ],
                      borderColor: "rgba(0, 123, 255, 0.9)",
                      borderWidth: "0",
                      backgroundColor: "rgba(0, 255, 255, 0.5)"
                              },
                  {
                      label: "Protestos",
                      data: [ pv90m, pv90, pv60, pv30, pp30, pp60, pp90, pp90m ],
                      borderColor: "rgba(0, 123, 255, 0.9)",
                      borderWidth: "0",
                      backgroundColor: "rgba(255, 0, 0, 0.5)"
                              }
                          ]
          },
          options: {
              scales: {
                  yAxes: [ {
                      ticks: {
                          beginAtZero: true
                      }
                                  } ]
              }
          }
      } );

  })
}    

function ReversarAsientoDiario(asiento_id, asiento){
  MensajeConfirmacion("Reversar diario " +  asiento +"?",function(){
    fetchProcesar("/contabilidad/reversarasiento/"+asiento_id, function(){
        location.reload();
    })
})
}

function ModificarCobranza(cobranza_id, tipo_operacion, contabilizada){
  if (contabilizada){
    MensajeError("Cobranza ya está contabilizada. No se puede modificar.")
  }
  else{
    if (tipo_operacion == 'C' || tipo_operacion =='R'){
      AbrirModal("/cobranzas/modificarcobranza/"+ cobranza_id + '/' + tipo_operacion)
    }
    else{
      MensajeError("Solo puede modificar cobranzas y recuperaciones no protestadas.")
    }

  }

}