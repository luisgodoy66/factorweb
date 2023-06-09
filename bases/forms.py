from django import forms
from .models import Empresas

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresas
        fields = ('ctruccompania', 'ctnombre', 'ctgerente', 'ctdireccion'
                  , 'ctcontribuyenteespecial', 'lregimenrimpe')
        labels = {'ctruccompania':'RUC', 'ctnombre':'Nombre'
                  , 'ctgerente':'Gerente', 'ctdireccion':'Dirección'
                  , 'ctcontribuyenteespecial':'Número de contribuyente especial'
                  , 'lregimenrimpe': 'Régimen RIMPE'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

