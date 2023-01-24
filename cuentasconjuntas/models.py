from django.db import models

from bases.models import ClaseModelo

from pais.models import Bancos
from clientes.models import Datos_generales
from empresa import models as Empresa_modelo
from operaciones.models import Notas_debito_cabecera

class Cuentas_bancarias(ClaseModelo):
    TIPOS_DE_CUENTAS = (
        ('A', 'Ahorro'),
        ('C', 'Corriente'),
    )
    cxcliente=models.OneToOneField(Datos_generales,
        to_field="cxcliente", on_delete=models.CASCADE)
    cxbanco = models.ForeignKey(Bancos, on_delete=models.RESTRICT
        , related_name="banco_cuenta")
    cxtipocuenta=models.CharField(
        max_length=1, null=False, choices=TIPOS_DE_CUENTAS,
        help_text='A-ahorro / C-corriente'
    )
    cxcuenta=models.CharField(max_length=15,null=False,
        help_text='Número de cuenta'
    )
    lactiva=models.BooleanField(default=True,)

    def __str__(self):
        return '{} Cta. {}'.format(self.cxbanco,self.cxcuenta)


class Transferencias(ClaseModelo):
    cuentaorigen = models.ForeignKey(Cuentas_bancarias, on_delete=models.CASCADE)
    cuentadestino = models.ForeignKey(Empresa_modelo.Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True, related_name="banco_destino")
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ndevolucion = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dmovimiento = models.DateField
    cxtransferencia = models.CharField(max_length=10)

class Debitos(ClaseModelo):
    dmovimiento = models.DateField
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cuentabancaria = models.ForeignKey(Cuentas_bancarias, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=60)
    notadedebito = models.OneToOneField(Notas_debito_cabecera, on_delete=models.CASCADE)

class Movimientos(ClaseModelo):
    TIPOS_DE_MOVIMIENTOS = (
        ('R', 'Recuperación'),
        ('D', 'Débito'),
        ('P', 'Protesto'),
        ('T', 'Transferencia'),
        ('C', 'Cobranza'),
    )
    cuentabancaria = models.ForeignKey(Cuentas_bancarias, on_delete=models.CASCADE)
    dmovimiento = models.DateField
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cxtipo = models.CharField(max_length=2, choices=TIPOS_DE_MOVIMIENTOS)
    cxmovimiento = models.CharField(max_length=10)
