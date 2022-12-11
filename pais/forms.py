from dataclasses import fields
from pyexpat import model
from django import forms
from .models import Bancos, Feriados
from datetime import date

class BancoForm(forms.ModelForm):

    class Meta:
        model=Bancos
        
        fields=['ctbanco', 'llocal']
        labels={'ctbanco':'Nombre', 'llocal':'Banco local'}        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class FeriadoForm(forms.ModelForm):
    class Meta:
        model=Feriados

        fields=['dferiado','llaborable']

        labels={
            'dferiado':'Fecha',
            'llaborable':'Es laborable'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dferiado'].widget.attrs['value']=date.today
        self.fields['dferiado'].widget.attrs['readonly']=True
