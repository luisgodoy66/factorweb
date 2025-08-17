from dataclasses import fields
from django import forms

from .models import Clases_cliente, Datos_participantes, Tipos_factoring, \
    Tasas_factoring, Cuentas_bancarias, Localidades, Puntos_emision, Otros_cargos
from pais.models import Bancos, Actividades
from datetime import datetime

class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Datos_participantes
        fields = [
            'cxtipoid', 'cxparticipante', 'ctnombre', 'ctdireccion',
            'cttelefono1', 'cttelefono2', 'ctemail', 'ctemail2', 
            'ctcelular',
            'ctgirocomercial', 'dinicioactividades', 'actividad'
        ]
        labels = {
            'cxtipoid': 'Tipo de identificación', 
            'cxparticipante': 'Identificación',
            'ctnombre': 'Nombre completo', 'ctdireccion': 'Dirección',
            'cttelefono1': 'Teléfono principal', 
            'cttelefono2': 'Teléfono secundario',
            'ctemail': 'Email 1', 'ctemail2': 'Email 2', 
            'ctcelular': 'WhatsApp',
            'ctgirocomercial': 'Giro comercial', 
            'dinicioactividades': 'Inicio de actividades',
            'actividad': 'Actividad económica'
        }
        widgets = {
            'ctdireccion': forms.Textarea(attrs={'rows': '2'}),
            'ctgirocomercial': forms.Textarea(attrs={'rows': '5'}),
            'dinicioactividades': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control'
                       , 'placeholder': 'Seleccione una fecha'
                       , 'type': 'date'}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({'class': 'form-control'})

        self.fields['cxtipoid'].empty_label = "Seleccione tipo de identificación"

        if self.empresa:
            self.fields['actividad'].queryset = Actividades.objects\
                .filter(empresa=self.empresa, leliminado=False)\
                .order_by('cxactividad')

    def clean(self):
        cleaned_data = super().clean()
        cxparticipante = cleaned_data.get('cxparticipante')
        if self.empresa and cxparticipante:
            try:
                # 27-feb-25: considerar el estad de eliminado
                existing_participant = Datos_participantes.objects\
                    .get(cxparticipante=cxparticipante
                         , leliminado=False
                         , empresa=self.empresa)
                
                if not self.instance.pk:
                    # cuando es nuevo y lo encontró
                    raise forms.ValidationError("Identificación de participante ya registrada como cliente o como deudor.")
                elif self.instance.pk != existing_participant.pk:
                    # cuando se está editando y no es el mismo
                    raise forms.ValidationError("Identificación coincide con otro registro previo de cliente o deudor.")
                else:
                    #No existe duplicidad
                    return cleaned_data
                
            except Datos_participantes.DoesNotExist:
                # No existe la identificacion
                pass

        return cleaned_data
    
