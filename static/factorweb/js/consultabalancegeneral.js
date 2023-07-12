var $btnConsultar = jQuery('#btnConsultar')
var $btnBloquear = jQuery('#btnBloquear')

window.onload=function(){

    $btnConsultar.click(function () {

        var select = document.getElementById('cmb_mes');
        var mes = select.options[select.selectedIndex].value;

        ConsultaBG(capturaValor('añocorte'), mes)
    })

    $btnBloquear.click(function () {
        var select = document.getElementById('cmb_mes');
        var mes = select.options[select.selectedIndex].value;

        BloquearMes(capturaValor('añocorte'), mes)
    })

};
    
function ConsultaBG(año,mes){
        
    // en una nueva ventana abrir el reporte de asignación
    url = window.location.origin
    url = url + "/contabilidad/reportebalancegeneral/"+año+"/"+mes;
    window.open( url);
}

function BloquearMes(año, mes){
    
    MensajeConfirmacion("Continúa con el bloqueo del mes?", function(){
        fetchProcesar("/contabilidad/cierredemes/"+año+"/"+mes, function(){
            MensajeOK("Mes ha sido bloqueado")
        })
    })
}