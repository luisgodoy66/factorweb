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
        timer: 5000
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

function antigüedadcartera(url){
    // chart antigüedad de la cartera
    fetchRecuperar(url,function(data){
        var ctx = document.getElementById( "singelBarChart" );
        ctx.height = 150;

        if (data["facturas"]){
            v90m = data["facturas"]["vencido_mas_90"]
            v90 = data["facturas"]["vencido_90"]
            v60 = data["facturas"]["vencido_60"]
            v30 = data["facturas"]["vencido_30"]
            p30 = data["facturas"]["porvencer_30"]
            p60 = data["facturas"]["porvencer_60"]
            p90 = data["facturas"]["porvencer_90"]
            p90m = data["facturas"]["porvencer_mas_90"]
        }
        else{
            v90m=0;v90=0;v60=0;v30=0; p30=0; p60=0; p90=0; p90m=0
        }

        if (data["accesorios"]){
            av90m = data["accesorios"]["vencido_mas_90"]
            av90 = data["accesorios"]["vencido_90"]
            av60 = data["accesorios"]["vencido_60"]
            av30 = data["accesorios"]["vencido_30"]
            ap30 = data["accesorios"]["porvencer_30"]
            ap60 = data["accesorios"]["porvencer_60"]
            ap90 = data["accesorios"]["porvencer_90"]
            ap90m = data["accesorios"]["porvencer_mas_90"]
        }
        else{
            av90m=0;av90=0;av60=0;av30=0; ap30=0; ap60=0; ap90=0; ap90m=0
        }
        
        if (data["protestos"]){
            pv90m = data["protestos"]["pvencido_mas_90"]
            pv90 = data["protestos"]["pvencido_90"]
            pv60 = data["protestos"]["pvencido_60"]
            pv30 = data["protestos"]["pvencido_30"]
            pp30 = data["protestos"]["pporvencer_30"]
            pp60 = data["protestos"]["pporvencer_60"]
            pp90 = data["protestos"]["pporvencer_90"]
            pp90m = data["protestos"]["pporvencer_mas_90"]
    }
        else{
            pv90m=0;pv90=0;pv60=0;pv30=0; pp30=0; pp60=0; pp90=0; pp90m=0
        }
        
        var myChart = new Chart( ctx, {
            type: 'bar',
            data: {
                labels: [ "v+90", "v90", "v60", "v30", "x30", "x60", "x90", "x+90" ],
                datasets: [
                    {
                        label: "Facturas",
                        data: [ v90m, v90, v60, v30, p30, p60, p90, p90m ],
                        borderColor: "rgba(0, 123, 255, 0.9)",
                        borderWidth: "0",
                        backgroundColor: "rgba(0, 123, 255, 0.5)"
                                },
                    {
                        label: "Accesorios",
                        data: [ av90m, av90, av60, av30, ap30, ap60, ap90, ap90m ],
                        borderColor: "rgba(0, 123, 255, 0.9)",
                        borderWidth: "0",
                        backgroundColor: "rgba(0, 255, 255, 0.5)"
                                },
                    {
                        label: "Protestos",
                        data: [ pv90m, pv90, pv60, pv30, pp30, pp60, pp90, pp90m ],
                        borderColor: "rgba(0, 123, 255, 0.9)",
                        borderWidth: "0",
                        backgroundColor: "rgba(255, 0, 0, 0.5)"
                                }
                            ]
            },
            options: {
                scales: {
                    yAxes: [ {
                        ticks: {
                            beginAtZero: true
                        }
                                    } ]
                }
            }
        } );

    })
}    