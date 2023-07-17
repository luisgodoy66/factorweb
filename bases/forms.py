from django import forms
from .models import Empresas

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresas
        fields = ('ctruccompania', 'ctnombre', 'ctgerente', 'ctdireccion'
                  , 'ctcontribuyenteespecial', 'lregimenrimpe', 'ctciudad')
        labels = {'ctruccompania':'RUC', 'ctnombre':'Nombre'
                  , 'ctgerente':'Gerente', 'ctdireccion':'Dirección'
                  , 'ctcontribuyenteespecial':'Número de contribuyente especial'
                  , 'lregimenrimpe': 'Régimen RIMPE', 'ctciudad':'Ciudad de domicilio'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

