from django import forms
from .models import Cuentas_bancarias

from datetime import date

class CuentasBancariasForm(forms.ModelForm):
    class Meta:
        model=Cuentas_bancarias
        fields=['cxbanco', 'cxtipocuenta', 'cxcuenta'
            , 'lactiva', 'cxcliente'
        ]
        labels={'cxbanco':'Banco', 'cxtipocuenta':'Tipo de cuenta'
            , 'cxcuenta':'Número de cuenta'
            , 'lactiva':'Está activa', 'cxcliente':'Cliente'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
