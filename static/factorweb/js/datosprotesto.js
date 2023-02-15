const tipo_operacion = capturaValor("tipo_operacion")

window.onload=function(){
    // objeto_fechas("#id_dprotesto")
}

function AceptarProtesto(){
  
  MensajeConfirmacion("Aceptar el protesto de " + capturaValor("codigo_cobranza") +"?"
    ,function(){
      var tipo

    if (tipo_operacion=='Cobranza') {tipo = 'C'} else {tipo = 'R'}

    var objeto={
        "id_cliente":capturaValor("id_cliente"),
        "tipo_factoring":capturaValor("tipo_factoring"),
        "forma_cobro":capturaValor("forma_cobro"),
        "id_cobranza" :capturaValor("id_cobranza"),
        "codigo_cobranza" : capturaValor("codigo_cobranza"),
        "id_cheque":capturaValor("id_cheque"),
        "valor" :capturaValor("valor_cheque"), 
        "fecha_protesto":capturaValor("id_dprotesto"), 
        "valor_nd": capturaValor("id_nvalornotadebito"), 
        "motivoprotesto" : capturaValor("id_motivoprotesto"),
        "tipo_emisor":capturaValor("tipo_emisor"),
        "id_accesorio":capturaValor("id_accesorio"),
        "tipo_operacion":tipo
          }
          
    fetchPostear("/cobranzas/aceptarprotesto/", objeto, function(data){
          // regresar a la lista de solicitudes
          window.location.href = "/cobranzas/listacobranzasporconfirmar";
          // en una nueva ventana abrir el reporte de cobranza
           url = window.location.origin
           if (tipo_operacion=="Cobranza"){
            url = url + "/cobranzas/reportecobranzacartera/"+data;
           }
           else{
            url = url + "/cobranzas/reporterecuperacion/"+data;
           }
           window.open( url);
        })
    })       
  }
   
  