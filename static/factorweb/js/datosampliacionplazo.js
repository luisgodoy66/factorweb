const $table = jQuery('#table')
const acumula_gao = capturaValor("acumula_gao")
const carga_dc = capturaValor("carga_dc")
const tipo_asignacion = capturaValor("tipo_asignacion")
const porcentaje_iva = capturaValor("porcentaje_iva")
const iva_gaoa = capturaValor("iva_gaoa")
const iva_dc = capturaValor("iva_dc")
const ids = capturaValor("ids")
const id_cliente = capturaValor("id_cliente")
var iniciales_dc = capturaValor("iniciales_dc")
var iniciales_gaoa = capturaValor("iniciales_gaoa")
var selections = []

window.onload=function(){
  //  // cerrar side bar
  //   CerrarSideBar();
 
   // inicializar el encabezado
    ActualizarHeader();
    // // configuar cambios en los campos de fecha y valores y select
    // jQuery('#id_ndescuentodecartera', '#id_ngao', '#id_nanticipo')
    //     .change(function(){
    //       Calcula_Neto();
    //       });
          
    jQuery('#fechacorte')
        .change(function(){
          RecalcularCargos(ids,capturaValor("fechacorte"));
        });

    // inicializar tabla
    if (iniciales_dc==''){iniciales_dc='DCAR'}
    if (iniciales_gaoa==''){iniciales_gaoa='GAOA'}

    initTable(iniciales_gaoa,iniciales_dc);

    // mostrar valores
    RecalcularCargos( ids, capturaValor("fechacorte"));

  };

  window.operateEvents = {
  'click .like': function (e, value, row, index) {
    CambiarTasasDocumento(row.id,capturaValor("id_ddesembolso"),function(){
    })
  },
};

function operateFormatter(value, row, index) {
  return [
    '<a class="like" href="javascript:void(0)" title="Configurar tasas">',
    '<i class="fa fa-cog"></i>',
    '</a>  '
  ].join('')
}
  
function RecalcularCargos(ids,fecha_corte){
  // el formato usado es yyyy-mm-dd. Esta validación necesaria pues al digitar la fecha
  // su pueden tener meses y dias como '00'
  var isValid = fecha_corte.match(/^\d{4}(\-)(((0)[0-9])|((1)[0-2]))(\-)([0-2][0-9]|(3)[0-1])$/);

  if (isValid) {
    fetchProcesar("/cobranzas/detallecargosampliaciondeplazo/"+ids+"/"+tipo_asignacion
      +"/"+ fecha_corte +"/" + carga_dc + "/" + acumula_gao + '/' + id_cliente, function(){
            RefrescarTabla(ids, tipo_asignacion)
        }) 
  } 

}

function RefrescarTabla(ids, tipo_asignacion){
  // se invoca desde modal de cambio de tasa
  $table.bootstrapTable('refresh', {
    url: "/cobranzas/refrescadetallecargosampliacionplazo/" + ids + "/" + tipo_asignacion
  });
  Suma_Cargos(ids, iva_gaoa, iva_dc, porcentaje_iva )
}

function Suma_Cargos(ids, iva_gaoa, iva_dc, porcentaje_iva){
  fetchRecuperar("/cobranzas/sumacargos/"+ids+"/"+tipo_asignacion+"/"+iva_gaoa+"/"
              +iva_dc+"/"+porcentaje_iva
    , function(data){
    if (data){
      jQuery("#id_ndescuentodecartera").val(data['dc'])
      jQuery("#id_ngaoa").val(data['gaoa'])    
      jQuery("#id_niva").val(data['iva'])    
      jQuery("#total").val(data['total'])    
    }
  })
}

function initTable(iniciales_GAOA, iniciales_DC) {

    $table.bootstrapTable('destroy').bootstrapTable({
      locale: "es-EC",
      columns: [
        [{title: 'Ref.', field: 'id', rowspan: 2, align: 'center', valign: 'middle', 
          sortable: true, footerFormatter: LineaTotalEnPieDePaginaDeTabla
          }, {title: 'Asignación', field: 'Asignacion', rowspan: 2, align: 'center', 
          valign: 'middle', sortable: true, footerFormatter: LineaCantidadEnPieDePaginaDeTabla
          }, {title: 'Documento', field: 'Documento', rowspan: 2, align: 'center', 
          valign: 'middle', sortable: true,
          }, {title: 'Saldo', field: 'Saldo', rowspan: 2, align: 'center', valign: 'middle', 
          sortable: true, footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }, {title: 'Última generación', field: 'UltimaGeneracioncargos', rowspan: 2, align: 'center', 
          valign: 'middle', sortable: true,
          }, {title: 'Plazo', field: 'Plazo', rowspan: 2, align: 'center', valign: 'middle', 
          sortable: true, 
          }, {title: iniciales_GAOA, colspan: 2, align: 'center'
          }, {title: iniciales_DC, colspan: 2, align: 'center'
          
          }, {field: 'operate', title: 'Acción',rowspan: 2, align: 'center', valign: 'middle'
          , clickToSelect: false, events: window.operateEvents, formatter: operateFormatter
          }],
        [ {field: 'Tasa_GAOA', title: '%', sortable: true, align: 'center'
          }, {field: 'Valor_GAOA', title: 'valor', sortable: true, align: 'center', 
          footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }, {field: 'Tasa_DC', title: '%', sortable: true, align: 'center'
          }, {field: 'Valor_DC', title: 'valor', sortable: true, align: 'center', 
          footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }]
      ],
      
    })
}

function CambiarTasasDocumento(doc_id, fecha_desembolso, callback){
  AbrirModal("/operaciones/editartasasdocumento/"+ doc_id+"/"+fecha_desembolso+"/"
    +asignacion_id)
  
}

function AceptarAmpliacionPlazo(){
  MensajeConfirmacion("Aceptar ampliación de plazo para el " 
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
