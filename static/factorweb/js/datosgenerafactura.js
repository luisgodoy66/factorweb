window.onload=function(){
    jQuery('#id_puntoemision')
        .change(function(){
        SecuenciaPorPuntoEmision( capturaValor("id_puntoemision"));
        });

    jQuery("#frmGenera").submit(function(e){
        e.preventDefault();
        var formData = jQuery("form").serializeArray();
        var token = jQuery("[name=csrfmiddlewaretoken]").val();
        // console.log(formData);
        jQuery.ajax({
            method:"POST",
            headers: {'X-CSRFToken': token },
            data: formData
        })
        .done(function(r,textStatus,xhr){
            if(xhr.status=200){
                MensajeOK('Archivo grabado en carpeta Descargas');
                location.href = "/contabilidad/listapendientesgenerarfactura";
                window.open('/contabilidad/imprimirdiariocontable/'+xhr.responseText);            
            }
            else{
                alert(textStatus);
            }
        }).fail(function (error) {
            MensajeError(error.responseText);
        });
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

function GenerarFactura(){
  MensajeConfirmacion("Aceptar generación de factura " 
    + capturaValor("id_cxnumerofactura") +"?",function(){
    
    var objeto={
        "tipo_operacion": capturaValor("tipo_operacion"),
        "id_operacion": capturaValor("id_operacion"),
        "id_puntoemision": capturaValor("id_puntoemision"),
        "id_cliente": capturaValor("id_cliente"),
        "base_iva" : capturaValor("id_nbaseiva"), 
        "base_noiva" : capturaValor("id_nbasenoiva"), 
        "concepto" : capturaValor("concepto"), 
        "emision" : capturaValor("id_demision"),
        "porcentaje_iva" : capturaValor("id_nporcentajeiva"),
        "ngao" : capturaValor("valor_gao"),
        "ndescuentocartera" : capturaValor("valor_dc"),
        "ngaoa" : capturaValor("valor_gaoa"),
        "niva" : capturaValor("id_niva"),
        "ndescuentocarteravencido" : capturaValor("valor_dcv"),
        }

    fetchPostear("/contabilidad/generarfacturadiario/", objeto, function(data){
        // regresar a la lista de generar factura
        window.location.href = "/contabilidad/listapendientesgenerarfactura";
        
        // en una nueva ventana abrir el reporte de asiento
        url = window.location.origin
        url = url + "/contabilidad/generarxmlfactura/"+data+"/"+capturaValor("concepto");
        window.open( url);
      })
  })
    
}
