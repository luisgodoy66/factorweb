var linea 

window.onload=function(){

  if (diario != 'None') {
    // cargar el asiento contable y cargarlo en la tabla
    cargarTablaDiario(diario)
  }

  // validar antes de enviar
  jQuery("#frmAsiento").submit(function(e){

      var total_debe = 0
      var total_haber = 0

      e.preventDefault();
      
      jQuery("#body_asiento tr").each(function (i,row) {
            var valordebe = row.children[2].innerText
            var valorhaber = row.children[3].innerText
            total_debe += parseFloat( valordebe)
            total_haber += parseFloat( valorhaber)
      });
    
      if (total_debe != total_haber){
          alert("Totales de debe y haber no cuadran: " )
          return false;
      };

      inicializaValor("total_debe", total_debe)
      inicializaValor("total_haber", total_haber)

      // validar que el mes no este cerrado
      var fecha = document.getElementById("id_dcontabilizado").value
      var mes = fecha.split("-")[1]
      var anio = fecha.split("-")[0]
      fetchRecuperar("/contabilidad/mescerrado/"+anio+"/"+mes, function(data){
        if (data.mesbloqueado){
          MensajeError("El mes ya esta cerrado, no se puede modificar el asiento contable")
          return true;
        }
        else{
          // convertir la tabla de cheques en un dicconario para pasarlo en el contexto
          DicDiario = new Array();

          jQuery("#body_asiento tr").each(function (i,row) {

            var referencia = row.children[1].innerText
            var debe = row.children[2].innerText
            var haber = row.children[3].innerText
            var cuenta = row.children[4].innerText
            var tipo = row.children[5].innerText

            DicDiario.push({          
              cuenta: cuenta,
              tipo: tipo,
              referencia: referencia,
              debe: debe,
              haber: haber,  
              id_linea: row.children[6].innerText      
            });

          });

          var token = jQuery("[name=csrfmiddlewaretoken]").val();
          var formData = jQuery("form").serializeArray();

          // para agregar el diario al contexto estos se deben agregar a
          // la data usando la siguiente formula
          formData.push({name:"Diario",value:JSON.stringify(DicDiario)});
          formData.push({name:"total_debe",value:JSON.stringify(total_debe)});

          jQuery.ajax({
            method:"POST",
            headers: {'X-CSRFToken': token },
            data: formData
          })
          .done(function(r,textStatus,xhr){
              if(xhr.status=200){
                location.href="/contabilidad/listaasientoscontables/";
                // en una nueva ventana abrir el reporte 
                url = window.location.origin
                url = url + "/contabilidad/imprimirdiariocontable/"+xhr.responseText;
                window.open( url);
                  MensajeOk()
              }
              else{
                MensajeError(textStatus);
              }
          }).fail(function (error) {
              MensajeError(error.responseText);
          });

          // cerrar el modal
          CerrarModal();}
          });

      // return false;

    });

};

function cargarTablaDiario(diario_id){
  // leer el asiento contable y cargarlo en la tabla
  fetchRecuperar("/contabilidad/cargadetalleasiento/"+diario_id, function(data){
    if (data.length > 0){
      for (var i=0; i<data.length; i++){
        cuenta = data[i].cxcuenta
        nombre_cuenta = data[i].cxcuenta__ctcuenta
        referencia = data[i].ctreferencia
        tipo = data[i].cxtipo
        valor = data[i].nvalor
        linea = data[i].id

        agregarFilaTabla(cuenta, nombre_cuenta, tipo, referencia, valor, linea)
      }
    }
  })
}

