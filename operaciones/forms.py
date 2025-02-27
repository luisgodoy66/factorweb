from cProfile import label
from dataclasses import fields
from pyexpat import model
from django import forms

from .models import Condiciones_operativas_detalle, Datos_operativos, \
    Asignacion, Condiciones_operativas_cabecera, Anexos\
    , Desembolsos, Documentos, ChequesAccesorios, Pagare_detalle
from solicitudes import models as ModelosSolicitudes
from empresa.models import Clases_cliente, Tipos_factoring, Cuentas_bancarias\
    ,Movimientos_maestro
from datetime import date

class DatosOperativosForm(forms.ModelForm):
    dalta = forms.DateInput

    class Meta:
        model=Datos_operativos
        fields=[
            'cxcliente', 'dalta', 'cxclase', 'nporcentajeanticipo'
            ,'ntasacomision', 'ntasadescuentocartera', 'ntasagaoa'
            , 'cxbeneficiarioasignacion', 'ctbeneficiarioasignacion'
            , 'cxbeneficiariocobranzas', 'ctbeneficiariocobranzas'
            , 'cxestado', 'ntasamora'
        ]
        labels={'cxcliente':'Cliente', 'dalta':'Fecha de alta'
            , 'cxclase':'Clase', 'nporcentajeanticipo':'% Anticipo'
            ,'ntasacomision':'Tasa comisión'
            , 'ntasadescuentocartera':'Tasa de descuento de cartera'
            , 'ntasagaoa':'Tasa de comisión adicional'
            , 'cxbeneficiarioasignacion': 'Id. de beneficiario de cheque'
            , 'ctbeneficiarioasignacion': 'Nombre de beneficiario de cheque'
            , 'cxbeneficiariocobranzas':'Id. de beneficiario de cheque'
            , 'ctbeneficiariocobranzas': 'Nombre de beneficiario de cheque'
            , 'cxestado':'Estado', 'ntasamora':'Tasa de mora'
        }
        help_texts = {
            'cxcliente': 'Seleccione el cliente.',
            'dalta': 'Ingrese la fecha de alta en formato AAAA-MM-DD.',
            'cxclase': 'Seleccione la clase del cliente.',
            'nporcentajeanticipo': 'Ingrese el porcentaje de anticipo.',
            'ntasacomision': 'Ingrese la tasa de comisión.',
            'ntasadescuentocartera': 'Ingrese la tasa de descuento de cartera.',
            'ntasagaoa': 'Esta tasa se puede sumar a la tasa de comisión negociada del documento para el cálculo de la comisión adicional.',
            'cxbeneficiarioasignacion': 'Ingrese el ID del beneficiario del cheque.',
            'ctbeneficiarioasignacion': 'Ingrese el nombre del beneficiario del cheque.',
            'cxbeneficiariocobranzas': 'Ingrese el ID del beneficiario de cobranzas.',
            'ctbeneficiariocobranzas': 'Ingrese el nombre del beneficiario de cobranzas.',
            'cxestado': 'Seleccione el estado.',
            'ntasamora': 'Esta tasa se puede sumar a la tasa de descuento del documento para el cálculo del descuento de cartera vencido.'
        }
        widgets={'ctbeneficiarioasignacion': forms.Textarea(attrs={'rows': '1'})
            , 'ctbeneficiariocobranzas': forms.Textarea(attrs={'rows': '1'}), 
            'dalta': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
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

        if empresa:
            self.fields['cxclase'].queryset = Clases_cliente.objects\
                .filter(empresa=empresa, leliminado = False)

class AsignacionesForm(forms.ModelForm):
    class Meta:
        model=Asignacion
        fields=['cxcliente', 'nanticipo', 'nvalor', 'ngao', 'ndescuentodecartera'
            , 'dnegociacion', 'ddesembolso', 'ctinstrucciondepago', 'niva'
            # , 'notrocargo'
        ]
        labels={'cxcliente':'Cliente', 'nanticipo':'Anticipo'
            , 'nvalor':'Total negociado', 'ngao':'Comisión'
            , 'ndescuentodecartera':'Descuento de cartera'
            , 'dnegociacion':'Negociación', 'ddesembolso':'Desembolso'
            , 'ctinstrucciondepago':'Instrucción de pago', 'niva':'IVA'
        }
        widgets={'ctinstrucciondepago': forms.Textarea(attrs={'rows': '2'}), 
            'dnegociacion': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'datepicker', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
            'ddesembolso': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'datepicker', 
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
        # self.fields['ncantidaddocumentos'].widget.attrs['readonly']=True
        self.fields['nvalor'].widget.attrs['readonly']=True
        self.fields['ngao'].widget.attrs['readonly']=True
        self.fields['niva'].widget.attrs['readonly']=True
        self.fields['ndescuentodecartera'].widget.attrs['readonly']=True
        self.fields['nanticipo'].widget.attrs['readonly']=True
        self.fields['dnegociacion'].widget.attrs['value']=date.today
        self.fields['dnegociacion'].widget.attrs['readonly']=True
        self.fields['ddesembolso'].widget.attrs['value']=date.today
        # self.fields['ddesembolso'].widget.attrs['readonly']=True

class DesembolsarForm(forms.ModelForm):
    class Meta:
        model=Desembolsos
        fields=['cxtipooperacion', 'cxoperacion', 'cxcliente', 
                'nvalor','cxformapago', 'cxcuentapago', 
                'cxbeneficiario', 'ctbeneficiario', 'cxcuentadestino'
        ]
        labels={'cxformapago':'Forma de pago', 
                'cxcuentapago':'Cuenta de origen de fondos', 
                'nvalor':"Valor a pagar", 
                'ctbeneficiario':'Beneficiario de cheque', 
                'cxcliente':'Id de cliente', 
                'cxoperacion':'Código de operación', 
                'cxbeneficiario':'id de beneficiario',
                'cxcuentadestino':'Destino de transferencia'
        }
        widgets={
            'ctbeneficiario':forms.Textarea(attrs={'rows':'1'}, )}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['nvalor'].widget.attrs['readonly']=True
        self.fields['ctbeneficiario'].widget.attrs['readonly']=True
        self.fields['cxcuentadestino'].required = False
        # Al usar el atributo disabled se muestra el valor en la forma
        # pero no se carga en el metodo POST, y al volver a mostrar la
        # forma por algun error, no se muestra el campo nuevamente
        self.fields['cxcuentadestino'].widget.attrs['disabled']=True
        # # al usar la propiedad disabled no se envía el valor al servidor
        # # y no se muestra valor alguno en el campo en el formulario
        # self.fields['cxcuentadestino'].disabled = True

        if empresa:
            self.fields['cxcuentapago'].queryset = Cuentas_bancarias\
                .objects.filter(empresa=empresa, \
                                leliminado = False, \
                                lactiva = True)

    def clean(self):
        cleaned_data = super().clean()
        cxformapago = cleaned_data.get('cxformapago')
        cxcuentapago = cleaned_data.get('cxcuentapago')
        cxcuentadestino = cleaned_data.get('cxcuentadestino')
        ctbeneficiario = cleaned_data.get('ctbeneficiario')

        if cxformapago in ['TRA'] and not cxcuentadestino:
            self.add_error('cxcuentadestino', 
                           'Debe marcar una cuenta del cliente para transferencias en Participantes/Clientes/Cuentas bancarias.')

        if cxformapago in ['CHE'] and not ctbeneficiario:
            self.add_error('ctbeneficiario', 
                           'Debe registrar un beneficiario en los datos operativos del cliente.')

        if cxformapago in ['TRA', 'CHE'] and not cxcuentapago:
            self.add_error('cxcuentapago', 
                           'Debe seleccionar una cuenta de origen de fondos si la forma de pago es cheque o transferencia.')

        return cleaned_data
    
class MaestroMovimientosForm(forms.ModelForm):
    class Meta:
        model=Movimientos_maestro
        fields=['cxmovimiento', 'ctmovimiento', 'cxsigno', 'litemfactura'
            , 'lcolateral', 'cxmovimientopadre', 'lcargo']
        labels={'cxmovimiento':'Código', 'ctmovimiento':'Descripción'
            , 'cxsigno': 'Signo', 'litemfactura': 'Es ítem de factura'
            , 'lcolateral': 'Afecta a cartera', 'lcargo':'Es cargo (No ítem factura)'
            , 'cxmovimientopadre':'Movimiento padre'}

    def __init__(self, *args, **kwargs):
        nuevo = kwargs.pop('nuevo', False)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        if nuevo:
            self.fields['cxmovimiento'].widget.attrs['readonly']=False
        else:
            self.fields['cxmovimiento'].widget.attrs['readonly']=True

class CondicionesOperativasForm(forms.ModelForm):
    class Meta:
        model = Condiciones_operativas_cabecera
        fields=['ctcondicion', 'cxtipofactoring'
            , 'laplicaafacturaspuras', 'laplicaaaccesorios']
        labels={'ctcondicion':'Descripción', 'cxtipofactoring':'Tipo de factoring'
            , 'laplicaafacturaspuras':'Aplica a facturas puras'
            , 'laplicaaaccesorios':'Aplica a facturas con accesorios'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxtipofactoring'].queryset = Tipos_factoring.objects\
                .filter(empresa=empresa, leliminado = False)

class DetalleCondicionesOperativasForm(forms.ModelForm):
    class Meta:
        model = Condiciones_operativas_detalle
        fields=['cxcondicion','cxclasecliente','cxclasecomprador'
            ,'nplazodesde','nplazohasta','nporcentajeanticipo'
            ,'ntasagao','ntasadescuento'
        ]        
        labels={'cxcondicion':'Id. condición'
            ,'cxclasecliente':'Clase de cliente'
            ,'cxclasecomprador':'Clase de deudor'
            ,'nplazodesde':'Desde'
            ,'nplazohasta':'Hasta','nporcentajeanticipo':'% Anticipo'
            ,'ntasadescuento':'Tasa de descuento'
            ,'ntasagao':'Tasa de comisión'
        }
        
    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxclasecliente'].queryset = Clases_cliente.objects\
                .filter(empresa=empresa, leliminado = False)
            self.fields['cxclasecomprador'].queryset = Clases_cliente.objects\
                .filter(empresa=empresa, leliminado = False)

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
    # fanexo = forms.FileField(widget=forms.FileInput(attrs={'class':'form-control-file'}))
    ctnombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))    
    class Meta:
        model=Anexos

        fields=['ctnombre', 'lactivo', 'fanexo', 'cxtipocliente']

        labels={'ctnombre':'Descripción', 'lactivo':'Activo'
            , 'fanexo': 'Ruta de archivo anexo'
            , 'cxtipocliente': 'Tipo de cliente'
            }

        widgets={'ctnombre': forms.Textarea(attrs={'rows': '1'}), 
            }

class TasasAPAccesoriosForm(forms.ModelForm):
    # demision = forms.DateInput()
    
    class Meta:
        model=ChequesAccesorios
        
        fields=['ntasacomisionap', 'ntasadescuentoap'
        ]
        labels={ 'ntasacomisionap':"GAOA adicional"
            , 'ntasadescuentoap': "Tasa de descuento"
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class TasasAPDocumentoForm(forms.ModelForm):
    # demision = forms.DateInput()
    
    class Meta:
        model=Documentos
        
        fields=['ntasacomisionap', 'ntasadescuentoap'
        ]
        labels={ 'ntasacomisionap':"GAOA adicional"
            , 'ntasadescuentoap': "Tasa de descuento"
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

class CuotasForm(forms.ModelForm):

    class Meta:
        model=Pagare_detalle
        fields=['dfechapago', ]
        labels={'dfechapago':'Fecha de pago',
        }
        widgets = {
            'dfechapago': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
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
        # self.fields['ddeposito'].widget.attrs['value']=date.today
