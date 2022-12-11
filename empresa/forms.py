from dataclasses import fields
from tkinter import Widget
from django import forms
from .models import Clases_cliente, Datos_participantes, \
    Tipos_factoring, Tasas_factoring, Cuentas_bancarias

class ParticipanteForm(forms.ModelForm):
    # ctnombre = forms.CharField(widget=forms.TextInput, label="Nombre completo")
    # cxparticipante = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model=Datos_participantes
        
        fields=['cxtipoid', 'cxparticipante', 'ctnombre'
            , 'cxlocalidad', 'ctdireccion'
            ,'cttelefono1', 'cttelefono2', 'ctemail'
            , 'ctemail2', 'ctcelular','ctgirocomercial', 'cxusuariocrea']
        labels={'cxtipoid':'Tipo cliente', 'cxparticipante':'Identificación'
            ,'ctnombre': 'Nombre completo', 'cxlocalidad':'Localidad'
            , 'ctdireccion':'Dirección', 'cttelefono1': 'Teléfono principal'
            , 'cttelefono2':'Teléfono secundario', 'ctemail':'Email 1'
            , 'ctemail2':'Email 2', 'ctcelular':'Celular'
            ,'ctgirocomercial':'Giro comercial'}        
        widgets={'ctdireccion': forms.Textarea(attrs={'rows': '3'})
                , 'ctgirocomercial':forms.Textarea(attrs={'rows': '5'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['cxtipoid'].empty_label="Seleccione tipo de identificación"

    def clean(self) :
        try:
            sc = Datos_participantes.objects.get(
                cxparticipante = self.cleaned_data['cxparticipante']
            )
            if not self.instance.pk:
                raise forms.ValidationError("Identificación ya existe")
            elif self.instance.pk != sc.pk:
                raise forms.ValidationError("Cambio no permitido. Coincide con otro registro")
        except Datos_participantes.DoesNotExist:
            pass
        return self.cleaned_data

class TipoFactoringForm(forms.ModelForm):
    
    class Meta:
        model = Tipos_factoring

        fields=[
            'cxtipofactoring', 'cttipofactoring', 'ctabreviacion','cxmoneda'
            ,'lmanejalineafactoring', 'lanticipatotalnegociado', 'ndiasgracia', 'lpermitediasferiados'
            ,'lmanejacondicionesoperativas', 'lcargagaoa', 'lgeneradcenaceptacion', 'lgeneragaoenaceptacion'
            ,'lesnegociada', 'lcobramorabc', 'ctinicialesliquidacioncobranza'
            ,'lacumulagaoaatasagao', 'lfactoringproveedores', 'ctinicialesasignacion'
        ]
        labels={
            'cxtipofactoring':'Código', 'cttipofactoring':'Descripción'
            , 'ctabreviacion':'Nombre corto','cxmoneda':'Moneda'
            ,'lmanejalineafactoring':'Maneja línea de factoring'
            , 'lanticipatotalnegociado':'Anticipa el total negociadi'
            , 'ndiasgracia':'Días de gracia'
            , 'lpermitediasferiados':'Permite vencimiento en fin de semana y días feriado'
            ,'lmanejacondicionesoperativas':'Maneja condiciones operativas'
            , 'lcargagaoa':'Carga comisión adicional a documentos vencidos'
            , 'lgeneradcenaceptacion':'Carga descuento en negociación'
            , 'lgeneragaoenaceptacion':'Carga comisión en negociación'
            , 'lesnegociada':'Es cartera de otro factor'
            , 'lcobramorabc':'Cobra intereses del banco central'
            , 'ctinicialesliquidacioncobranza': 'Iniciales de liquidación de cobranzas'
            ,'lacumulagaoaatasagao':'Suma la tasa de comisión adicional a la tasa negociada'
            , 'lfactoringproveedores':'Factoring proveedores'
            , 'ctinicialesasignacion':'Iniciales de asignaciones aceptadas'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class TasaFactoringForm(forms.ModelForm):
    
    class Meta:
        model = Tasas_factoring

        fields=[
            'cxtasa', 'cttasa', 'lflat','ndiasperiocidad'
            ,'limprimeenreporte', 'ctdescripcionenreporte'
            , 'lcargaiva', 'lsobreanticipo'
        ]
        labels={
            'cxtasa':'Código', 'cttasa':'Descripción'
            , 'lflat':'Flat','ndiasperiocidad': 'Días de periocidad'
            , 'limprimeenreporte':'Se imprime en reportes'
            , 'ctdescripcionenreporte':'Nombre en reportes'
            , 'lcargaiva':'Carga IVA'
            , 'lsobreanticipo': 'Cálculo sobre el valor anticipado'
        }
        widgets={'ctdescripcionenreporte': forms.Textarea(attrs={'rows': '1'})
                }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class ClasesParticipantesForm(forms.ModelForm):
    class Meta:
        model = Clases_cliente

        fields = [ 'cxclase']
        labels={'cxclase':'Clase'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class CuentaBancariaForm(forms.ModelForm):
    
    class Meta:
        model = Cuentas_bancarias

        fields=[
            'cxbanco', 'cxcuenta', 'lactiva',
        ]
        labels={
            'cxbanco':'Banco', 'cxcuenta':'Número de cuenta'
            , 'lactiva':'Activa',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
