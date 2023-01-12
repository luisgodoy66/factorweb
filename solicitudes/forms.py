from datetime import date
from django import forms
from .models import Asignacion, Documentos, ChequesAccesorios, Clientes

class AsignacionesForm(forms.ModelForm):

    class Meta:
        model=Asignacion
        fields=['cxcliente', 'cxtipofactoring', 'cxtipo'
            ,'nvalor', 'ncantidaddocumentos', 
        ]
        labels={'cxcliente':'Cliente', 'cxtipofactoring':'Tipo de factoring'
            , 'cxtipo':'Tipo de asignación'
            ,'nvalor':'Valor', 'ncantidaddocumentos':'Cantidad de documentos', 
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['ncantidaddocumentos'].widget.attrs['readonly']=True
        self.fields['nvalor'].widget.attrs['readonly']=True

class DocumentosForm(forms.ModelForm):
    demision = forms.DateInput()
    
    class Meta:
        model=Documentos
        fields=[
            'cxcomprador', 'ctcomprador', 'ctserie1', 'ctserie2'
            ,'ctdocumento', 'demision', 'dvencimiento', 'nvalorantesiva'
            ,'niva', 'nretencioniva', 'nretencionrenta', 'ntotal', 'nvalornonegociado'
        ]
        labels={
            'cxcomprador':'Comprador', 'ctcomprador':'Nombre de comprador'
            , 'ctserie1':'Serie 1', 'ctserie2':'Serie 2'
            , 'ctdocumento':'Documento', 'demision':'Emisión'
            , 'dvencimiento':'Vencimiento', 'nvalorantesiva':'Valor antes de IVA'
            , 'niva':'IVA', 'nretencioniva':'Retención de IVA'
            , 'nretencionrenta':'Retencion de impuesto a la renta'
            , 'ntotal':'Neto', 'nvalornonegociado':'Valor no negociado'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['demision'].widget.attrs['value']=date.today
        self.fields['demision'].widget.attrs['readonly']=True
        self.fields['dvencimiento'].widget.attrs['value']=date.today
        self.fields['dvencimiento'].widget.attrs['readonly']=True
        self.fields['ntotal'].widget.attrs['readonly']=True

class ChequesForm(forms.ModelForm):
    class Meta:
        model=ChequesAccesorios
        fields=[
            'cxbanco', 'ctcuenta', 'ctcheque'
            ,'ctgirador', 'ntotal', 'dvencimiento'
        ]
        labels={
            'cxbanco':'Banco', 'ctcuenta':'Número de cuenta'
            , 'ctcheque':'Número de cheque'
            , 'ctgirador':'Girador', 'ntotal':'Valor'
            , 'dvencimiento':'Vencimiento'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dvencimiento'].widget.attrs['value']=date.today
        self.fields['dvencimiento'].widget.attrs['readonly']=True

class ClientesForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields=['cxcliente', 'ctnombre', 'ctdireccion', 'cttelefono1'
            , 'cttelefono2', 'ctemail', 'ctemail2', 'ctcelular'
            , 'ctgirocomercial']
        labels={
            'cxcliente':'Id. cliente', 'ctnombre':'Nombre de cliente'
            , 'ctdireccion':'Dirección', 'cttelefono1':'Teléfono'
            , 'cttelefono2':'Teléfono', 'ctemail':'Dirección email'
            , 'ctemail2':'Dirección email', 'ctcelular':'Celular'
            , 'ctgirocomercial':'Giro comercial'
        }

        widgets={'ctdireccion': forms.Textarea(attrs={'rows': '3'})
                }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
