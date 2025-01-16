var $table = jQuery('#table')
var selections = []
var cliente_id = capturaValor("id_cliente")
var asignacion_id = capturaValor("asignacion_id")

window.onload=function(){
    initTable();
};

window.operateEvents = {
  'click .editar': function (e, value, row, index) {
    EditarDocumento( row.id)
  },
    'click .remove': function (e, value, row, index) {
      EliminarDocumentoDeSolicitudAsignacion(asignacion_id, row.id,'A', row.Documento)
    }
  };

function operateFormatter(value, row, index) {
return [
  '<a class="editar" href="javascript:void(0)" title="Editar cheque">',
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
          }, {title: 'Documento', field: 'Documento', rowspan: 2,
            align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Emisión', field: 'Emision', rowspan: 2,
            align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Cheques', colspan:5, align: 'center'
        }, {
            field: 'operate', title: 'Acción', align: 'center',
          clickToSelect: false, rowspan: 2, events: window.operateEvents
          ,align: 'center', valign: 'middle', formatter: operateFormatter
        }],
        [{field: 'Banco', title: 'Banco',
          sortable: true, align: 'center'
        }, {
          field: 'Cuenta', title: 'Cuenta', sortable: true,
          align: 'center'
        }, {
            field: 'Cheque', title: 'Cheque',
            sortable: true, align: 'center',
            footerFormatter: LineaCantidadEnPieDePaginaDeTabla
          }, {title: 'Vencimiento', field: 'Vencimiento', 
          align: 'center', valign: 'middle', sortable: true,
        }, {
            field: 'Total', title: 'Total', sortable: true,
            align: 'center', footerFormatter: LineaTotalValoresEnPieDepaginaDeTabla
          }]
      ]
    })
}

function NuevaAsignacion(){
  cliente_id=capturaValor("id_cxcliente");
  tipo_factoring=capturaValor("id_cxtipofactoring");
  
  if (cliente_id == "" || tipo_factoring==""){
    alert("debe especificar cliente y tipo de factoring")
  }
  else{
    url = '/solicitudes/nuevodocumentoconaccesorios/'
    +cliente_id+'/'+tipo_factoring;
    
    location.href=url
  }
  return false
}

function EditarDocumento( doc_id){
  tipo_factoring=capturaValor("id_cxtipofactoring");
  AbrirModal('/solicitudes/editarchequeaccesorio/'+doc_id+'/'+tipo_factoring )
}