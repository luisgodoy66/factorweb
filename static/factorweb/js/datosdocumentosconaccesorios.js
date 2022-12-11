window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();

    // configuar cambios en los campos de valores
    jQuery('#id_nvalorantesiva, #id_niva, #id_nretencioniva, #id_nretencionrenta')
        .change(function(){
            calcular_factura();
        });

    // inicializar valores
    objeto_fechas("#id_demision");
    objeto_fechas("#id_dvencimiento");
    
    // cerrar side bar
    // CerrarSideBar();

    // validar antes de enviar
    jQuery("#frmSolicitud").submit(function(e){

      var total_cheques = 0
      e.preventDefault();
      
      jQuery("#body_cheques tr").each(function (i,row) {
            var valor = row.children[5].innerText
            total_cheques += parseFloat( valor)
      });
    
      if (total_cheques != capturaValor("id_ntotal")){
          alert("Valor de cheques "+total_cheques +" no coincide con el neto a negociar")
          return false;
      };

      // convertir la tabla de cheques en un dicconario para pasarlo en el contexto
      DicCheques = new Array();

      jQuery("#body_cheques tr").each(function (i,row) {

        var banco = row.children[0].innerText
        var cuenta = row.children[1].innerText
        var cheque = row.children[2].innerText
        var girador = row.children[3].innerText
        var vencimiento = row.children[4].innerText
        var valor = row.children[5].innerText

        DicCheques.push({          
          banco: banco,
          cuenta: cuenta,
          cheque: cheque,
          girador: girador,
          vencimiento: vencimiento,
          valor: valor,        
        });

      });

      var token = jQuery("[name=csrfmiddlewaretoken]").val();
      var formData = jQuery("form").serializeArray();

      // para agregar los cheques al contexto estos se deben agregar a
      // la data usando la siguiente formula
      formData.push({name:"Cheques",value:JSON.stringify(DicCheques)});

      // no se está poniendo el parametro url, pero sí se ejecuta 
      // la vista correcta
      // cuando puse la url , se unió con la inicial y se duplicó.

      jQuery.ajax({
        method:"POST",
        headers: {'X-CSRFToken': token },
        data: formData
      })
      .done(function(r,textStatus,xhr){
          if(xhr.status=200){
            // aquí es necesario, en caso que sea nueva asignación, 
            // rescatar el número de la asignación
            // para enviarlo para edición.
            location.href="/solicitudes/editarsolicitudconaccesorios/"+xhr.responseText;
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

function calcular_factura()
{
    var antes_de_iva,iva,retencion_iva, retencion_renta,stotal,total;
    
    antes_de_iva = jQuery("#id_nvalorantesiva").val();
    antes_de_iva = antes_de_iva==="" ? 0 : +antes_de_iva;
    antes_de_iva = antes_de_iva<0 ? 0 : antes_de_iva;


    iva =jQuery('#id_niva').val();
    iva = iva==="" ? 0 : +iva;
    iva = iva<0 ? 0 : iva;

    // nota: si iva es 0 no debe pedir retencion de iva
    retencion_iva = jQuery('#id_nretencioniva').val();
    retencion_iva = retencion_iva==="" ? 0 : +retencion_iva;
    retencion_iva = retencion_iva<0 ? 0 : retencion_iva;

    retencion_renta = jQuery('#id_nretencionrenta').val();
    retencion_renta = retencion_renta==="" ? 0 : +retencion_renta;
    retencion_renta = retencion_renta<0 ? 0 : retencion_renta;

    stotal = antes_de_iva + iva;
    total  = stotal - retencion_iva - retencion_renta;

    jQuery('#id_nvalorantesiva').val(antes_de_iva);
    jQuery('#id_niva').val(iva);
    jQuery('#id_nretencioniva').val(retencion_iva);
    jQuery('#id_nretencionrenta').val(retencion_renta);
    jQuery('#id_ntotal').val(total);

};

function AgregarFilaCheque( ){
  var tabla=document.getElementById('tabla_cheques')
  var tbody = tabla.children[1]
  var nuevafila=""
  var banco = capturaValor("id_cxbanco")
  var cuenta = capturaValor("id_ctcuenta")
  var cheque = capturaValor("id_ctcheque")
  var girador = capturaValor("id_ctgirador")
  var vencimiento = capturaValor("id_dvencimiento")
  var valor = capturaValor("cheque_nvalor")

  if (banco=="" || cuenta=="" || cheque=="" || girador=="")
    return false;

  if (! tbody){
      tbody = document.createElement("tbody")
      tbody.setAttribute("id",'body_cheques')
      tbody.setAttribute("name",'body_cheques')
      tabla.appendChild(tbody);
  }

  //<pintar la fila>
  nuevafila+="<tr>"

  nuevafila+="<td>" + banco +"</td>"
  nuevafila+="<td>" + cuenta +"</td>"
  nuevafila+="<td>" + cheque +"</td>"
  nuevafila+="<td>" + girador +"</td>"
  nuevafila+="<td>" + vencimiento +"</td>"
  nuevafila+="<td>" + valor +"</td>"

  nuevafila+= `<td><a class="remove" onclick='eliminarFila(this)'"
              title="Eliminar"><i class="fa fa-trash"></i></a></td>`

  nuevafila+="</tr>"

  tbody.insertAdjacentHTML("beforeend",nuevafila)
  
  CerrarModal();
}



