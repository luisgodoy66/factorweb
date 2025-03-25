from django import forms
from django.core.exceptions import ValidationError

from .models import Asignacion, Documentos, ChequesAccesorios, \
    Clientes, Niveles_aprobacion
from empresa.models import Tipos_factoring
from pais.models import Bancos
from api.models import Configuracion_slack
from operaciones.models import Documentos as DocumentosOperaciones

from datetime import date
from api.sri import SRIConsultationService

class AsignacionesForm(forms.ModelForm):

    class Meta:
        model=Asignacion
        fields=['cxcliente', 'cxtipofactoring'
            ,'nvalor', 'ncantidaddocumentos', 
        ]
        labels={'cxcliente':'Cliente', 'cxtipofactoring':'Tipo de factoring'
            ,'nvalor':'Total negociado', 'ncantidaddocumentos':'Cantidad de documentos', 
        }

    def __init__(self, *args, **kwargs,):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['ncantidaddocumentos'].widget.attrs['readonly']=True
        self.fields['nvalor'].widget.attrs['readonly']=True

        if empresa:
            self.fields['cxcliente'].queryset = Clientes.objects\
                .filter(empresa=empresa, leliminado = False)
            self.fields['cxtipofactoring'].queryset = Tipos_factoring.objects\
                .filter(empresa=empresa, leliminado = False)

class DocumentosForm(forms.ModelForm):
    demision = forms.DateInput()
    ruc = None
    class Meta:
        model=Documentos
        fields=[
            'cxcomprador', 'ctcomprador', 'ctserie1', 'ctserie2'
            ,'ctdocumento', 'demision', 'dvencimiento', 'nvalorantesiva'
            ,'niva', 'nretencioniva', 'nretencionrenta', 'ntotal'
            ,'nvalornonegociado', 'cxautorizacion_ec'
        ]
        labels={
            'cxcomprador':'Comprador'
            , 'ctcomprador':'Nombre de deudor'
            , 'ctserie1':'Establecimiento'
            , 'ctserie2':'Punto de emisión'
            , 'ctdocumento':'Documento', 'demision':'Emisión'
            , 'dvencimiento':'Vencimiento'
            , 'nvalorantesiva':'Valor antes de IVA'
            , 'niva':'IVA', 'nretencioniva':'Retención de IVA'
            , 'nretencionrenta':'Retención de impuesto a la renta'
            , 'ntotal':'Valor negociado'
            , 'nvalornonegociado':'Valor descartado'
            , 'cxautorizacion_ec':'Autorización SRI'
        }
        widgets = {
            'demision': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'datepicker', 
                    'placeholder': 'Seleccione  una fecha',
                    'type': 'date'
                    }
                    ),
            'dvencimiento': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'datepicker', 
                    'placeholder': 'Seleccione  una fecha',
                    'type': 'date'
                    }
                    ),
            'cxautorizacion_ec':forms.Textarea(attrs={'rows': '3'}),
        }
    def __init__(self, *args, **kwargs):
        self.ruc = kwargs.pop('ruc', None)
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['demision'].widget.attrs['value']=date.today
        self.fields['dvencimiento'].widget.attrs['value']=date.today
        self.fields['ntotal'].widget.attrs['readonly']=True

    def clean(self):
        tipo_doc="01"
        ambiente="2"
        cleaned_data = super().clean()
        ctserie1 = cleaned_data.get('ctserie1')
        ctserie2 = cleaned_data.get('ctserie2')
        ctdocumento = cleaned_data.get('ctdocumento')
        demision = cleaned_data.get('demision')
        cxautorizacion_ec = cleaned_data.get('cxautorizacion_ec')

        if ctdocumento:
            ctdocumento = ctdocumento.zfill(9)
            cleaned_data['ctdocumento'] = ctdocumento

        if ctserie1 and ctserie2 and ctdocumento and demision \
            and cxautorizacion_ec and len(cxautorizacion_ec) != 10:

            demision_str = demision.strftime('%d%m%Y')
            expected_prefix = f"{demision_str}{tipo_doc}{self.ruc}{ambiente}{ctserie1}{ctserie2}{ctdocumento}"

            if not cxautorizacion_ec.startswith(expected_prefix):
                raise ValidationError({
                    'cxautorizacion_ec': f"La Autorización SRI corresponde a otro emisor, número de documento, fecha de emisión, ambiente o tipo de documento ( '{expected_prefix}...')."
                })
            # else:
                # service = SRIConsultationService("https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl")
                # result = service.consult_document_status(cxautorizacion_ec)
                # if "error" in result:
                #     raise ValidationError({
                #         'cxautorizacion_ec': f"Error al consultar el SRI: {result['error']}"
                #     })
                # elif "mensaje" in result:
                #     raise ValidationError({
                #         'cxautorizacion_ec': f"Error al consultar el SRI: {result['mensaje']} o tiene más de 45 días de antigüedad."
                #     })
                # else:
                    # if result[0]["estado"] != "AUTORIZADO":
                    #     raise ValidationError({
                    #         'cxautorizacion_ec': f"Documento no autorizado por el SRI o tiene más de 45 días de antigüedad."
                    #     })

                #  validar que el documento no exista
        try:
            sc = DocumentosOperaciones.objects\
                .get(ctdocumento=ctserie1+'-'+ctserie2+'-'+ctdocumento
                        , cxasignacion__cxcliente__cxcliente__cxparticipante=self.ruc
                        , leliminado=False
                    )
            
            if not self.instance.pk:
                # es nuevo registro
                if sc.empresa.id == self.empresa:
                    raise forms.ValidationError(
                        f"Documento ya negociado anteriormente en operación {sc.cxasignacion}")
                else:
                    raise forms.ValidationError("Documento negociado en otro factor.")

            elif self.instance.pk!=sc.pk:
                # es un registro existente
                raise forms.ValidationError("Cambio No Permitido.")
        except DocumentosOperaciones.DoesNotExist:
            pass
                
        except Exception as e:
            raise forms.ValidationError(f"Documento ya registrado, {e}")
        
        return cleaned_data

