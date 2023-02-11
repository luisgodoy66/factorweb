var $table = jQuery('#table')
var selections = []
var cliente_id = capturaValor("id_cliente")
var asignacion_id = capturaValor("asignacion_id")

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();

    // // inicializar valores
    // inicializaValor("cliente_id",cliente_id)
    
    // // configuar select
    // jQuery(".standardSelect").chosen({
    //     disable_search_threshold: 10,
    //     no_results_text: "Cliente no encontrado!",
    //     width: "100%"
    // });

    // inicializar tabla
    initTable();
    // // cerrar side bar
    // CerrarSideBar();
  
};

window.operateEvents = {
  'click .editar': function (e, value, row, index) {
    EditarDocumento(asignacion_id,cliente_id,capturaValor("id_cxtipofactoring"), row.id)
  },
    'click .remove': function (e, value, row, index) {
      EliminarDocumentoDeSolicitudAsignacion(asignacion_id, row.id,'F', row.Documento)
    }
};

function operateFormatter(value, row, index) {
return [
  '<a class="editar" href="javascript:void(0)" title="Editar">',
  '<i class="fa fa-edit"></i>',
  '</a>',
  '<a class="remove" href="javascript:void(0)" title="Eliminar">',
  '<i class="fa fa-trash"></i>',
  '</a>'
].join('')
}

function initTable() {

    $table.bootstrapTable('destroy').bootstrapTable({
      height: 400,
      locale: "es-EC",
      columns: [
        [{title: 'Ref.', field: 'id', rowspan: 2, align: 'center',
          valign: 'middle', sortable: true,
          footerFormatter: LineaTotalEnPieDePaginaDeTabla
        }, {title: 'Deudor', field: 'Comprador', rowspan: 2,
            align: 'center', valign: 'middle', sortable: true,
            footerFormatter: LineaCantidadEnPieDePaginaDeTabla
          }, {title: 'Documento', field: 'Documento', rowspan: 2,
            align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Emisión', field: 'Emision', rowspan: 2,
            align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Vencimiento', field: 'Vencimiento', rowspan: 2,
            align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Valores', colspan: 5, align: 'center'
        }, {
            field: 'operate', title: 'Acción', align: 'center',rowspan: 2,
          clickToSelect: false, events: window.operateEvents,valign: 'middle',
          formatter: operateFormatter
        }],
        [{field: 'ValorAntesDeIVA', title: 'Antes de IVA',
          sortable: true, footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla,
          align: 'center'
        }, {
          field: 'IVA', title: 'IVA', sortable: true,
          align: 'center', footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }, {
            field: 'Retenciones', title: 'Retenciones',
            sortable: true, align: 'center',
            footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
        }, {
            field: 'NoNegociado', title: 'Descartado',
            sortable: true, align: 'center',
            footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }, {
            field: 'Total', title: 'Negociado', sortable: true,
            align: 'center', footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }]
      ]
    })
    // $table.on('check.bs.table uncheck.bs.table ' +
    //   'check-all.bs.table uncheck-all.bs.table',
    // function () {
    //   $remove.prop('disabled', !$table.bootstrapTable('getSelections').length)

    //   // save your data, here just save the current page
    //   selections = getIdSelections()
    //   // push or splice the selections if you want to save all data selections
    // })
    // $table.on('all.bs.table', function (e, name, args) {
    //   console.log(name, args)
    // })
    // $remove.click(function () {
    //   var ids = getIdSelections()
    //   $table.bootstrapTable('remove', {
    //     field: 'id',
    //     values: ids
    //   })
    //   $remove.prop('disabled', true)
    // })
}

function NuevaAsignacion(){
  cliente_id=capturaValor("cliente_id");
  tipo_factoring=capturaValor("id_cxtipofactoring");
  
  if (cliente_id == "" || tipo_factoring==""){
    alert("debe especificar cliente y tipo de factoring")
  }
  else{
    return AbrirModal('/solicitudes/nuevasolicitudfacturaspuras/'+cliente_id
    +'/'+tipo_factoring);
  }
}

function EditarDocumento(asignacion_id, cliente_id, tipofactoring_id, doc_id){
  AbrirModal('/solicitudes/editardocumentofacturaspuras/'+asignacion_id 
    +'/'+cliente_id +'/'+tipofactoring_id+'/'+doc_id )
}