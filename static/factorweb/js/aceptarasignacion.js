var $table = jQuery('#table')
var selections = []
var asignacion_id = capturaValor("asignacion_id")
var iva_gao = capturaValor("iva_gao")
var iva_dc = capturaValor("iva_dc")
var carga_gao = capturaValor("carga_gao")
var carga_dc = capturaValor("carga_dc")
var tipo_asignacion = capturaValor("tipo_asignacion")
var porcentaje_iva = capturaValor("porcentaje_iva")

window.onload=function(){
  //  // cerrar side bar
  //   CerrarSideBar();
 
   // inicializar el encabezado
    ActualizarHeader();

    // configuar cambios en los campos de fecha y valores y select
    jQuery('#condicion_id')
        .change(function(){
          RecalcularCargos(asignacion_id
            ,capturaValor("id_ddesembolso")
            ,capturaValor("condicion_id"));
        });

    jQuery('#id_ndescuentodecartera', '#id_ngao', '#id_nanticipo')
        .change(function(){
          Calcula_Neto();
          });
          
    jQuery('#id_ddesembolso')
        .change(function(){
          RecalcularCargos(asignacion_id,capturaValor("id_ddesembolso"), capturaValor("condicion_id"));
        });

    // // inicializar valores
    // objeto_fechas("#id_dnegociacion");
    // objeto_fechas("#id_ddesembolso");
    
    // inicializar tabla
    initTable();

    // mostrar valores
    RecalcularCargos(asignacion_id, capturaValor("id_ddesembolso"), capturaValor("condicion_id"));

  
};
function Calcula_Neto()
{
    var iva,total, anticipo;
    
    anticipo = jQuery("#id_nanticipo").val();
    anticipo = anticipo==="" ? 0 : +anticipo;

    iva =jQuery('#id_ntotalimpuesto1a').val();
    iva = iva==="" ? 0 : +iva;

    gao = jQuery('#id_ngao').val();
    gao = gao==="" ? 0 : +gao;

    descuento_cartera = jQuery('#id_ndescuentodecartera').val();
    descuento_cartera = descuento_cartera==="" ? 0 : +descuento_cartera;

    total = anticipo - gao - descuento_cartera - iva;

    jQuery('#id_nvalor').val(total);

};

window.operateEvents = {
  'click .like': function (e, value, row, index) {
    CambiarTasasDocumento(row.id,capturaValor("id_ddesembolso"),function(){
      // alert('refersacar')
    })
  },
  'click .remove': function (e, value, row, index) {
  EliminarDocumentoDeSolicitudAsignacion(asignacion_id, row.id, tipo_asignacion, row.Documento)
  }
};

function operateFormatter(value, row, index) {
  return [
    '<a class="like" href="javascript:void(0)" title="Configurar tasas">',
    '<i class="fa fa-cog"></i>',
    '</a>  ',
    '<a class="remove" href="javascript:void(0)" title="Eliminar">',
      '<i class="fa fa-trash"></i>',
      '</a>'
  ].join('')
}
  
function RecalcularCargos(asgn,fecha_desembolso, cond){
  // el formato usado es yyyy-mm-dd. Esta validación necesaria pues al digitar la fecha
  // su pueden tener meses y dias como '00'
  var isValid = fecha_desembolso.match(/^\d{4}(\-)(((0)[0-9])|((1)[0-2]))(\-)([0-2][0-9]|(3)[0-1])$/);

  if (isValid) {
    fetchProcesar("/operaciones/detallecargosasignacion/" + asgn + "/" 
        + fecha_desembolso + "/" + cond, function(){
            RefrescarTabla(asgn)
        }) 
  } 

}

function RefrescarTabla(asgn){
  // se invoca desde modal de cambio de tasa
  $table.bootstrapTable('refresh', {
    url: "/operaciones/refrescadetallesolicitud/" + asgn 
  });
  Suma_Cargos(asgn, iva_gao, iva_dc, carga_gao, carga_dc, porcentaje_iva )
}

