window.onload=function(){

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
                location.href = "/contabilidad/listadesembolsospendientes";
                window.open('/contabilidad/imprimircomprobanteegreso/'+xhr.responseText);
            }
            else{
                alert(textStatus);
            }
        }).fail(function (error) {
            MensajeError(error.responseText);
        });
    });

    }  

function GenerarEgreso(){
    cuenta_pago = 'null'
    numero_cheque = 'null'
    cuenta_destino = 'null'

    if (capturaValor("forma_pago") == 'CHE') {
        numero_cheque = capturaValor("id_ctcheque")
    }
    if (capturaValor("forma_pago") == 'TRA') {
        cuenta_destino=capturaValor("id_cxcuentadestino")
        if (cuenta_destino==''){
            alert('Se especificó transferencia pero no se ha determinado cuenta de destino')
            return false;
        }
    }
    if (capturaValor("forma_pago") != 'EFE') {
        cuenta_pago = capturaValor("id_cxcuentapago")
    }
    
    MensajeConfirmacion("Aceptar generación de egreso ?",function(){
    
    var objeto={
        "psforma_pago": capturaValor("forma_pago"),
        "pid_desembolso" :capturaValor("id_desembolso"),
        "pscxbeneficiario" :capturaValor("id_cxbeneficiario"),
        "psrecibidopor" :capturaValor("id_ctrecibidopor"),
        "pid_cuentapago": cuenta_pago,
        "pscheque": numero_cheque,
        "pid_cuentadestino": cuenta_destino,
        "concepto" : capturaValor("concepto"), 
        "pdemision" :capturaValor("id_demision"),
        "pnvalor" :capturaValor("id_nvalor"),
        "pid_factura" :capturaValor("id_factura"),
            }
    fetchPostear("/contabilidad/generaregresodiario/", objeto, function(data){
        // regresar a la lista de generar factura
        window.location.href = "/contabilidad/listadesembolsospendientes";
        // en una nueva ventana abrir el reporte de asiento
        url = window.location.origin
        url = url + "/contabilidad/imprimircomprobanteegreso/"+data;
        window.open( url);
        
      })
  })
    
}
