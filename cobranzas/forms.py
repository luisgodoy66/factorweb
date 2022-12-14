from pyexpat import model
from django import forms
from .models import Cheques, Documentos_cabecera, Liquidacion_cabecera\
    , Cheques_protestados, Recuperaciones_cabecera
from operaciones.models import Motivos_protesto_maestro

from datetime import date

class CobranzasDocumentosForm(forms.ModelForm):

    class Meta:
        model=Documentos_cabecera
        fields=['cxcliente', 'cxtipofactoring', 'cxformapago'
            , 'nvalor', 'dcobranza', 'nsobrepago', 'cxcuentadeposito'
            , 'ddeposito', 'cxcuentatransferencia'
        ]
        labels={'cxcliente':'Cliente', 'cxtipofactoring':'Tipo de factoring'
            , 'cxformapago':'Forma de cobro','nvalor':'Valor recibido'
            , 'dcobranza':'Fecha de cobro', 'nsobrepago':'Sobrepago'
            , 'cxcuentadeposito':'Cuenta de la empresa'
            , 'ddeposito': 'Fecha de depósito'
            , 'cxcuentatransferencia': 'Cuenta de origen de transferencia'
        }
        # esto sirve para ventana de condonacion. Lo importante es el formato
        widgets = {
            'ddeposito': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
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
        self.fields['nsobrepago'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['value']=date.today
        self.fields['ddeposito'].widget.attrs['readonly']=True
        self.fields['ddeposito'].widget.attrs['value']=date.today

class ChequesForm(forms.ModelForm):
    class Meta:
        model = Cheques
        fields=['cxcuentabancaria', 'ctcheque', 'ctgirador'
        ]
        labels={
            'cxcuentabancaria':'Cuenta bancaria'
            , 'ctcheque':'Cheque', 'ctgirador':'Girador'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class LiquidarForm(forms.ModelForm):
    class Meta:
        model=Liquidacion_cabecera
        fields=['ctinstrucciondepago', 'ddesembolso', 'dliquidacion', 'nneto'
            ]
        labels={'ctinstrucciondepago':'Instrucción de pago'
            , 'ddesembolso':'Desembolso', 'cxcuentapago': 'Cuenta de origen'
            , 'dliquidacion': 'Liquidación', 'nneto': 'Neto'
        }
        widgets={'ctinstrucciondepago': forms.Textarea(attrs={'rows': '2'}), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['ddesembolso'].widget.attrs['readonly']=True
        self.fields['ddesembolso'].widget.attrs['value']=date.today
        self.fields['dliquidacion'].widget.attrs['readonly']=True
        self.fields['dliquidacion'].widget.attrs['value']=date.today

class MotivoProtestoForm(forms.ModelForm):
    class Meta:
        model = Motivos_protesto_maestro
        fields=['ctmotivoprotesto', 'ctabreviacion', 'lresponsabilidadgirador']
        labels={'ctmotivoprotesto':'Desripción'
            , 'ctabreviacion':'Descripción corta'
            , 'lresponsabilidadgirador':'Responsabilidad del girador'

        }
        widgets={'ctmotivoprotesto': forms.Textarea(attrs={'rows': '2'}), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class ProtestoForm(forms.ModelForm):
    class Meta:
        model = Cheques_protestados

        fields=['dprotesto', 'motivoprotesto','nvalornotadebito']

        labels={'dprotesto':'Fecha de protesto'
        , 'motivoprotesto':'Motivo'
        ,'nvalornotadebito':'Nota de débito bancaria'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dprotesto'].widget.attrs['readonly']=True
        self.fields['dprotesto'].widget.attrs['value']=date.today

class RecuperacionesProtestosForm(forms.ModelForm):

    class Meta:
        model=Recuperaciones_cabecera
        fields=['cxcliente', 'cxtipofactoring','cxformacobro', 'nvalor'
            , 'dcobranza', 'nsobrepago', 'cxcuentadeposito', 'ddeposito'
            , 'cxcuentatransferencia'
        ]
        labels={'cxcliente':'Cliente', 'cxtipofactoring':'Tipo de factoring'
            , 'cxformacobro':'Forma de cobro','nvalor':'Valor recibido'
            , 'dcobranza':'Fecha de recuperación', 'nsobrepago':'Sobrepago'
            , 'cxcuentadeposito':'Cuenta de la empresa'
            , 'ddeposito': 'Fecha de depósito'
            , 'cxcuentatransferencia': 'Cuenta de origen de transferencia'
        }
        # esto sirve para ventana de condonacion. Lo importante es el formato
        widgets = {
            'ddeposito': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
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
        self.fields['nsobrepago'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['value']=date.today
        self.fields['ddeposito'].widget.attrs['readonly']=True
        self.fields['ddeposito'].widget.attrs['value']=date.today
