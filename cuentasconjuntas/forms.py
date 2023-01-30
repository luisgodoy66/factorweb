from django import forms
from .models import Cuentas_bancarias, Transferencias
from cobranzas.models import DebitosCuentasConjuntas

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


class TransferenciasForm(forms.ModelForm):
    class Meta:
        model = Transferencias
        fields = ['cuentadestino', 'nvalor', 'ndevolucion', 'dmovimiento']
        labels = {'cuentadestino':'Cuenta destino'
            , 'nvalor':'Valor transferido'
            , 'ndevolucion':'Valor a devolver', 'dmovimiento':'Fecha'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dmovimiento'].widget.attrs['readonly']=True
        self.fields['dmovimiento'].widget.attrs['value']=date.today

class DebitosForm(forms.ModelForm):
    input_formats=["%Y/%m/%d"],
    
    class Meta:
        model=DebitosCuentasConjuntas
        fields = ['ctmotivo', 'nvalor', 'dmovimiento']
        labels = {'ctmotivo':'Motivo', 'nvalor':'Valor', 'dmovimiento':'Fecha'}
        # Lo importante es el formato
        widgets = {
            'dmovimiento': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'datepicker', 
                    'placeholder': 'Select a date',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dmovimiento'].widget.attrs['value']=date.today

class DebitosNuevosForm(forms.ModelForm):
    input_formats=["%Y/%m/%d"],
    
    class Meta:
        model=DebitosCuentasConjuntas
        fields = ['ctmotivo', 'nvalor', 'dmovimiento', 'cuentabancaria']
        labels = {'ctmotivo':'Motivo', 'nvalor':'Valor', 'dmovimiento':'Fecha'
            , 'cuentabancaria':'Cuenta bancaria'}
        # Lo importante es el formato
        widgets = {
            'dmovimiento': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'datepicker', 
                    'placeholder': 'Select a date',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dmovimiento'].widget.attrs['value']=date.today
