// funciones operativas
function EliminarDocumentoDeSolicitudAsignacion(asignacion_id, documento_id, tipo_asignacion, documento){
    MensajeConfirmacion("Eliminar documento " + documento
        + " con referencia " + documento_id +"?",function(){

      fetchProcesar("/solicitudes/eliminardetalleasignacion/"
        + asignacion_id + "/" + documento_id+"/"+tipo_asignacion, function(){
        $table.bootstrapTable('remove', {
          field: 'id',
          values: [documento_id]
        });
        // location.reload();
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
     if (tipo=="P"){
      url = url + "/cobranzas/reportecobranzacuota/"+cobranza_id;
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

function ReversarAceptacionAsignacion(asignacion_id, codigo_asgn = ''){
  // este proceso a diferencia de aceptar no se ejecuta desde un
  // formulario por eso no usa fetchPostear

  MensajeConfirmacion("Reversar aceptación " +  codigo_asgn +"?",function(){
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

function Prorroga(id, tipo_asignacion, vencimiento, documento, por_vencer){
  // si el id es negativo es un accesorio quitado que aparece en la cartera vencida
  if (id < 0){
    id = -id
    tipo_asignacion='A'
  }
  AbrirModal("/cobranzas/prorroga/"+ id + '/' + tipo_asignacion
    +'/'+vencimiento+'/'+documento+'/'+por_vencer)
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
      
      if (data["pagares"]){
          cv90m = data["pagares"]["vencido_mas_90"]
          cv90 = data["pagares"]["vencido_90"]
          cv60 = data["pagares"]["vencido_60"]
          cv30 = data["pagares"]["vencido_30"]
          cp30 = data["pagares"]["porvencer_30"]
          cp60 = data["pagares"]["porvencer_60"]
          cp90 = data["pagares"]["porvencer_90"]
          cp90m = data["pagares"]["porvencer_mas_90"]
      }
      else{
          cv90m=0;cv90=0;cv60=0;cv30=0; cp30=0; cp60=0; cp90=0; cp90m=0
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
                      borderColor: "rgba(0, 255, 255, 0.5)",
                      borderWidth: "0",
                      backgroundColor: "rgba(0, 255, 255, 0.5)"
                              },
                  {
                      label: "Protestos",
                      data: [ pv90m, pv90, pv60, pv30, pp30, pp60, pp90, pp90m ],
                      borderColor: "rgba(255, 0, 0, 0.5)",
                      borderWidth: "0",
                      backgroundColor: "rgba(255, 0, 0, 0.5)"
                              },
                  {
                      label: "Reestructuración",
                      data: [ cv90m, cv90, cv60, cv30, cp30, cp60, cp90, cp90m ],
                      borderColor: "rgba(128, 0, 128, 0.5)",
                      borderWidth: "0",
                      backgroundColor: "rgba(128, 0, 128, 0.5)"
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

function EliminarDebitoCuentaCompartida(nd_id,){
  // este proceso a diferencia de aceptar no se ejecuta desde un
  // formulario por eso no usa fetchPostear

  MensajeConfirmacion("Eliminar débito " +  nd_id +"?",function(){
      fetchProcesar("/cuentasconjuntas/debitoeliminar/"+nd_id, function(){
          location.reload();
      })
  })
    
}

function CargaXMLfactura(xmlFile){
  const file = xmlFile.files[0];
  const reader = new FileReader();
  var parser = new DOMParser();

  reader.readAsText(file);

  reader.onload = function() {
      const xml = reader.result;
      // process the xml here
      var xmlDoc = parser.parseFromString(xml,"text/xml");
      if (xmlDoc.documentElement.localName != 'autorizacion'){
          alert('No corresponde')
      }
      else{
          let estado=xmlDoc.getElementsByTagName("estado")[0].childNodes[0].nodeValue ;

          if (estado != 'AUTORIZADO'){
              alert('Documento no tiene estado de autorizado')
          }
          else{
              comprobante = xmlDoc.getElementsByTagName("comprobante")[0].childNodes[0].nodeValue

              xmlFactura = parser.parseFromString(comprobante,"text/xml")

              let infoTributaria=xmlFactura.getElementsByTagName("infoTributaria")[0].childNodes ;

              for (let i in infoTributaria ){
                  switch (infoTributaria[i].nodeName ){
                      case "estab":
                      inicializaValor("id_ctserie1",infoTributaria[i].childNodes[0].nodeValue)
                      case "ptoEmi":
                      inicializaValor("id_ctserie2",infoTributaria[i].childNodes[0].nodeValue)
                      case "secuencial":
                      inicializaValor("id_ctdocumento",infoTributaria[i].childNodes[0].nodeValue)
                  }
              }

              let infoFactura=xmlFactura.getElementsByTagName("infoFactura")[0].childNodes ;
              
              for (let i in infoFactura ){
                  switch (infoFactura[i].nodeName){
                      case "razonSocialComprador":
                          inicializaValor("id_ctcomprador",infoFactura[i].childNodes[0].nodeValue);
                          break;
                      case "identificacionComprador":
                          inicializaValor("id_cxcomprador",infoFactura[i].childNodes[0].nodeValue);
                          break;
                      case "totalSinImpuestos":
                          inicializaValor("id_nvalorantesiva",infoFactura[i].childNodes[0].nodeValue);
                          break;
                      case "fechaEmision":
                          var fechaEmision = infoFactura[i].childNodes[0].nodeValue
                          var dateParts = fechaEmision.split("/");
                          var fecha= dateParts[2] + "-" + (dateParts[1]) + "-" + dateParts[0];
                          inicializaValor("id_demision",fecha)
                          break;
                      case "tipoIdentificacionComprador":
                          var tipo =infoFactura[i].childNodes[0].nodeValue
                          switch (tipo) {
                              case '04': inicializaValor("cxtipoid",'R'); break;
                              case '05': inicializaValor("cxtipoid",'C'); break;
                              case '06': inicializaValor("cxtipoid",'P'); break;
                              case '08': inicializaValor("cxtipoid",'O'); break;
                          }
                          break;
                  }
                  
              }
              let detalles =xmlFactura.getElementsByTagName("detalles")[0].childNodes ;
              valorIva=0;

              for (let i in detalles ){
                  detalle1=detalles[i].childNodes
                  for (let j in detalle1){
                      if (detalle1[j].nodeName=="impuestos"){
                          impuesto1=detalle1[j].childNodes
                          for (let k in impuesto1 ){
                              nodo = impuesto1[k].childNodes
                              iva_imp=false
                              for (let l in nodo){
                                  if(nodo[l].nodeName=='codigo'){
                                      if (nodo[l].childNodes[0].nodeValue='2'){iva_imp = true}
                                  }
                                  if (iva_imp & nodo[l].nodeName== "valor"){
                                      valorIva += parseFloat((parseFloat(nodo[l].childNodes[0].nodeValue)*1).toFixed(3))
                                      }
                              }
                          }
                      }
                  }
              }
              inicializaValor("id_niva",valorIva)
              total=jQuery("#id_nvalorantesiva").val()
              total = +total+valorIva;
              inicializaValor("id_ntotal",total.toFixed(2))
              
          }
      }
};

}

function ProrrogaStyle(value, row, index) {
  var classes = [
    'bg-blue',
    'bg-green',
    'bg-orange',
    'bg-yellow',
    'bg-red'
  ]

  if (row.Prorroga == 0) {
    return {
      css: {
        color: 'black'
      }
      }
  }
  return {
    css: {
      color: 'blue'
    }
  }
}

function generarXMLFactura(factura, ambiente){
  // nota: marcar la factura como ya generado XML
    window.location.href = "/contabilidad/generarxmlfactura/"+factura+"/"+ambiente;

}

function generaAnexos(id_asignacion, tipo_cliente){
  // nota: marcar la factura como ya generado XML
  fetchRecuperar('/operaciones/anexosactivos/'+tipo_cliente, function(anexos){
    for (let a = 0; a < anexos.length; a++){
      let anexo = anexos[a]
      window.location.href = "/operaciones/generaranexo/"+id_asignacion+"/"+anexo
      if (anexos.length >1){
        alert('Un anexo generado.')
      }
      // // marcar asignación como anexos generados
      // if (a == anexos.length - 1 ){
      //   fetchProcesar('/operaciones/marcaanexogenerado/'+id_asignacion, function(){
      //     location.reload()
      //   })

      // }
    }

  })


}

function carteranegociada(url){

    //line chart
  fetchRecuperar(url,function(cartera){
      var ctx = document.getElementById( "lineChart" );
    ctx.height = 150;
    var myChart = new Chart( ctx, {
        type: 'line',
        data: {
            labels: [ "Ene", "Feb", "Mar", "Abr", "May", "Jun"
              , "Jul" , "Ago", "Sep", "Oct", "Nov", "Dic"],
            datasets: [
                {
                    label: "Año anterior",
                    borderColor: "rgba(0,0,0,.09)",
                    borderWidth: "1",
                    backgroundColor: "rgba(0,0,0,.07)",
                    data: [ cartera['anterior']['enero']
                      , cartera['anterior']['febrero']
                      , cartera['anterior']['marzo']
                      , cartera['anterior']['abril']
                      , cartera['anterior']['mayo']
                      , cartera['anterior']['junio']
                      , cartera['anterior']['julio'] 
                      , cartera['anterior']['agosto'] 
                      , cartera['anterior']['septiembre'] 
                      , cartera['anterior']['octubre'] 
                      , cartera['anterior']['noviembre'] 
                      , cartera['anterior']['diciembre'] 
                    ]
                            },
                {
                    label: "Año actual",
                    borderColor: "rgba(0, 123, 255, 0.9)",
                    borderWidth: "1",
                    backgroundColor: "rgba(0, 123, 255, 0.5)",
                    pointHighlightStroke: "rgba(26,179,148,1)",
                    data: [ cartera['actual']['enero']
                      , cartera['actual']['febrero']
                      , cartera['actual']['marzo']
                      , cartera['actual']['abril']
                      , cartera['actual']['mayo']
                      , cartera['actual']['junio']
                      , cartera['actual']['julio'] 
                      , cartera['actual']['agosto'] 
                      , cartera['actual']['septiembre'] 
                      , cartera['actual']['octubre'] 
                      , cartera['actual']['noviembre'] 
                      , cartera['actual']['diciembre'] 
                    ]
                            }
                        ]
        },
        options: {
            responsive: true,
            tooltips: {
                mode: 'index',
                intersect: false
            },
            hover: {
                mode: 'nearest',
                intersect: true
            }

        }
    } );
  })
}

function ingresosGenerados(url){

  fetchRecuperar(url,function(cartera){
      var ctx = document.getElementById( "IngresosGenerados" );
    ctx.height = 150;
    var myChart = new Chart( ctx, {
        type: 'bar',
        data: {
            labels: [ "Ene", "Feb", "Mar", "Abr", "May", "Jun"
              , "Jul" , "Ago", "Sep", "Oct", "Nov", "Dic"],
            datasets: [
                {
                    label: "Año anterior",
                    borderColor: "rgba(0,0,0,.09)",
                    borderWidth: "1",
                    backgroundColor: "rgba(0,0,0,.07)",
                    data: [ cartera['anterior']['enero']
                      , cartera['anterior']['febrero']
                      , cartera['anterior']['marzo']
                      , cartera['anterior']['abril']
                      , cartera['anterior']['mayo']
                      , cartera['anterior']['junio']
                      , cartera['anterior']['julio'] 
                      , cartera['anterior']['agosto'] 
                      , cartera['anterior']['septiembre'] 
                      , cartera['anterior']['octubre'] 
                      , cartera['anterior']['noviembre'] 
                      , cartera['anterior']['diciembre'] 
                    ]
                            },
                {
                    label: "Año actual",
                    borderColor: "rgba(0, 123, 255, 0.9)",
                    borderWidth: "1",
                    backgroundColor: "rgba(0, 123, 255, 0.5)",
                    pointHighlightStroke: "rgba(26,179,148,1)",
                    data: [ cartera['actual']['enero']
                      , cartera['actual']['febrero']
                      , cartera['actual']['marzo']
                      , cartera['actual']['abril']
                      , cartera['actual']['mayo']
                      , cartera['actual']['junio']
                      , cartera['actual']['julio'] 
                      , cartera['actual']['agosto'] 
                      , cartera['actual']['septiembre'] 
                      , cartera['actual']['octubre'] 
                      , cartera['actual']['noviembre'] 
                      , cartera['actual']['diciembre'] 
                    ]
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

function CargaXMLOperacion(xmlFile){
  return new Promise((resolve, reject) => {

  const file = xmlFile.files[0];
  const reader = new FileReader();

  reader.readAsText(file);
  reader.onerror = function(event) {
    reject(new Error("Error al leer el archivo"));
  };
  reader.onload = function() {
      const xml = reader.result;
      var parser = new DOMParser();
      // process the xml here
      var xmlDoc = parser.parseFromString(xml,"text/xml");

      if (xmlDoc.documentElement.localName != 'ASIGNACION'){
        alert('No corresponde')
        reject(new Error('No corresponde'));          
      }
      else{
          let cliente = xmlDoc.getElementsByTagName("CLIENTE")[0].childNodes;
          for (let i in cliente){
            switch(cliente[i].nodeName){
              case "RUC":
                ruc_cliente = cliente[i].childNodes[0].nodeValue;
                break;
              case "NOMBRE":
                nombre_cliente = cliente[i].childNodes[0].nodeValue;
                break;
            }
          }

          let tipo_operacion = xmlDoc.getElementsByTagName("TIPO")[0].childNodes[0].nodeValue
          let tipo_factoring = xmlDoc.getElementsByTagName("TIPOFAC")[0].childNodes[0].nodeValue ;
          let lista = xmlDoc.getElementsByTagName("LISTA")[0].children ;
          let documentos = lista[0].children
          
          valorNegociado=0;
          cantidad =0;

          let docs = []; // Paso 1

          for (let i in documentos) {
              let detalle1 = documentos[i].children;
              let objetoDetalle = {}; // Paso 2

              for (let j in detalle1) {
                if (detalle1[j].nodeName != undefined && detalle1[j].childNodes.length > 0) {
                  switch (detalle1[j].nodeName) {
                      case "TIPIDCOMP":
                          objetoDetalle.tipo_id_comprador = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "RUCCOMP":
                          objetoDetalle.ruc_comprador = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "NOMBRECOMP":
                          objetoDetalle.nombre_comprador = detalle1[j].childNodes[0].nodeValue;
                          break;
                      // case "DOCTIPO":
                      //     objetoDetalle.tipo_documento = detalle1[j].childNodes[0].nodeValue;
                      //     break;
                      case "SERIE1":
                          objetoDetalle.serie1 = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "SERIE2":
                          objetoDetalle.serie2 = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "NUMFACTURA":
                          objetoDetalle.numero_documento = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "EMISION":
                          objetoDetalle.emision = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "ACCTIPO" && tipo_operacion == 'A':
                          objetoDetalle.tipo_accesorio = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "BANCO" && tipo_operacion == 'A':
                          objetoDetalle.banco_accesorio = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "CTA" && tipo_operacion == 'A':
                          objetoDetalle.cuenta_accesorio = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "CHEQUE" && tipo_operacion == 'A':
                          objetoDetalle.cheque_accesorio = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "PLAZA" && tipo_operacion == 'A':
                          objetoDetalle.plaza_accesorio = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "GIRADOR" && tipo_operacion == 'A':
                          objetoDetalle.girador_accesorio = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "VENCIMIENTO":
                          objetoDetalle.vencimiento = detalle1[j].childNodes[0].nodeValue;
                          break;
                      case "VALORANTESDEIVA":
                          objetoDetalle.valor_antes_iva = parseFloat((parseFloat(detalle1[j].childNodes[0].nodeValue) * 1).toFixed(3));
                          break;
                      case "IVA":
                          objetoDetalle.valor_iva = parseFloat((parseFloat(detalle1[j].childNodes[0].nodeValue) * 1).toFixed(3));
                          break;
                      case "RETENCIONIVA":
                          objetoDetalle.retencion_iva = parseFloat((parseFloat(detalle1[j].childNodes[0].nodeValue) * 1).toFixed(3));
                          break;
                      case "RETENCIONRENTA":
                          objetoDetalle.retencion_renta = parseFloat((parseFloat(detalle1[j].childNodes[0].nodeValue) * 1).toFixed(3));
                          break;
                      case "VALORADESCARTAR":
                          objetoDetalle.descartar = parseFloat((parseFloat(detalle1[j].childNodes[0].nodeValue) * 1).toFixed(3));
                          break;
                      case "MONTO":
                        objetoDetalle.total = objetoDetalle.valor_antes_iva 
                                          + objetoDetalle.valor_iva 
                                          - objetoDetalle.retencion_iva 
                                          - objetoDetalle.retencion_renta
                                          - objetoDetalle.descartar;
                        objetoDetalle.total = parseFloat(objetoDetalle.total).toFixed(2);
                        valorNegociado +=  parseFloat(objetoDetalle.total);
                        cantidad += 1;
                  }
                }
              }
              if (detalle1 != undefined){
                docs.push(objetoDetalle); // Paso 5
              }
          }
          
          resultado = {
            id_cliente: ruc_cliente,
            nombre_cliente: nombre_cliente,
            tipo_factoring : tipo_factoring,
            tipo_operacion: tipo_operacion,
            numero_documentos: cantidad,
            total_negociado : parseFloat(valorNegociado).toFixed(2),
            documentos: docs,
          }
    }
    resolve(resultado);
};

});
}

function ReversarAceptacionPagare(asignacion_id, codigo_asgn = ''){
  // este proceso a diferencia de aceptar no se ejecuta desde un
  // formulario por eso no usa fetchPostear

  MensajeConfirmacion("Reversar pagaré " +  codigo_asgn +"?",function(){
      fetchProcesar("/operaciones/reversaraceptacionpagare/"+  asignacion_id,  function(){
          location.reload();
      })
  })
    
}

function ReversarDesembolso(desembolso_id, tipo_operacion, operacion, asiento){
  // este proceso a diferencia de aceptar no se ejecuta desde un
  // formulario por eso no usa fetchPostear

  if (asiento ){
    MensajeError("Desembolso tiene asiento contable. No se puede reversar.")
  }
  else{
    MensajeConfirmacion("Reversar el desembolso de la operación " +  operacion +"?",function(){
      if (tipo_operacion == 'A'){
        fetchProcesar("/operaciones/reversardesembolsoasignacion/"+ desembolso_id, function(){
            location.reload();
        })
      }
      if (tipo_operacion == 'C'){
        fetchProcesar("/cobranzas/reversardesembolsoliquidacion/"+ desembolso_id, function(){
            location.reload();
        })
      }
    })  
  }
    
}

