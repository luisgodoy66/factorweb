// estos procesos corresponden a la confirmación de cobranzas depositadas en 
// cuentas conjuntas
var hay_transferencia = true
var hay_cargo = true

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();
    
    objeto_fechas("#id_dmovimiento")
    objeto_fechas("#id_dtransferencia")

    jQuery('input[type=checkbox][name="cargo"]').change(function() {
        toggle_cargo();
    });
    jQuery('input[type=checkbox][name="transferencia"]').change(function() {
        toggle_transferencia();
    });

};

function toggle_cargo(){
  const div_c = document.querySelector('#div_datos_cargo');
  let endendido = document.querySelector('input[name="cargo"]:checked');

 if (endendido == null){
    div_c.setAttribute('hidden',true);
}else{
    div_c.removeAttribute('hidden');
}
  }

function toggle_transferencia(){
  const div_c = document.querySelector('#div_datos_transferencia');
  let endendido = document.querySelector('input[name="transferencia"]:checked');

 if (endendido == null){
    div_c.setAttribute('hidden',true);
}else{
    div_c.removeAttribute('hidden');
}
  }

function ConfirmarCobranza(){
  let encendido_tr = document.querySelector('input[name="transferencia"]:checked');
  let encendido_cg = document.querySelector('input[name="cargo"]:checked');
  let valor_tr = capturaValor("id_ntransferencia")
  let valor_cg = capturaValor("id_nvalor")

  hay_transferencia = encendido_tr !== null;
  hay_cargo = encendido_cg !== null

  if (hay_transferencia & valor_tr ==0){
    alert('Ha especificado registro de transferencia y no ha indicado el valor de la misma')
    return false;
  }
  if (hay_cargo & valor_cg ==0){
    alert('Ha especificado registro de cargo y no ha indicado el valor del mismo')
    return false;
  }

  MensajeConfirmacion("Confirmar cobranza ?",function(){

    var objeto={
      "pstipooperacion": "C",
      "pncobranza": capturaValor("operacion"),
      "pltransferencia": hay_transferencia,
      "pntransferencia":capturaValor("id_ntransferencia"),
      "pndevolucion": capturaValor("id_ndevolucion"),
      "pncuentadestino":capturaValor("id_cuentadestino"),
      "pncuentaorigen" :capturaValor("cuentaconjunta"),
      "pdtransferencia": capturaValor("id_dtransferencia"),
      "plcargo":hay_cargo,
      "pncargo" :capturaValor("id_nvalor"),
      "psmotivo": capturaValor("id_ctmotivo"),
      "pdcargo": capturaValor("id_dmovimiento"),
        }

    fetchPostear("/cuentasconjuntas/aceptarconfirmacion/", objeto, function(data){
        // regresar a la lista de solicitudes
        window.location.href = "/cuentasconjuntas/listadocobranzasporconfirmar";
        // // en una nueva ventana abrir el reporte de cobranza
        // // hay que saber el id de la cobranza
        //  url = window.location.origin
        //  url = url + "/cobranzas/reportecobranzacartera/"+data;
        //  window.open( url);
      })
  })
     
}
