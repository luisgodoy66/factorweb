from django import forms
from .models import Empresas
from django.forms.widgets import PasswordInput
from django.contrib.auth.models import User


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresas
        fields = ('ctruccompania', 'ctnombre', 'ctgerente', 'ctdireccion'
                  , 'ctcontribuyenteespecial', 'lregimenrimpe', 'ctciudad'
                  , 'ambientesri', 'ilogolargo', 'ilogocorto', 'nporcentajeiva'
                  )
        labels = {'ctruccompania':'RUC', 'ctnombre':'Nombre'
                  , 'ctgerente':'Gerente', 'ctdireccion':'Dirección'
                  , 'ctcontribuyenteespecial':'Número de contribuyente especial'
                  , 'lregimenrimpe': 'Régimen RIMPE', 'ctciudad':'Ciudad de domicilio'
                  , 'ambientesri':'Ambiente SRI'
                  , 'ilogolargo':'Logo largo', 'ilogocorto':'Logo corto'
                  , 'nporcentajeiva':'Porcentaje de IVA'
                  }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class Userform(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['email','first_name','last_name']
        widget = {'email': forms.EmailInput, }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class':'form-control'
            })

class UserPasswordForm(forms.ModelForm):
    password = forms.CharField(widget=PasswordInput)
    
    class Meta:
        model = User
        fields = ['password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class':'form-control'
            })
