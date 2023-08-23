# from dataclasses import fields
from django import forms

from .models import  Cuentas_bancarias, Datos_generales, Linea_Factoring\
    , Personas_juridicas , Personas_naturales, Cupos_compradores\
    , Datos_compradores, Clases_cliente
from empresa.models import Localidades, Datos_participantes
from pais.models import Bancos

from datetime import date

class ClienteForm(forms.ModelForm):
    # dinicioactividades = forms.DateInput()
    
    class Meta:
        model=Datos_generales
        fields=['cxcliente','cxtipocliente', 'cxlocalidad',]
        labels={'cxcliente':'Identificación','cxtipocliente':'Tipo'
            , 'cxlocalidad':'Sucursal de atención'
        }
    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxlocalidad'].queryset = Localidades.objects\
                .filter(empresa=empresa, lactiva = True, leliminado = False)
            
class CompradorForm(forms.ModelForm):
    
    class Meta:
        model=Datos_compradores
        fields=[ 'cxclase', 'cxestado']
        labels={'cxclase':'Clase', 'cxestado':'Estado'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxclase'].queryset = Clases_cliente.objects\
                .filter(empresa=empresa, leliminado = False)

class PersonaNaturalForm(forms.ModelForm):
    
    class Meta:
        model=Personas_naturales
        fields=['cxcliente','dnacimiento', 'cxsexo', 'cxestadocivil'
            , 'cxconyuge', 'ctnombrenegocio', 'ctnombreconyuge'
            , 'ctprofesion']
        labels={'cxcliente':'Cliente','dnacimiento':'Nacimiento'
            , 'cxsexo':'Sexo', 'cxestadocivil':'Estado civil'
            , 'cxconyuge':'Id. cónyuge', 'ctnombrenegocio':'Nombre de negocio'
            , 'ctnombreconyuge':'Nombre de cónyuge'
            , 'ctprofesion':'Profesión'
        }
        widgets = {
            'dnacimiento': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        # self.fields['dnacimiento'].widget.attrs['readonly']=True

class PersonaJuridicaForm(forms.ModelForm):
    dvencimientocargorepresentante1 = forms.DateInput
    dvencimientocargorepresentante2 = forms.DateInput
    dvencimientocargorepresentante3 = forms.DateInput

    class Meta:
        model=Personas_juridicas
        fields=['cxcliente','ctnombrecorto', 'cxtipoempresa', 'ctcontacto'
            , 'ladministrasocios', 'ladministraindividual', 'ctobjetosocial'
            , 'cxrepresentante1', 'ctrepresentante1'
            , 'dvencimientocargorepresentante1', 'ctcargorepresentante1'
            , 'cxestadocivilrepresentante1', 'cttelefonorepresentante1'
            , 'cxrepresentante2', 'ctrepresentante2'
            , 'dvencimientocargorepresentante2', 'ctcargorepresentante2'
            , 'cxestadocivilrepresentante2', 'cttelefonorepresentante2'
            , 'cxrepresentante3', 'ctrepresentante3'
            , 'dvencimientocargorepresentante3', 'ctcargorepresentante3'
            , 'cxestadocivilrepresentante3', 'cttelefonorepresentante3'
            ]
        labels={'cxcliente':'Cliente','ctnombrecorto':'Nombre corto'
            , 'cxtipoempresa':'Tipo de empresa', 'ctcontacto':'Contacto'
            , 'ladministrasocios':'Administran socios'
            , 'ladministraindividual':'Administración individual'
            , 'ctobjetosocial':'Objeto social'
            , 'cxrepresentante1':'Cédula de representante legal'
            , 'ctrepresentante1':'Nombre de representate legal'
            , 'dvencimientocargorepresentante1':'Vencimiento de cargo'
            , 'ctcargorepresentante1':'Cargo de representate legal'
            , 'cxestadocivilrepresentante1':'Estado civil'
            , 'cttelefonorepresentante1':'Teléfono '
            , 'cxrepresentante2':'Cédula de representante legal'
            , 'ctrepresentante2':'Nombre de representate legal'
            , 'dvencimientocargorepresentante2':'Vencimiento de cargo'
            , 'ctcargorepresentante2':'Cargo de representate legal'
            , 'cxestadocivilrepresentante2':'Estado civil'
            , 'cttelefonorepresentante2':'Teléfono '
            , 'cxrepresentante3':'Cédula de representante legal'
            , 'ctrepresentante3':'Nombre de representate legal'
            , 'dvencimientocargorepresentante3':'Vencimiento de cargo'
            , 'ctcargorepresentante3':'Cargo de representate legal'
            , 'cxestadocivilrepresentante3':'Estado civil'
            , 'cttelefonorepresentante3':'Teléfono '
        }
        widgets={'ctnombrecorto': forms.Textarea(attrs={'rows': '1'})
            , 'ctcontacto':forms.Textarea(attrs={'rows': '1'})
            , 'ctobjetosocial':forms.Textarea(attrs={'rows': '3'})
            , 'ctrepresentante1':forms.Textarea(attrs={'rows': '1'})
            , 'ctrepresentante2':forms.Textarea(attrs={'rows': '1'})                , 'ctrepresentante3':forms.Textarea(attrs={'rows': '1'})
            ,'dvencimientocargorepresentante1': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
            'dvencimientocargorepresentante2': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
            'dvencimientocargorepresentante3': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
        }

                
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        # self.fields['dvencimientocargorepresentante1'].widget.attrs['readonly']=True
        # self.fields['dvencimientocargorepresentante2'].widget.attrs['readonly']=True
        # self.fields['dvencimientocargorepresentante3'].widget.attrs['readonly']=True
        self.fields['dvencimientocargorepresentante1'].widget.attrs['value']=date.today
        self.fields['dvencimientocargorepresentante2'].widget.attrs['value']=date.today
        self.fields['dvencimientocargorepresentante3'].widget.attrs['value']=date.today

class LineaFactoringForm(forms.ModelForm):
    class Meta:
        model=Linea_Factoring
        fields=['cxcliente','nvalor', 'cxmoneda', 'lconrecurso']
        labels={'cxcliente':'Cliente','nvalor':'Valor'
            , 'cxmoneda':'Moneda', 'lconrecurso':'Con recurso'

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class CuposCompradoresForm(forms.ModelForm):
    class Meta:
        model=Cupos_compradores
        fields=['cxcliente', 'cxcomprador','cxmoneda', 'ncupocartera'
            , 'lactivo', 'lsenotifica']
        labels={'cxcliente':'Cliente', 'cxcomprador':'Deudor'
            ,'cxmoneda': 'Moneda', 'ncupocartera':'Cupo de cartera'
            # , 'cxmodalidadcobranza':'Modalidad de cobranza'
            , 'lactivo': 'Activo', 'lsenotifica':'Se notifica de operación al deudor', }        

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxcliente'].queryset = Datos_generales.objects\
                .filter(empresa=empresa, leliminado = False)
            self.fields['cxcomprador'].queryset = Datos_compradores.objects\
                .filter(empresa=empresa, leliminado = False)

class CuentasBancariasForm(forms.ModelForm):
    class Meta:
        model=Cuentas_bancarias
        fields=['cxbanco', 'cxtipocuenta', 'cxcuenta', 'lpropia'
            , 'lactiva', 'cxtipoidpropietario'
            , 'cxidpropietario','ctnombrepropietario', 'cxparticipante'
        ]
        labels={'cxbanco':'Banco', 'cxtipocuenta':'Tipo de cuenta'
            , 'cxcuenta':'Número de cuenta', 'lpropia':'Es propia'
            , 'lactiva':'Está activa'
            , 'cxtipoidpropietario':'Tipo de id de propietario'
            , 'cxidpropietario': 'Id de propietario'
            , 'ctnombrepropietario':'Nombre de propietario'}

        widgets={'ctnombrepropietario': forms.Textarea(attrs={'rows': '2'}), }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxbanco'].queryset = Bancos.objects\
                .filter(empresa=empresa, leliminado = False)
            deudores = Datos_compradores.objects\
                .filter(empresa = empresa).values_list('cxcomprador__id')
            self.fields['cxparticipante'].queryset = Datos_participantes.objects\
                .filter(empresa=empresa, leliminado = False, id__in = deudores)

