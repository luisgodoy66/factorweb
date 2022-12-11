var $table = jQuery('#table')
var selections = []

window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();
    
    // inicializar tabla
    initTable();
    // // cerrar side bar
    // CerrarSideBar();
  
};
window.operateEvents = {
    'click .remove': function (e, value, row, index) {
        EliminarDetalleDeCondicion( row.id)
    }
  };
  
function operateFormatter(value, row, index) {
    return [
        '<a class="remove" href="javascript:void(0)" title="Remove">',
        '<i class="fa fa-trash"></i>',
        '</a>'
    ].join('')
    }
    
function initTable() {
    $table.bootstrapTable('destroy').bootstrapTable({
      height: 550,
      locale: "es-EC",
      columns: [
        [{  title: 'Ref.', field: 'id', rowspan: 2
        , align: 'center', valign: 'middle', sortable: true,
          }, {title: 'Clase de cliente', field: 'ClaseCliente'
          , rowspan: 2
          , align: 'center', valign: 'middle', sortable: true
          }, {title: 'Clase de comprador', field: 'ClaseComprador'
          , rowspan: 2, align: 'center', valign: 'middle', sortable: true,
        }, 
        {title: 'Plazo', colspan: 2, align: 'center'
          }, {title: 'Porcentajes', colspan: 3, align: 'center'
          }, {field: 'operate', title: 'Acción'
          ,rowspan: 2
          , align: 'center', clickToSelect: false, 
          events: window.operateEvents, formatter: operateFormatter
          }],
        [
          {field: 'Desde', title: 'Desde', sortable: true
          }, {field: 'Hasta', title: 'Hasta', sortable: true, align: 'center', 
          }, {field: 'Porc_Anticipo', title: 'Anticipo', sortable: true, align: 'center'
          }, {field: 'Porc_GAO', title: 'Comisión', sortable: true, align: 'center'
          }, {field: 'Porc_DC', title: 'Descuento', sortable: true, align: 'center'
        }]
      ]
      
    })

  }

  function EliminarDetalleDeCondicion( detalle_id){
    MensajeConfirmacion("Eliminar detalle " + detalle_id  +"?",function(){
      fetchProcesar("/operaciones/eliminardetallecondicionoperativa/"+detalle_id, function(){
        // $table.bootstrapTable('remove', {
        //   field: 'id',
        //   values: [documento_id]
        // });
        location.reload();
      })
  })
  }