class ChequesForm(forms.ModelForm):
    class Meta:
        model=ChequesAccesorios
        fields=[
            'cxbanco', 'ctcuenta', 'ctcheque', 'cxpropietariocuenta'
            ,'ctgirador', 'ntotal', 'dvencimiento'
        ]
        labels={
            'cxbanco':'Banco', 'ctcuenta':'Número de cuenta'
            , 'ctcheque':'Número de cheque'
            , 'cxpropietariocuenta':'Propietario de cuenta'
            , 'ctgirador':'Girador', 'ntotal':'Valor'
            , 'dvencimiento':'Vencimiento'
        }
        # Lo importante es el formato
        widgets = {
            'dvencimiento': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'datepicker', 
                    'placeholder': 'Select a date',
                    'type': 'date'
                    }
                    ),
        }
    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dvencimiento'].widget.attrs['value']=date.today

        if empresa:
            self.fields['cxbanco'].queryset = Bancos.objects\
                .filter(empresa=empresa, leliminado = False)
            
class ClientesForm(forms.ModelForm):

    class Meta:
        model = Clientes
        fields=['cxcliente', 'ctnombre', 'ctdireccion', 'cttelefono1'
            , 'cttelefono2', 'ctemail', 'ctemail2', 'ctcelular'
            , 'ctgirocomercial', 'dinicioactividades', 'empresa']
        labels={
            'cxcliente':'Id. cliente', 'ctnombre':'Nombre de cliente'
            , 'ctdireccion':'Dirección', 'cttelefono1':'Teléfono'
            , 'cttelefono2':'Teléfono', 'ctemail':'Dirección email'
            , 'ctemail2':'Dirección email', 'ctcelular':'Celular'
            , 'ctgirocomercial':'Giro comercial'
            , 'empresa':'Empresa'
            , 'dinicioactividades': 'Inicio de actividades'
        }

        widgets={
            'ctdireccion': forms.Textarea(attrs={'rows': '3'}),
            'ctgirocomercial':forms.Textarea(attrs={'rows': '5'}),
            'dinicioactividades': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 'placeholder': 'Seleccione una fecha', 'type': 'date'}
            ),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        
    def clean(self):
        try:
            sc = Clientes.objects.get(cxcliente=self.cleaned_data["cxcliente"]
                                      , empresa= self.cleaned_data["empresa"]
            )

            if not self.instance.pk:
                raise forms.ValidationError("Identificación ya registrada anteriormente.")
            elif self.instance.pk!=sc.pk:
                raise forms.ValidationError("Cambio No Permitido.")
        except Clientes.DoesNotExist:
            pass
        return self.cleaned_data

class NivelesAprobacionForm(forms.ModelForm):
    
    class Meta:
        model = Niveles_aprobacion
        fields=['nmontominimo', 'naprobadores', 'nhorasrespuestamaxima'
                , 'configuracionslack', 'lactivo'
            ]
        labels={
            'nmontominimo':'Desde'
            , 'naprobadores':'Cantidad de aprobadores'
            , 'nhorasrespuestamaxima':'Horas para responder'
            , 'configuracionslack':'Configuración Slack'
            , 'lactivo':'Activo'
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        
        if empresa:
            self.fields['configuracionslack'].queryset = Configuracion_slack.objects\
                .filter(empresa=empresa
                        , leliminado = False, lactivo = True)

