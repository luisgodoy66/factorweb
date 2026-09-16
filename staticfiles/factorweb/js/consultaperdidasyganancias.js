var $btnConsultar = jQuery('#btnConsultar')

window.onload=function(){

    $btnConsultar.click(function () {

        var select = document.getElementById('cmb_mes');
        var mes = select.options[select.selectedIndex].value;
        
        ConsultaPYG(capturaValor('añocorte'), mes)
    })
 
};
    
function ConsultaPYG(año,mes){
        
    // en una nueva ventana abrir el reporte de asignación
    url = window.location.origin
    url = url + "/contabilidad/reporteperdidasyganancias/"+año+"/"+mes;
    window.open( url);
}