function agregarFilaTabla(cuenta, nombre_cuenta, tipo, referencia, valor, id_linea){
  var tabla=document.getElementById('tabla_diario')
  var tbody = tabla.children[1]
  var nuevafila=""
  var valordebe = 0
  var valorhaber = 0
  
  if (cuenta=="" || tipo=="" || referencia=="" )
    return false;

  if (tipo == 'D')
    valordebe=valor
  else
    valorhaber=valor

  if (! tbody){
      tbody = document.createElement("tbody")
      tbody.setAttribute("id",'body_asiento')
      tbody.setAttribute("name",'body_asiento')
      tabla.appendChild(tbody);
  }

  //<pintar la fila>
  nuevafila+="<tr>"

  nuevafila+="<td>" + nombre_cuenta +"</td>"
  nuevafila+="<td>" + referencia +"</td>"
  nuevafila+="<td>" + valordebe +"</td>"
  nuevafila+="<td>" + valorhaber +"</td>"
  nuevafila+="<td hidden>" + cuenta +"</td>"
  nuevafila+="<td hidden>" + tipo +"</td>"
  nuevafila+="<td hidden>" + id_linea +"</td>"

  nuevafila+= `<td>
    <a class="remove" onclick='editarFila(this)' title="Editar">
              <i class="fa fa-edit"></i>
    </a>
    <a class="remove" onclick='eliminarFila(this)' title="Eliminar">
              <i class="fa fa-trash"></i>
    </a>
    </td>`

  nuevafila+="</tr>"

  tbody.insertAdjacentHTML("beforeend",nuevafila)
  
  // acumular en totales
  sumarTotales(valordebe, valorhaber)
}

function sumarTotales(valordebe, valorhaber){
  console.log("sumarTotales", valordebe, valorhaber)
  totaldebe=capturaValor("total_debe")
  totalhaber=capturaValor("total_haber")
  sumadebe = parseFloat(totaldebe) + parseFloat(valordebe)
  sumahaber = parseFloat(totalhaber) + parseFloat(valorhaber)
  
  inicializaValor("total_debe", sumadebe)
  inicializaValor("total_haber", sumahaber)
}

function restarTotales(valordebe, valorhaber){
  totaldebe=capturaValor("total_debe")
  totalhaber=capturaValor("total_haber")
  sumadebe = parseFloat(totaldebe) - parseFloat(valordebe)
  sumahaber = parseFloat(totalhaber) - parseFloat(valorhaber)
  
  inicializaValor("total_debe", sumadebe)
  inicializaValor("total_haber", sumahaber)
}

function eliminarFila(btn){
  var td=btn.parentNode
  var tr =td.parentNode
  var trpadre = tr.parentNode
  var valordebe = tr.children[2].innerText
  var valorhaber = tr.children[3].innerText
  var id_linea = tr.children[6].innerText
  // actualizar totales
  restarTotales(valordebe, valorhaber)

  // si es una linea de un diario existente dejar los valoers en cero
  if (id_linea != '0'){
    var td=btn.parentNode
    var tr =td.parentNode
    var trpadre = tr.parentNode
    tr.children[3].innerText = 0
    tr.children[2].innerText = 0  
  }else{
    // si es una linea de un diario nuevo eliminar la fila
    trpadre.removeChild(tr)
  }
}

function editarFila(btn){
  var td=btn.parentNode
  var tr =td.parentNode
  var id_linea = tr.children[6].innerText

  linea = btn
  AbrirModal('/contabilidad/editarlineadeasiento/'+id_linea)
}

function actualizarFilaTabla(id_linea){
  var select = document.getElementById('id_cxcuenta');
  var nombre_cuenta = select.options[select.selectedIndex].text;
  var cuenta = select.value;
  var tipo = document.getElementById("id_cxtipo").value;
  var referencia = document.getElementById("id_ctreferencia").value;
  var nvalor = document.getElementById("id_nvalor").value;

  var td=linea.parentNode
  var tr =td.parentNode

  // actualizar el total
  var valordebe = tr.children[2].innerText
  var valorhaber = tr.children[3].innerText
  restarTotales(valordebe, valorhaber)

  tr.children[0].innerText = nombre_cuenta
  tr.children[1].innerText = referencia
  if (tipo == 'D'){
    tr.children[2].innerText = nvalor
    tr.children[3].innerText = 0
  }
  else{
    tr.children[2].innerText = 0
    tr.children[3].innerText = nvalor
  }
  tr.children[4].innerText = cuenta
  tr.children[5].innerText = tipo
  tr.children[6].innerText = id_linea
  // actualizar el total
  valordebe = tr.children[2].innerText
  valorhaber = tr.children[3].innerText
  sumarTotales(valordebe, valorhaber)

}