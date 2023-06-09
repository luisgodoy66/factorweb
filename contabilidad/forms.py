from django import forms
from .models import Cuentas_especiales, Plan_cuentas, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring, Factura_venta
from empresa.models import Cuentas_bancarias, Tipos_factoring, Puntos_emision

class CuentasEspecialesForm(forms.ModelForm):
    class Meta:
        model=Cuentas_especiales
        fields=[ 'cuentaporcobrar','pagoconcajachica', 'sobrepago', 'cuentaconjunta'
            , 'protesto', 'cuentaivaganado', 'cuentagananciaejercicio'
            , 'cuentaperdidaejercicio', 'cuentagananciaejercicioanterior'
            , 'cuentaperdidaejercicioanterior'
        ]
        labels={'cuentaporcobrar' :'Cuenta por cobrar'
                ,'pagoconcajachica':'Pago con caja chica'
                , 'sobrepago':'Sobrepago'
                , 'cuentaconjunta':'Cuenta compartida'
                , 'protesto':'Protesto'
                , 'cuentaivaganado':'IVA ganado'
                , 'cuentagananciaejercicio':'Ganancia del ejercicio actual'
                , 'cuentaperdidaejercicio':'Pérdida del ejercicio actual'
                , 'cuentagananciaejercicioanterior':'Ganancia del ejercicio anterior'
                , 'cuentaperdidaejercicioanterior':'Pérdida del ejercicio anterior'
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        for f in iter(self.fields):
            self.fields[f].widget.attrs.update({
                'class':'form-control'
            })

        if empresa:
            self.fields['cuentaporcobrar'].queryset = Plan_cuentas.objects\
                .filter(empresa=empresa, leliminado = False, ldetalle=True)\
                .order_by('cxcuenta')
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
        fields = ['tipofactoring', 'cuenta']
        labels = {'tipofactoring':'Tipo de factoring', 'cuenta':'Cuenta contable'}

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
        self.fields['demision'].widget.attrs['readonly']=True
        self.fields['nvalor'].widget.attrs['readonly']=True
        self.fields['niva'].widget.attrs['readonly']=True
        self.fields['nbaseiva'].widget.attrs['readonly']=True
        self.fields['nbasenoiva'].widget.attrs['readonly']=True

        if empresa:
            self.fields['puntoemision'].queryset = Puntos_emision.objects\
                .filter(empresa=empresa, leliminado = False)
                  