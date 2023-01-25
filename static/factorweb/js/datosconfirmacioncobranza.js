window.onload=function(){
    // inicializar el encabezado
    ActualizarHeader();
    
    objeto_fechas("#id_dmovimiento")

    jQuery('input[type=checkbox][name="cargo"]').change(function() {
        toggle_cargo();
    });
    jQuery('input[type=checkbox][name="transferencia"]').change(function() {
        toggle_transferencia();
    });

};

function toggle_cargo(){
  const div_c = document.querySelector('#div_datos_cargo');
  let endendido = document.querySelector('input[name="cargo"]:checked');

 if (endendido == null){
    div_c.setAttribute('hidden',true);
}else{
    div_c.removeAttribute('hidden');
}
  }

function toggle_transferencia(){
  const div_c = document.querySelector('#div_datos_transferencia');
  let endendido = document.querySelector('input[name="transferencia"]:checked');

 if (endendido == null){
    div_c.setAttribute('hidden',true);
}else{
    div_c.removeAttribute('hidden');
}
  }

function AceptarConfirmacion(){
  let endendido_tr = document.querySelector('input[name="transferencia"]:checked');
  valor_tr = capturaValor("id_nvalor")

  if (endendido_tr !== null & valor_tr ==0){
    alert('Ha especificado registro de transferencia y no ha indicado el valor de la misma')
    return false;
  }
    alert('confirmado')
}
