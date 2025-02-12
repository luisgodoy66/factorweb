from django import forms
from .models import Configuracion_slack

class SlackForm(forms.ModelForm):

    class Meta:
        model = Configuracion_slack
        fields=['ctdescripcion', 'ctslackbottoken'
                , 'ctslackchannelname', 'ctslacksigningsecret'
                , 'lactivo'
        ]
        labels={'ctdescripcion':'Descripción'
                , 'ctslackbottoken':'Token'
                , 'ctslackchannelname':'Nombre de canal'
                , 'ctslacksigningsecret':'Firma secreta'
                , 'lactivo':'Activo'
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        
