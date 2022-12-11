from datetime import date
from django import forms
from .models import Asignacion, Documentos, ChequesAccesorios

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
            ,'niva', 'nretencioniva', 'nretencionrenta', 'ntotal'
        ]
        labels={
            'cxcomprador':'Comprador', 'ctcomprador':'Nombre de comprador'
            , 'ctserie1':'Serie 1', 'ctserie2':'Serie 2'
            ,'ctdocumento':'Documento', 'demision':'Emisión'
            , 'dvencimiento':'Vencimiento', 'nvalorantesiva':'Valor antes de IVA'
            ,'niva':'IVA', 'nretencioniva':'Retención de IVA'
            , 'nretencionrenta':'Retencion de impuesto a la renta'
            , 'ntotal':'Neto'
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
