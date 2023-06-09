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
            alert('done')
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
