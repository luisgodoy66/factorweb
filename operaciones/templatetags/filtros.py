from django import template
register = template.Library()

@register.filter
def running_saldo(sales_list):
    return sum(d.get('nsaldo') for d in sales_list)

@register.filter
def running_valor(sales_list):
    return sum(d.nvalor for d in sales_list)

@register.filter
def running_total(sales_list):
    return sum(d.get('ntotal') for d in sales_list)

@register.filter
def running_total2(sales_list):
    return sum(d.ntotal for d in sales_list)    

@register.filter
def running_aplicado(sales_list):
    return sum(d.aplicado() for d in sales_list)    

@register.filter
def suma(valor1, valor2):
    return valor1 + valor2