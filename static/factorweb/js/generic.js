function objeto_fechas(Campo, Valor = null){
    jQuery(Campo).datetimepicker({
        timepicker:false,
        format:'Y-m-d',
        value:Valor
       });
};

// <funciones de tablas bootstrap>
function responseHandler(res) {
    jQuery.each(res.rows, function (i, row) {
        row.state = $.inArray(row.id, selections) !== -1
    })
    return res
}
    
function LineaTotalEnPieDePaginaDeTabla(data) {
    return 'Total'
}
    
function LineaCantidadEnPieDePaginaDeTabla(data) {
return data.length
}

function LineaTotalValoresEnPieDepaginaDeTabla(data) {
    var field = this.field
    return '$' + data.map(function (row) {
        return +row[field].substring(0)
    }).reduce(function (sum, i) {
        return Math.round((sum + i + Number.EPSILON) * 100) / 100;
    }, 0)
}
    
function detailFormatter(index, row) {
    var html = []
    $.each(row, function (key, value) {
        html.push('<p><b>' + key + ':</b> ' + value + '</p>')
    })
    return html.join('')
}

function getIdSelections() {
    return jQuery.map($table.bootstrapTable('getSelections'), function (row) {
        return row.id
    })
}

// mensajes
function MensajeError(msg="Ocurrió un error"){
    Swal.fire({
        icon: 'error',
        title: 'Oops...',
        text: msg,
        //footer: '<a href="">Why do I have this issue?</a>'
      })    
}

function MensajeOK(msg="Grabado con éxito"){
    Swal.fire({
        position: 'top-end',
        icon: 'success',
        title: msg,
        showConfirmButton: false,
        timer: 3000
      })    
}

function MensajeConfirmacion(msg="Confirme proceso",callback){
    Swal.fire({
        title: 'Confirmación',
        text: msg,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí!'
      }).then((result) => {
        if (result.isConfirmed) {
            callback()
        }
      })
}        

// funciones de html
function capturaValor(Elemento){
    return document.getElementById(Elemento).value;
}

function inicializaValor(Elemento, Valor){
    document.getElementById(Elemento).value=Valor
}

function CerrarSideBar(){
    jQuery("#menuToggle").click();
}

// funciones fetch
function fetchProcesar(url,callback){
    // devuelve mensajes 
    fetch(url)
    .then(res=>res.text())
    .then(res=>{
        if(res=='OK'){
            // MensajeOK()
            callback()
        }
        else
            MensajeError(res)
    })

}
    
function fetchRecuperar(url,callback){
    // devuelve json
    fetch(url)
    .then(res=>res.json())
    .then(res=>{
        callback(res)
    })

}

function fetchPostear(url, objeto, callback){
    var token= document.getElementsByName("csrfmiddlewaretoken")[0].value
    fetch(url,{
        headers:{
            "Content-type":"application/json",
            "X-CSRFToken":token
        },
        method:"POST",
        body:JSON.stringify(objeto)
    }).then(res=>res.text())
    .then(res=>{
        if(res.slice(0,2)=='OK'){
            MensajeOK()
            // callback()
            callback(res.slice(2))
        }
        else{
           MensajeError(res)       
        }
    })

}

// funciones modal
function AbrirModal(url){
    jQuery("#popup").load(url, function(){
        jQuery(this).modal({
            backdrop: 'static',
            keyboard: false
        })
        jQuery(this).modal('show');
    });
    return false;
}

function CerrarModal(){
    jQuery("#popup").modal('hide');
    return false;
}

// funciones de tablas html
function AgregarFilaVacia(id, nombre_body){
    var tabla=document.getElementById(id)
    var thead = tabla.children[0]
    var tr = thead.children[0]
    var nnodos = tr.children.length
    var tbody = tabla.children[1]
    var nfilas = 0
    var trultimo = 0
    var nuevafila=""
    var propiedadId = tabla.getAttribute("data-propiedadId")

    if (tbody){
        nfilas = tbody.children.length

        if (nfilas>0){
            trultimo = tbody.children[nfilas-1]

            // //no agregar más de una fila
            // if (trultimo.children[0].getAttribute("data-valor")=="") {
            //     return}
        }
    }else{
        tbody = document.createElement("tbody")
        tbody.setAttribute("id",nombre_body)
        tbody.setAttribute("name",nombre_body)
        tabla.appendChild(tbody);

    }

    //<pintar la fila>
    nuevafila+="<tr>"
    var propiedadNombre 

    for (var i=0;i<nnodos-1;i++){
        propiedadNombre=thead.children[0].children[i].getAttribute("data-cabecera")

        nuevafila+=`<td data-valor=''>
                        <input ${propiedadNombre==propiedadId? 'readonly' :''} 
                            type='text' class='form-control' />
                    </td>`
    }

    nuevafila+= `<td>
        <button onclick='eliminarFila(this)' class='btn btn-danger'>Eliminar</button>
        <button class='btn btn-success' onclick='GrabarEdicion(capturarEdicion(this))'>Guardar</button>
        </td>`        

    nuevafila+="</tr>"

    tbody.insertAdjacentHTML("beforeend",nuevafila)
    // </pintar la fila>
}

function eliminarFila(btn){
    var td=btn.parentNode
    var tr =td.parentNode
    var trpadre = tr.parentNode

    trpadre.removeChild(tr)
}

function capturarEdicion(btn){
    // esta funcion se asigna en la funcion clickCelda con un insertAdjacentHTML
    var tr = btn.parentNode.parentNode
    var nhijos = tr.children.length
    var valores=[]

    for(var i=0; i<nhijos-1;i++){
        tdObj=tr.children[i]
        // si en la celda hay un input (al dar dblclick) el valor está en el input
        if(tdObj.children.length>0){
            if (tdObj.children[0].nodeName=="INPUT"){
                        valores.push(tdObj.children[0].value)
            }            
        }
        else{
            valores.push(tdObj.getAttribute("data-valor"))
        }

    }

    return valores
}
