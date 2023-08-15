from django import forms

from datetime import date

from .models import Cuentas_especiales, Plan_cuentas, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring, Factura_venta\
    , Comprobante_egreso, Cuentas_diferidos, Cuentas_provisiones\
    , Diario_cabecera, Transaccion, Cuentas_cargosfactoring
from empresa.models import Cuentas_bancarias, Tipos_factoring, Puntos_emision
from clientes.models import Cuenta_transferencia

class CuentasEspecialesForm(forms.ModelForm):
    class Meta:
        model=Cuentas_especiales
        fields=[ 'pagoconcajachica', 'sobrepago', 'cuentaconjunta'
            , 'protesto', 'cuentaivaganado', 'cuentagananciaejercicio'
            , 'cuentaperdidaejercicio', 'cuentagananciaejercicioanterior'
            , 'cuentaperdidaejercicioanterior', 'ivadiferido'
            , 'liquidacionennegativo', 'comisionchequesprotestados'
        ]
        labels={ 'pagoconcajachica':'Pago con caja chica'
                , 'sobrepago':'Sobrepago'
                , 'cuentaconjunta':'Cuenta bancaria compartida'
                , 'protesto':'Protesto'
                , 'cuentaivaganado':'IVA ganado'
                , 'cuentagananciaejercicio':'Ganancia del ejercicio actual'
                , 'cuentaperdidaejercicio':'Pérdida del ejercicio actual'
                , 'cuentagananciaejercicioanterior':'Ganancia del ejercicio anterior'
                , 'cuentaperdidaejercicioanterior':'Pérdida del ejercicio anterior'
                , 'ivadiferido': 'IVA diferido'
                , 'liquidacionennegativo':'Liquidación en negativo'
                , 'comisionchequesprotestados':'Comisión por cheques protestados'
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['pagoconcajachica'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['sobrepago'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['cuentaconjunta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['protesto'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['cuentaivaganado'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['ivadiferido'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['cuentagananciaejercicio'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['cuentaperdidaejercicio'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['cuentagananciaejercicioanterior'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['cuentaperdidaejercicioanterior'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['liquidacionennegativo'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['comisionchequesprotestados'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')

class CuentasBancosForm(forms.ModelForm):
    class Meta:
        model=Cuentas_bancos
        fields = ['banco', 'cuenta']
        labels = {'banco':'banco', 'cuenta':'Cuenta contable'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cuenta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['banco'].queryset = Cuentas_bancarias.objects\
                .filter(empresa=empresa, leliminado = False, )
            
class CuentasTiposFactoringForm(forms.ModelForm):
    class Meta:
        model=Cuentas_tiposfactoring
        fields = ['tipofactoring', 'cuenta', 'cuentaporcobrar']
        labels = {'tipofactoring':'Tipo de factoring'
                  , 'cuenta':'Cuenta de operaciones'
                  , 'cuentaporcobrar':'Cuenta de facturación'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cuenta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['cuentaporcobrar'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['tipofactoring'].queryset = Tipos_factoring.objects\
                .filter(empresa=empresa, leliminado = False, )

class CuentasTasaTiposFactoringForm(forms.ModelForm):
    class Meta:
        model=Cuentas_tasasfactoring
        fields = ['tipofactoring', 'tasafactoring', 'cuenta']
        labels = {'tipofactoring':'Tipo de factoring'
                  , 'tasafactoring': 'Tasa'
                  , 'cuenta':'Cuenta contable'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cuenta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['tipofactoring'].queryset = Tipos_factoring.objects\
                .filter(empresa=empresa, leliminado = False, )

class CuentasDiferidoTasaTiposFactoringForm(forms.ModelForm):
    class Meta:
        model=Cuentas_diferidos
        fields = ['tipofactoring', 'tasafactoring', 'cuenta']
        labels = {'tipofactoring':'Tipo de factoring'
                  , 'tasafactoring': 'Tasa'
                  , 'cuenta':'Cuenta contable'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cuenta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['tipofactoring'].queryset = Tipos_factoring.objects\
                .filter(empresa=empresa, leliminado = False, )

class CuentasProvisionTasaTiposFactoringForm(forms.ModelForm):
    class Meta:
        model=Cuentas_provisiones
        fields = ['tipofactoring', 'tasafactoring', 'cuenta']
        labels = {'tipofactoring':'Tipo de factoring'
                  , 'tasafactoring': 'Tasa'
                  , 'cuenta':'Cuenta contable'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cuenta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['tipofactoring'].queryset = Tipos_factoring.objects\
                .filter(empresa=empresa, leliminado = False, )

class FacturaVentaForm(forms.ModelForm):
    class Meta:
        model=Factura_venta
        fields = ['puntoemision', 'cxnumerofactura', 'demision', 'nbasenoiva'
                  , 'cxestado', 'nvalor', 'nbaseiva', 'niva'
                  , 'cliente', 'nporcentajeiva']
        labels = {'puntoemision':'Punto de emisión'
                  , 'cxnumerofactura': 'Secuencia de factura'
                  , 'demision':'Fecha de emisión'
                  , 'nbasenoiva':'Base sin IVA'
                  , 'nbaseiva':'Base con IVA'
                  , 'nvalor':'Total'
                  , 'niva': 'IVA'}
        widgets={'demision': forms.DateInput(
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
        # self.fields['demision'].widget.attrs['readonly']=True
        self.fields['nvalor'].widget.attrs['readonly']=True
        self.fields['niva'].widget.attrs['readonly']=True
        self.fields['nbaseiva'].widget.attrs['readonly']=True
        self.fields['nbasenoiva'].widget.attrs['readonly']=True

        if empresa:
            self.fields['puntoemision'].queryset = Puntos_emision.objects\
                .filter(empresa=empresa, leliminado = False, lactiva = True)
                  
class ComprobanteEgresoForm(forms.ModelForm):
    class Meta:
        model=Comprobante_egreso
        fields = ['cxbeneficiario', 'ctrecibidopor', 'cxcuentapago', 'nvalor'
                  , 'ctcheque', 'cxcuentadestino', 'demision', 'cxformapago']
        labels = { 'demision':'Fecha de emisión'
                  , 'cxbeneficiario': 'Id. beneficiario'
                  , 'ctrecibidopor':'Recibido por'
                  , 'cxcuentapago':'Cuenta de pago'
                  , 'ctcheque':'Número de cheque'
                  , 'cxcuentadestino':'Cuenta destino'
                  , 'nvalor':'Valor'
                  }
        widgets={'demision': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control', 
                    'placeholder': 'Seleccione una fecha',
                    'type': 'date'
                    }
                    ),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        id_cliente = kwargs.pop('id_cliente', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        # self.fields['demision'].widget.attrs['readonly']=True
        self.fields['nvalor'].widget.attrs['readonly']=True

        if empresa:
            self.fields['cxcuentapago'].queryset = Cuentas_bancarias.objects\
                .filter(empresa=empresa, leliminado = False, lactiva = True)
            self.fields['cxcuentadestino'].queryset = Cuenta_transferencia.objects\
                .filter(empresa=empresa, leliminado = False, cxcliente = id_cliente)
                  
class PlanCuentasForm(forms.ModelForm):
    nnivel = forms.IntegerField(max_value=5, min_value=1)
    class Meta:
        model = Plan_cuentas
        fields = ['cxcuenta', 'ctcuenta', 'nnivel', 'ldetalle']
        labels={
            "cxcuenta": "Cuenta", 
            "ctcuenta":'Nombre de cuenta',
            "nnivel": "Nivel de la cuenta",
            "ldetalle":'Es cuenta de detalle'}
        widgets={'ctcuenta': forms.Textarea(attrs={'rows': '2'}), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })
        
class DiarioCabeceraForm(forms.ModelForm):
    class Meta:
        model = Diario_cabecera
        fields = ['ctconcepto', 'dcontabilizado', 'nvalor']
        labels = {'ctconcepto':'Concepto', 'dcontabilizado':'Fecha', 'nvalor':'Valor'}
        widgets= {'ctconcepto': forms.Textarea(attrs={'rows': '3'}),
            'dcontabilizado': forms.DateInput(
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
        self.fields['dcontabilizado'].widget.attrs['value']=date.today

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['cxcuenta', 'cxtipo', 'ctreferencia', 'nvalor']
        labels = {'cxcuenta' : 'Cuenta'
                  , 'cxtipo':'Debe/Haber'
                  , 'ctreferencia': 'Referencia'
                  , 'nvalor':'Valor'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cxcuenta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')

class CuentasCargoTiposFactoringForm(forms.ModelForm):
    class Meta:
        model=Cuentas_cargosfactoring
        fields = ['tipofactoring', 'cargo', 'cuenta']
        labels = {'tipofactoring':'Tipo de factoring'
                  , 'cargo': 'Cargo'
                  , 'cuenta':'Cuenta contable'}

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cuenta'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
            self.fields['tipofactoring'].queryset = Tipos_factoring.objects\
                .filter(empresa=empresa, leliminado = False, )

