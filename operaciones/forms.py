from cProfile import label
from dataclasses import fields
from pyexpat import model
from django import forms
from .models import Condiciones_operativas_detalle, Datos_operativos, \
    Asignacion, Movimientos_maestro, Condiciones_operativas_cabecera, Anexos\
        , Desembolsos
from datetime import date
from solicitudes import models as ModelosSolicitudes

class DatosOperativosForm(forms.ModelForm):
    dalta = forms.DateInput

    class Meta:
        model=Datos_operativos
        fields=[
            'cxcliente', 'dalta', 'cxclase', 'nporcentajeanticipo'
            ,'ntasacomision', 'ntasadescuentocartera', 'ntasagaoa'
            , 'cxbeneficiarioasignacion', 'ctbeneficiarioasignacion'
            , 'cxbeneficiariocobranzas', 'ctbeneficiariocobranzas'
        ]
        labels={'cxcliente':'Cliente', 'dalta':'Fecha de alta'
            , 'cxclase':'Clase', 'nporcentajeanticipo':'% Anticipo'
            ,'ntasacomision':'Tasa comisión'
            , 'ntasadescuentocartera':'Tasa de descuento de cartera'
            , 'ntasagaoa':'Tasa de comisión adicional'
            , 'cxbeneficiarioasignacion': 'Id. beneficiario asignación'
            , 'ctbeneficiarioasignacion': 'Nombre de beneficiario de asignación'
            , 'cxbeneficiariocobranzas':'Id. beneficiario cobranzas'
            , 'ctbeneficiariocobranzas': 'Nombre de beneficiario de cobranzas'
        }
        widgets={'ctbeneficiarioasignacion': forms.Textarea(attrs={'rows': '2'})
            , 'ctbeneficiariocobranzas': forms.Textarea(attrs={'rows': '2'}), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['dalta'].widget.attrs['readonly']=True

class AsignacionesForm(forms.ModelForm):
    class Meta:
        model=Asignacion
        fields=['cxcliente', 'nanticipo', 'nvalor', 'ngao', 'ndescuentodecartera'
            , 'dnegociacion', 'ddesembolso', 'ctinstrucciondepago', 'niva'
        ]
        labels={'cxcliente':'Cliente', 'nanticipo':'Anticipo'
            , 'nvalor':'Valor', 'ngao':'Comisión'
            , 'ndescuentodecartera':'Descuento de cartera'
            , 'dnegociacion':'Negociación', 'ddesembolso':'Desembolso'
            , 'ctinstrucciondepago':'Instrucción de pago', 'niva':'IVA'
        }
        widgets={'ctinstrucciondepago': forms.Textarea(attrs={'rows': '2'}), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        # self.fields['ncantidaddocumentos'].widget.attrs['readonly']=True
        self.fields['nvalor'].widget.attrs['readonly']=True
        self.fields['ngao'].widget.attrs['readonly']=True
        self.fields['niva'].widget.attrs['readonly']=True
        self.fields['ndescuentodecartera'].widget.attrs['readonly']=True
        self.fields['nanticipo'].widget.attrs['readonly']=True
        self.fields['dnegociacion'].widget.attrs['value']=date.today
        self.fields['dnegociacion'].widget.attrs['readonly']=True
        self.fields['ddesembolso'].widget.attrs['value']=date.today
        self.fields['ddesembolso'].widget.attrs['readonly']=True

class DesembolsarForm(forms.ModelForm):
    class Meta:
        model=Desembolsos
        fields=['cxtipooperacion', 'cxoperacion', 'cxcliente', 'nvalor'
            ,'cxformapago', 'cxcuentapago', 'cxbeneficiario', 'ctbeneficiario'
        ]
        labels={'cxformapago':'Forma de pago'
            , 'cxcuentapago':'Cuenta de origen de fondos'
            , 'nvalor':"Valor a pagar", 'ctbeneficiario':'Beneficiario de cheque'
            , 'cxcliente':'Id de cliente', 'cxoperacion':'Código de operación'
            , 'cxbeneficiario':'id de beneficiario'
        }
        # widgets={'ctinstrucciondepago': forms.Textarea(attrs={'rows': '2'}), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['nvalor'].widget.attrs['readonly']=True

class MaestroMovimientosForm(forms.ModelForm):
    class Meta:
        model=Movimientos_maestro
        fields=['cxmovimiento', 'ctmovimiento', 'cxsigno', 'nprioridad'
            , 'lcargadescuentocartera', 'lcolateral', 'cxmovimientopadre']
        labels={'cxmovimiento':'Movimiento', 'ctmovimiento':'Descripción'
            , 'cxsigno': 'Signo', 'nprioridad': 'Prioridad'
            , 'lcargadescuentocartera':'Carga descuento de cartera'
            , 'lcolateral': 'Afecta a cartera'
            , 'cxmovimientopadre':'Movimiento padre'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class CondicionesOperativasForm(forms.ModelForm):
    class Meta:
        model = Condiciones_operativas_cabecera
        fields=['ctcondicion', 'cxtipofactoring', 'lactiva'
            , 'laplicaafacturaspuras', 'laplicaaaccesorios']
        labels={'ctcondicion':'Descripción', 'cxtipofactoring':'Tipo de factoring'
            , 'lactiva':'Activa', 'laplicaafacturaspuras':'Aplica a facturas puras'
            , 'laplicaaaccesorios':'Aplica a facturas con accesorios'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class DetalleCondicionesOperativasForm(forms.ModelForm):
    class Meta:
        model = Condiciones_operativas_detalle
        fields=['cxcondicion','cxclasecliente','cxclasecomprador'
            ,'nplazodesde','nplazohasta','nporcentajeanticipo'
            ,'ntasagao','ntasadescuento'
        ]        
        labels={'cxcondicion':'Id. condición'
            ,'cxclasecliente':'Clase de cliente'
            ,'cxclasecomprador':'Clase de comprador'
            ,'nplazodesde':'Desde'
            ,'nplazohasta':'Hasta','nporcentajeanticipo':'% Anticipo'
            ,'ntasadescuento':'Tasa de descuento'
            ,'ntasagao':'Tasa de comisión'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class TasasDocumentosForm(forms.ModelForm):
    # demision = forms.DateInput()
    
    class Meta:
        model=ModelosSolicitudes.Documentos
        
        fields=['ntotal',
            'nporcentajeanticipo', 'ntasacomision', 'ntasadescuento'
            ,'nanticipo', 'ngao', 'ndescuentocartera'
        ]
        labels={
            'nporcentajeanticipo':'% Anticipo'
            , 'ntasacomision':"Tasa de comisión"
            , 'ntasadescuento': "Tasa de descuento"
            , 'nanticipo':'Anticipo'
            , 'ngao':'Comisión'
            , 'ndescuentocartera':'Descuento'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class TasasAccesoriosForm(forms.ModelForm):
    
    class Meta:
        model=ModelosSolicitudes.ChequesAccesorios
        
        fields=['ntotal',
            'nporcentajeanticipo', 'ntasacomision', 'ntasadescuento'
            ,'nanticipo', 'ngao', 'ndescuentocartera'
        ]
        labels={
            'nporcentajeanticipo':'% Anticipo'
            , 'ntasacomision':"Tasa de comisión"
            , 'ntasadescuento': "Tasa de descuento"
            , 'nanticipo':'Anticipo'
            , 'ngao':'Comisión'
            , 'ndescuentocartera':'Descuento'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class AnexosForm(forms.ModelForm):
    class Meta:
        model=Anexos

        fields=['ctnombre', 'lactivo', 'ctrutageneracion','ctrutaanexo']

        labels={'ctnombre':'Descripción', 'lactivo':'Activo'
            , 'ctrutageneracion':'Directorio de anexos generados'
            , 'ctrutaanexo': 'Ruta de archivo anexo'}

        widgets={'ctnombre': forms.Textarea(attrs={'rows': '1'}), 
            'ctrutageneracion': forms.Textarea(attrs={'rows': '1'}), 
            'ctrutaanexo':forms.Textarea(attrs={'rows':'1'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
