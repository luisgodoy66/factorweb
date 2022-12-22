var $table = jQuery('#table')
var selections = []
var cliente_id = capturaValor("id_cxparticipante")

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();

    // inicializar tabla
    initTable();

    // // cerrar side bar
    // CerrarSideBar();
  
};

window.operateEvents = {
  'click .like': function (e, value, row, index) {
    MarcarCuentaTransferencia(row.id,cliente_id)
  },
    'click .remove': function (e, value, row, index) {
      EliminarCuentaBancaria( row.id)
    }
};

function operateFormatter(value, row, index) {
return [
  '<a class="like" href="javascript:void(0)" title="Default transferencias">',
  '<i class="fa fa-heart"></i>',
  '</a>  ',
  '<a class="remove" href="javascript:void(0)" title="Eliminar">',
    '<i class="fa fa-trash"></i>',
    '</a>'
].join('')
}
function initTable() {

  $table.bootstrapTable('destroy').bootstrapTable({
    height: 450,
    locale: "es-EC",
    columns: [
      [{title: 'Ref.', field: 'id', rowspan: 2, align: 'center',
        valign: 'middle', sortable: true,
        footerFormatter: LineaTotalEnPieDePaginaDeTabla
      }, {title: 'Banco', field: 'Banco', rowspan: 2,
          align: 'center', valign: 'middle', sortable: true,
          footerFormatter: LineaCantidadEnPieDePaginaDeTabla
        }, {title: 'Tipo de cuenta', field: 'TipoCuenta', rowspan: 2,
          align: 'center', valign: 'middle', sortable: true,
        }, {title: 'Cuenta', field: 'Cuenta', rowspan: 2,
          align: 'center', valign: 'middle', sortable: true,
        }, {title: 'Propia', field: 'Propia', rowspan: 2,
          align: 'center', valign: 'middle', sortable: true,
        }, {title: 'Activa', field: 'Activa', rowspan: 2,
        align: 'center', valign: 'middle', sortable: true,
      }, {title: 'Recibe transferencia', field: 'Default', rowspan: 2,
      align: 'center', valign: 'middle', sortable: true,
      }, {title: 'Propietario', colspan: 2, align: 'center'
      }, {field: 'operate', title: 'Acción', align: 'center',valign: 'middle',
        clickToSelect: false, events: window.operateEvents,rowspan: 2,
        formatter: operateFormatter
      }],
      [{field: 'IdPropietario', title: 'Id.',
        sortable: true, 
        align: 'center'
        }, {
          field: 'Propietario', title: 'Propietario', sortable: true,
          align: 'center'          
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

function EliminarCuentaBancaria( documento_id){
  MensajeConfirmacion("Eliminar cuenta bancaria " + documento_id + "?",function(){

    fetchProcesar("/clientes/eliminarcuentabancaria/"+ documento_id, function(){
      // $table.bootstrapTable('remove', {
      //   field: 'id',
      //   values: [documento_id]
      // });
      location.reload();
    })
})
}

function MarcarCuentaTransferencia( documento_id, cliente_id){
  MensajeConfirmacion("Establecer como cuenta para transferencias " + documento_id + "?",function(){

    fetchProcesar("/clientes/actualizarcuentatransferencia/"
      + documento_id + "/" + cliente_id, function(){
      location.reload();
    })
})
}
