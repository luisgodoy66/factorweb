from pyexpat import model
from django import forms

from .models import Cheques, Documentos_cabecera, Liquidacion_cabecera\
    , Cheques_protestados, Recuperaciones_cabecera, Cargos_cabecera\
    , Pagare_cabecera
from operaciones.models import Motivos_protesto_maestro, ChequesAccesorios
from empresa.models import Cuentas_bancarias
from cuentasconjuntas.models import Cuentas_bancarias as Cuentas_compartidas

from datetime import date

class CobranzasDocumentosForm(forms.ModelForm):

    class Meta:
        model=Documentos_cabecera
        fields=['cxcliente', 'cxtipofactoring', 'cxformapago'
            , 'nvalor', 'dcobranza', 'nsobrepago', 'cxcuentadeposito'
            , 'ddeposito', 'cxcuentatransferencia', 'cxcuentaconjunta'
        ]
        labels={'cxcliente':'Cliente', 'cxtipofactoring':'Tipo de factoring'
            , 'cxformapago':'Forma de cobro','nvalor':'Valor recibido'
            , 'dcobranza':'Fecha de cobro', 'nsobrepago':'Sobrepago'
            , 'cxcuentadeposito':'Cuenta de la empresa'
            , 'ddeposito': 'Fecha de depósito'
            , 'cxcuentatransferencia': 'Cuenta de origen de transferencia'
            , 'cxcuentaconjunta': 'Cuenta compartida'
        }
        widgets = {
            'dcobranza': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
            'ddeposito': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['nsobrepago'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['value']=date.today
        self.fields['ddeposito'].widget.attrs['value']=date.today

        if empresa:
            self.fields['cxcuentadeposito'].queryset = Cuentas_bancarias.objects\
                .filter(empresa=empresa, lactiva = True, leliminado = False)
            self.fields['cxcuentaconjunta'].queryset = Cuentas_compartidas.objects\
                .filter(empresa=empresa, lactiva = True
                        , leliminado = False)

    def clean_ddeposito(self):
        data = self.cleaned_data['ddeposito']

        # #Check date is not in past.
        # if data < datetime.date.today():
        #     raise ValidationError(_('Invalid date - renewal in past'))

        # #Check date is in range librarian allowed to change (+4 weeks).
        # if data > datetime.date.today() + datetime.timedelta(weeks=4):
        #     raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data
    
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
        widgets={'ctinstrucciondepago': forms.Textarea(attrs={'rows': '2'}), 
            'dliquidacion': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
            'ddesembolso': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
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
        # self.fields['ddesembolso'].widget.attrs['readonly']=True
        self.fields['ddesembolso'].widget.attrs['value']=date.today
        # self.fields['dliquidacion'].widget.attrs['readonly']=True
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

    # el valor de la nd por protesto no se guarda en el registro del protesto
    # estará en el registro de la tabla de notas de debito asociada al protesto
    class Meta:
        model = Cheques_protestados

        fields=['dprotesto', 'motivoprotesto']

        labels={'dprotesto':'Fecha de protesto'
            , 'motivoprotesto':'Motivo'
            }
        widgets = {
            'dprotesto': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        # self.fields['dprotesto'].widget.attrs['readonly']=True
        self.fields['dprotesto'].widget.attrs['value']=date.today

        if empresa:
            self.fields['motivoprotesto'].queryset = Motivos_protesto_maestro.objects\
                .filter(empresa=empresa, leliminado = False)

class RecuperacionesProtestosForm(forms.ModelForm):

    class Meta:
        model=Recuperaciones_cabecera
        fields=['cxcliente', 'cxtipofactoring','cxformacobro', 'nvalor'
            , 'dcobranza', 'nsobrepago', 'cxcuentadeposito', 'ddeposito'
            , 'cxcuentatransferencia', 'cxcuentaconjunta'
        ]
        labels={'cxcliente':'Cliente', 'cxtipofactoring':'Tipo de factoring'
            , 'cxformacobro':'Forma de cobro','nvalor':'Valor recibido'
            , 'dcobranza':'Fecha de recuperación', 'nsobrepago':'Sobrepago'
            , 'cxcuentadeposito':'Cuenta de la empresa'
            , 'ddeposito': 'Fecha de depósito'
            , 'cxcuentatransferencia': 'Cuenta de origen de transferencia'
            , 'cxcuentaconjunta': 'Cuenta compartida'
        }
        widgets = {
            'ddeposito': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Select a date',
                    'type': 'date'
                    }
                    ),
            'dcobranza': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Select a date',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['nsobrepago'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['value']=date.today
        self.fields['ddeposito'].widget.attrs['value']=date.today

        if empresa:
            self.fields['cxcuentadeposito'].queryset = Cuentas_bancarias.objects\
                .filter(empresa=empresa, lactiva = True, leliminado = False)
            self.fields['cxcuentaconjunta'].queryset = Cuentas_compartidas.objects\
                .filter(empresa=empresa, lactiva = True
                        , leliminado = False)

class CobranzasCargosForm(forms.ModelForm):

    class Meta:
        model=Cargos_cabecera
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
        widgets = {
            'dcobranza': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
            'ddeposito': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['nsobrepago'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['value']=date.today
        self.fields['ddeposito'].widget.attrs['value']=date.today

        if empresa:
            self.fields['cxcuentadeposito'].queryset = Cuentas_bancarias.objects\
                .filter(empresa=empresa, lactiva = True, leliminado = False)

class AccesoriosForm(forms.ModelForm):
    class Meta:
        model=ChequesAccesorios
        fields=[
            'ctcheque', 'cxpropietariocuenta'
            ,'ctgirador', 
        ]
        labels={
            'ctcheque':'Número de cheque'
            , 'cxpropietariocuenta':'Propietario de cuenta'
            , 'ctgirador':'Girador'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class CobranzasPagareForm(forms.ModelForm):

    class Meta:
        model=Pagare_cabecera
        fields=['cxcliente', 'cxformapago'
            , 'nvalor', 'dcobranza', 'nsobrepago', 'cxcuentadeposito'
            , 'ddeposito', 'cxcuentatransferencia'
        ]
        labels={'cxcliente':'Cliente'
            , 'cxformapago':'Forma de cobro','nvalor':'Valor recibido'
            , 'dcobranza':'Fecha de cobro', 'nsobrepago':'Sobrepago'
            , 'cxcuentadeposito':'Cuenta de la empresa'
            , 'ddeposito': 'Fecha de depósito'
            , 'cxcuentatransferencia': 'Cuenta de origen de transferencia'
        }
        widgets = {
            'dcobranza': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
            'ddeposito': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['nsobrepago'].widget.attrs['readonly']=True
        self.fields['dcobranza'].widget.attrs['value']=date.today
        self.fields['ddeposito'].widget.attrs['value']=date.today

        if empresa:
            self.fields['cxcuentadeposito'].queryset = Cuentas_bancarias.objects\
                .filter(empresa=empresa, lactiva = True, leliminado = False)

    def clean_ddeposito(self):
        data = self.cleaned_data['ddeposito']

        return data
