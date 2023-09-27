window.onload=function(){


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

      return false;

    });

};


function AgregarFila( ){
  var tabla=document.getElementById('tabla_diario')
  var tbody = tabla.children[1]
  var nuevafila=""
  var cuenta = capturaValor("id_cxcuenta")
  var tipo = capturaValor("id_cxtipo")
  var referencia = capturaValor("id_ctreferencia")
  var valordebe = 0
  var valorhaber = 0
  var select = document.getElementById('id_cxcuenta');
  var nombre_cuenta = select.options[select.selectedIndex].text;
  
  if (cuenta=="" || tipo=="" || referencia=="" )
    return false;

  if (tipo == 'D')
    valordebe=capturaValor("id_nvalor")
  else
    valorhaber=capturaValor("id_nvalor")

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
  
  nuevafila+= `<td><a class="remove" onclick='eliminarFila(this)'"
              title="Eliminar"><i class="fa fa-trash"></i></a></td>`

  nuevafila+="</tr>"

  tbody.insertAdjacentHTML("beforeend",nuevafila)
  
  // acumular en totales
  totaldebe=capturaValor("total_debe")
  totalhaber=capturaValor("total_haber")
  sumadebe = parseFloat(totaldebe) + parseFloat(valordebe)
  sumahaber = parseFloat(totalhaber) + parseFloat(valorhaber)
  
  inicializaValor("total_debe", sumadebe)
  inicializaValor("total_haber", sumahaber)

  CerrarModal();

}

function eliminarFila(btn){
  var td=btn.parentNode
  var tr =td.parentNode
  var trpadre = tr.parentNode
  // actualizar totales
  totaldebe=capturaValor("total_debe")
  totalhaber=capturaValor("total_haber")

  var tipo = tr.children[5].innerText
  if (tipo=='D') {
    var valordebe = tr.children[2].innerText
    total_debe += parseFloat( valordebe)
    sumadebe = parseFloat(totaldebe) - parseFloat(valordebe)
    
    inicializaValor("total_debe", sumadebe)
  }
  if (tipo=='H') {
    var valorhaber = tr.children[3].innerText
    total_haber += parseFloat( valorhaber)
    sumahaber = parseFloat(totalhaber) - parseFloat(valorhaber)

    inicializaValor("total_haber", sumahaber)
  }

  trpadre.removeChild(tr)
}