class TipoFactoringForm(forms.ModelForm):
    
    class Meta:
        model = Tipos_factoring

        fields=[
            'cttipofactoring', 'ctabreviacion','cxmoneda'
            , 'lmanejalineafactoring', 'lanticipatotalnegociado'
            , 'ndiasgracia', 'lpermitediasferiados'
            , 'lmanejacondicionesoperativas', 'lcargagaoa'
            , 'lgeneradcenaceptacion', 'lgeneragaoenaceptacion'
            , 'lesnegociada', 'lcobramorabc'
            , 'ctinicialesliquidacioncobranza'
            , 'lacumulagaoaatasagao'
            # , 'lfactoringproveedores'
            , 'ctinicialesasignacion'
            , 'lcargadcenampliacionplazo'
            ,'lgenerafacturaenaceptacion', 'laplicaotroscargos'
            , 'lacumulamoraatasadc'
        ]
        labels={
            'cttipofactoring':'Descripción'
            , 'ctabreviacion':'Nombre corto','cxmoneda':'Moneda'
            , 'lmanejalineafactoring':'Maneja línea de factoring'
            , 'lanticipatotalnegociado':'Anticipa el total negociado'
            , 'ndiasgracia':'Días de gracia'
            , 'lpermitediasferiados':'Permite vencimiento en fin de semana y días feriado'
            , 'lmanejacondicionesoperativas':'Maneja condiciones operativas'
            , 'lcargagaoa':'Carga comisión adicional a documentos vencidos'
            , 'lgeneradcenaceptacion':'Carga descuento de cartera en negociación'
            , 'lgeneragaoenaceptacion':'Carga comisión en negociación'
            , 'lesnegociada':'Es cartera de otro factor'
            , 'lcobramorabc':'Cobra intereses del banco central'
            , 'ctinicialesliquidacioncobranza': 'Iniciales de liquidación de cobranzas'
            , 'lacumulagaoaatasagao':'Para vencidos, suma el % de comisión adicional al % de comisión negociada'
            # , 'lfactoringproveedores':'Factoring proveedores'
            , 'ctinicialesasignacion':'Iniciales de asignaciones aceptadas'
            , 'lcargadcenampliacionplazo':'Carga descuento de cartera en ampliaciones de plazo'
            , 'lgenerafacturaenaceptacion': 'Requiere generar factura en negociación'
            , 'laplicaotroscargos': 'Aplica otros cargos en liquidaciones al cliente'
            , 'lacumulamoraatasadc': 'Para vencidos, suma la tasa de descuento de cartera a la tasa de mora'
        }
        widgets = {
            'ndiasgracia': forms.NumberInput(
                attrs={
                    'min': '0', 'step': '1'
                }
            ),
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
            'cxtasa'
            # , 'cttasa'
            , 'lflat','ndiasperiocidad'
            ,'limprimeenreporte', 'ctdescripcionenreporte'
            , 'lcargaiva'
            , 'lsobreanticipo', 'ctinicialesentablas'
        ]
        labels={
            'cxtasa':'Código'
            # , 'cttasa':'Descripción'
            , 'lflat':'Cálculo con tasa flat'
            , 'ndiasperiocidad': 'Días de periodicidad'
            , 'limprimeenreporte':'Tasa se imprime en reportes'
            , 'ctdescripcionenreporte':'Nombre de valor en reportes'
            , 'lcargaiva':'Carga IVA'
            , 'lsobreanticipo': 'Cálculo sobre el valor anticipado'
            , 'ctinicialesentablas':'Iniciales de tasa'
        }
        widgets={
            'ctdescripcionenreporte': forms.Textarea(attrs={'rows': '1'}),
            'ndiasperiocidad': forms.NumberInput(attrs={'step': '30', 'min': '0'}),
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
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxbanco'].queryset = Bancos.objects\
                .filter(empresa=empresa, leliminado = False,)

class LocalidadForm(forms.ModelForm):
    class Meta:
        model = Localidades

        fields = [ 'ctlocalidad', 'lactiva']
        labels={'ctlocalidad':'Descripción', 'lactiva':'Activa'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class PuntoEmisionForm(forms.ModelForm):
    class Meta:
        model = Puntos_emision
        fields=[
            'cxestablecimiento', 'cxpuntoemision', 'ctdescripcion', 'ctdireccion'
            , 'lgeneracionxmldocumentoelectronico', 'lactiva', 'nultimasecuencia'
        ]
        labels={
            'cxestablecimiento':'Establecimiento', 'cxpuntoemision':'Punto de emisión'
            , 'ctdescripcion':'Descripción', 'ctdireccion':'Dirección'
            , 'lgeneracionxmldocumentoelectronico':'Generar xml', 'lactiva':'Activa'
            , 'nultimasecuencia': 'Última secuencia de factura generada'}
        
        widgets={'ctdireccion': forms.Textarea(attrs={'rows': '3'}),}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class OtroCargoForm(forms.ModelForm):
    
    class Meta:
        model = Otros_cargos

        fields=[
            'ctabreviacion', 'nvalor'
            ,'lcargaenliquidacionasignacion', 'lcargaenliquidacioncobranza'
            , 'lcargaiva', 'lactivo', 'movimiento'
        ]
        labels={
            # 'ctcargo':'Nombre',
            'ctabreviacion':'Nombre corto'
            , 'nvalor':'Valor'
            , 'lcargaenliquidacionasignacion':'Aplica a liquidación de asignación'
            , 'lcargaenliquidacioncobranza':'Aplica a liquidación de cobranza'
            , 'lcargaiva':'Carga IVA'
            , 'lactivo':'Activo'
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

