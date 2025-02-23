from django import forms
from .models import Configuracion_slack

class SlackForm(forms.ModelForm):

    class Meta:
        model = Configuracion_slack
        fields=['ctdescripcion', 'ctslackbottoken'
                , 'ctslackchannelname', 'ctslacksigningsecret'
                , 'lactivo', 'ctappid'
        ]
        labels={'ctdescripcion':'Descripción'
                , 'ctslackbottoken':'Token'
                , 'ctslackchannelname':'Nombre de canal'
                , 'ctslacksigningsecret':'Firma secreta'
                , 'lactivo':'Activo'
                , 'ctappid':'ID de la aplicación'
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        
