from django import forms
from .models import Cuentas_especiales, Plan_cuentas, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring
from empresa.models import Cuentas_bancarias, Tipos_factoring, Tasas_factoring

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
                , 'sobrepago':'sbrepago'
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
