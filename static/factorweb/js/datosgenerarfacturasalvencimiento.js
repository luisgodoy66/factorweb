window.onload=function(){
    jQuery('#id_puntoemision')
        .change(function(){
        SecuenciaPorPuntoEmision( capturaValor("id_puntoemision"));
        });

    }  

function SecuenciaPorPuntoEmision( punto_emision){
    // bucar la secuencia de factura del punto de emisión seleccionado
    jQuery.ajax({
        type: "GET",
        url: "/contabilidad/obtenersecuenciafactura/"+punto_emision,
        data: { punto_emision: punto_emision, },
        success: function (data) {
            if (data.success) {
                jQuery("#id_cxnumerofactura").val(data.secuencia);

            } else {
                    jQuery("#id_cxnumerofactura").val("Error");
                }
            },
        error: function(xhr, status, error) {
            // this function is called if there is an error with the request
            console.log(error);
        }
        });
}

function GenerarFacturas(){
  MensajeConfirmacion("Aceptar generación de facturas desde " 
    + capturaValor("id_cxnumerofactura") +"?",function(){
    
    var objeto={
        "id_puntoemision": capturaValor("id_puntoemision"),
        "concepto" : capturaValor("concepto"), 
        "emision" : capturaValor("id_demision"),
        "id_factoring" : capturaValor("id_factoring"),
        "mes" : capturaValor("cmb_mes"),
        "año" : capturaValor("añocorte"),
        }

    fetchPostear("/contabilidad/generarfacturasalvencimiento/", objeto, function(data){
        // regresar a la lista de generar factura
        if (data==''){
            MensajeError('Ningún registro encontrado para el mes indicado.')
        }
        else{
            // barrer las facturas generadas y generar el XML
            fetchProcesar("/contabilidad/generarxmlfactura/"+data,function(asiento){
                // url = window.location.origin
                // url = url + "/contabilidad/imprimirdiariocontable/"+asiento;
                // window.open( url);
                alert('Revise los asientos generados.')
                window.location.href = "/contabilidad/listaasientoscontables";
            })
        }
      })
  })
    
}