function Suma_Cargos(asgn, iva_gao, iva_dc, carga_gao, carga_dc, porcentaje_iva){
  fetchRecuperar("/operaciones/sumacargos/"+asgn+"/"+iva_gao+"/"+iva_dc
              +"/"+carga_gao+"/"+carga_dc+"/"+porcentaje_iva
    , function(data){
    if (data){
      jQuery("#id_nanticipo").val(data['anticipo'])    
      jQuery("#id_ndescuentodecartera").val(data['dc'])
      jQuery("#id_ngao").val(data['gao'])    
      jQuery("#id_niva").val(data['iva'])    
      jQuery("#neto").val(data['neto'])    
      jQuery("#id_nvalor").val(data['negociado'])    
    }
  })
}

function initTable() {

    $table.bootstrapTable('destroy').bootstrapTable({
      locale: "es-EC",
      columns: [
        [{title: 'Ref.', field: 'id', rowspan: 2, align: 'center', valign: 'middle', 
          sortable: true, footerFormatter: LineaTotalEnPieDePaginaDeTabla
          }, {title: 'Deudor', field: 'Comprador', rowspan: 2, align: 'center', 
          valign: 'middle', sortable: true, footerFormatter: LineaCantidadEnPieDePaginaDeTabla
          }, {title: 'Documento', field: 'Documento', rowspan: 2, align: 'center', 
          valign: 'middle', sortable: true,
          }, {title: 'Emisión', field: 'Emision', rowspan: 2, align: 'center', 
          valign: 'middle', sortable: true,
          }, {title: 'Vencimiento', field: 'Vencimiento', rowspan: 2, align: 'center', 
          valign: 'middle', sortable: true,
          }, {title: 'Negociado', field: 'Total', rowspan: 2, align: 'center', valign: 'middle', 
          sortable: true, footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }, {title: 'Plazo', field: 'Plazo', rowspan: 2, align: 'center', valign: 'middle', 
          sortable: true, 
          }, {title: 'Anticipo', colspan: 2, align: 'center'
          }, {title: 'GAO', colspan: 2, align: 'center'
          }, {title: 'DC', colspan: 2, align: 'center'
          
          }, {field: 'operate', title: 'Acción',rowspan: 2, align: 'center', valign: 'middle'
          , clickToSelect: false, events: window.operateEvents, formatter: operateFormatter
          }],
        [{field: 'Porc_anticipo', title: '%', sortable: true
          }, {field: 'Valor_anticipo', title: 'valor', sortable: true, align: 'center', 
          footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }, {field: 'Porc_GAO', title: '%', sortable: true, align: 'center'
          }, {field: 'Valor_GAO', title: 'valor', sortable: true, align: 'center', 
          footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }, {field: 'Porc_DC', title: '%', sortable: true, align: 'center'
          }, {field: 'Valor_DC', title: 'valor', sortable: true, align: 'center', 
          footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }]
      ],
      
    })
}

function CambiarTasasDocumento(doc_id, fecha_desembolso, callback){
  AbrirModal("/operaciones/editartasasdocumento/"+ doc_id+"/"+fecha_desembolso+"/"+asignacion_id)
  
}

function AceptarAsignacion(){
  MensajeConfirmacion("Aceptar solicitud con desembolso el " 
    + capturaValor("id_ddesembolso") +"?",function(){
    
    var objeto={
        "id_asignacion":asignacion_id,
        "dnegociacion":capturaValor("id_dnegociacion"),
        "ddesembolso": capturaValor("id_ddesembolso"), 
        "nanticipo":capturaValor("id_nanticipo"),
        "ngao":capturaValor("id_ngao"), 
        "ndescuentocartera": capturaValor("id_ndescuentodecartera"),
        "niva": capturaValor("id_niva"),
        "sinstruccionpago": capturaValor("id_ctinstrucciondepago"),
      }
    fetchPostear("/operaciones/aceptardocumentos/", objeto, function(){
        // regresar a la lista de solicitudes
        window.location.href = "/solicitudes/listasolicitudes";
        
        // en una nueva ventana abrir el reporte de asignación
        url = window.location.origin
        url = url + "/operaciones/reporteasignaciondesdesolicitud/"+asignacion_id;
        window.open( url);
      })
  })
    
}
