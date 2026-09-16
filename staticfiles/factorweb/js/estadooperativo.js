var $table = jQuery('#table')
var $tbcheques = jQuery('#tbcheques')
var $tbcargos = jQuery('#tbcargos')
var $tbprotestos = jQuery('#tbprotestos')
var $tbcanjes = jQuery('#tbcanjes')
var $tbquitados = jQuery('#tbquitados')
const cliente_id = capturaValor("id_cliente")

window.onload=function(){

$table.bootstrapTable({locale:"es-EC"});
$tbcargos.bootstrapTable({locale:"es-EC"});
$tbcheques.bootstrapTable({locale:"es-EC"});
$tbprotestos.bootstrapTable({locale:"es-EC"});
$tbcanjes.bootstrapTable({locale:"es-EC"});
$tbquitados.bootstrapTable({locale:"es-EC"});

antigüedadcartera("/operaciones/antigüedadcarteracliente/"+cliente_id);
}