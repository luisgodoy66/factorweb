var $table = jQuery('#table')
// data_cargos y data_cargos se cargan desde elementos tipo json.dumps que vienen 
// en el contexto
const cobranzastxt =capturaValor("data_cobranzas")
const cargostxt =capturaValor("data_cargos")
const neto = capturaValor("neto_id")
const tipo_operacion = capturaValor("tipo_operacion")
const otroscargostxt =capturaValor("data_otros_cargos")
var $tableotros = jQuery('#table_otros')

window.onload= function(){

    // para cargar la data en la tabla se necesita convertir, se usa JSON.parse
    data = JSON.parse(cargostxt)

    $table.bootstrapTable('destroy').bootstrapTable({
        data: data,
        fixedColumns: true,
        fixedNumber: 3
})
    // para cargar la data en la tabla se necesita convertir, se usa JSON.parse
    otros = JSON.parse(otroscargostxt)

    $tableotros.bootstrapTable('destroy').bootstrapTable({
        data: otros,
})
}

function LiquidarCobranza(){
    MensajeConfirmacion("Aceptar liquidación con desembolso el " 
      + capturaValor("id_ddesembolso") +"?",function(){

        //para pasar el detalle al stored procedure se envia como llegó (json.dumps)
        var objeto={
          "id_cliente":capturaValor("cliente_id"),
          "fecha_liquidacion":capturaValor("id_dliquidacion"),
          "ddesembolso": capturaValor("id_ddesembolso"), 
          "valor_liquidacion":capturaValor("neto_id"),
          "tipo_factoring":capturaValor("tipo_factoring_id"), 
          "base_iva": capturaValor("base_iva_id"),
          "porcentaje_iva": capturaValor("porcentaje_iva_id"),
          "niva": capturaValor("iva_id"),
          "sinstruccionpago": capturaValor("id_ctinstrucciondepago"),
          "documentos": cargostxt,
          "vuelto":capturaValor("vuelto_id"),
          "sobrepago":capturaValor("sobrepago_id"),
          "gao":capturaValor("gao_id"),
          "gaoa":capturaValor("gaoa_id"),
          "descuentodecartera":capturaValor("dc_id"),
          "descuentodecarteravencido":capturaValor("dcv_id"),
          "retenciones":capturaValor("retenciones_id"),
          "bajas":capturaValor("bajas_id"),
          "otros":capturaValor("otros_id"),
          "neto":capturaValor("neto_id"),
          "cobranzas" : cobranzastxt,
          "otros_cargos":otroscargostxt,
        }

        fetchPostear("/cobranzas/liquidacion/"+tipo_operacion, objeto, function(data){
          // regresar a la lista de solicitudes
          window.location.href = "/cobranzas/listacobranzaspendientesliquidar";
          // en una nueva ventana abrir el reporte de asignación
          url = window.location.origin
          url = url + "/cobranzas/reporteliquidacion/"+data;
          window.open( url);
        })
    })
      
  }
  