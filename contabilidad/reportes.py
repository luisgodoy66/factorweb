import os
import json

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.staticfiles import finders

from .models import  Diario_cabecera, Transaccion

from operaciones.models import Notas_debito_cabecera, Notas_debito_detalle
from bases.models import Usuario_empresa
from empresa.models import Tasas_factoring

from xhtml2pdf import pisa

def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        result = finders.find(uri)
        if result:
                if not isinstance(result, (list, tuple)):
                        result = [result]
                result = list(os.path.realpath(path) for path in result)
                path=result[0]
        else:
                sUrl = settings.STATIC_URL        # Typically /static/
                sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                mUrl = settings.MEDIA_URL         # Typically /media/
                mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                if uri.startswith(mUrl):
                        path = os.path.join(mRoot, uri.replace(mUrl, ""))
                elif uri.startswith(sUrl):
                        path = os.path.join(sRoot, uri.replace(sUrl, ""))
                else:
                        return uri

        # make sure that file exists
        if not os.path.isfile(path):
                raise Exception(
                        'media URI must start with %s or %s' % (sUrl, mUrl)
                )
        return path

def ImpresionDiarioContable(request, diario_id):
    detalle = {}
    template_path = 'contabilidad/diario_contable_reporte.html'

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # tomar el codigo de asignacion grabado en la solicitud
    diario = Diario_cabecera.objects.filter(id= diario_id).first()
    
    if not diario:
        return HttpResponse("no encontró diario contable")

    # cuando la forma de pago es DEP es deposito de accesorios y de ahí debe
    # tomar la fecha de vencimiento
    detalle = Transaccion.objects\
        .filter(diario = diario_id, leliminado = False)

    # totales
    tot_cobro_d = detalle.filter(cxtipo='D').aggregate(tot_debe=Sum('nvalor'))
    tot_cobro_h = detalle.filter(cxtipo='H').aggregate(tot_haber=Sum('nvalor'))

    totales = {
        "debe":tot_cobro_d["tot_debe"],
        "haber":tot_cobro_h["tot_haber"]
    }


    context = {
        "diario" : diario,
        "detalle" : detalle,
        "totales": totales,
        'empresa': id_empresa.empresa
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="diario "' \
        + str(diario.cxtransaccion) + ".pdf"
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

