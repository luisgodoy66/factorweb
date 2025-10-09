# import zeep
from urllib import response
from zeep import Client
from zeep.transports import Transport
from requests import Session
from django.http import HttpResponse, JsonResponse

WSDL_URL = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

class SRIConsultationService:
    def __init__(self, wsdl_url):
        self.wsdl_url = wsdl_url
        self.client = self._initialize_client()

    def _initialize_client(self):
        session = Session()
        session.verify = True  # Verificar certificado SSL
        transport = Transport(session=session)
        return Client(wsdl=self.wsdl_url, transport=transport)

    def consult_document_status(self, access_key):
        try:
            response = self.client.service.autorizacionComprobante(access_key)
            return self._parse_response(response)
        except Exception as e:
            return {"error": str(e)}

    def _parse_response(self, response):
        if hasattr(response, 'autorizaciones'):
            autorizaciones = response.autorizaciones
            if autorizaciones:
                return [{
                    "estado": autorizacion.estado,
                    "numeroAutorizacion": autorizacion.numeroAutorizacion,
                    "fechaAutorizacion": autorizacion.fechaAutorizacion,
                    "ambiente": autorizacion.ambiente,
                    "comprobante": autorizacion.comprobante,
                } for autorizacion in autorizaciones.autorizacion]
        print(response)
        return {"mensaje": "No se encontraron autorizaciones."}

# Ejemplo de uso
if __name__ == "__main__":
    access_key = "2508202501171423032100120010020000035750000007211"  # Reemplazar con clave de acceso real

    service = SRIConsultationService(WSDL_URL)
    result = service.consult_document_status(access_key)
    print(result)

import requests

def obtener_datos_contribuyente(request,ruc):
    datos = consulta_contribuyente_sri(ruc)
    return JsonResponse(datos)

def consulta_contribuyente_sri(ruc):
    # URL del servicio web del SRI
    url = f"https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc?ruc={ruc}"
    
    try:
        # Realizar la solicitud GET al servicio web
        response = requests.get(url)
        
        # Verificar si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            # Convertir la respuesta a JSON
            datos_contribuyente = response.json()
            return datos_contribuyente[0]
        else:
            # Si la solicitud no fue exitosa, devolver un mensaje de error
            return {"error": f"Error al consultar el RUC. Código de estado: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        # Manejar errores de conexión o solicitud
        return {"error": f"Error de conexión: {str(e)}"}

def consulta_estado_comprobante_sri(request, access_key):
    # Crear cliente SOAP
    try:
        client = Client(wsdl=WSDL_URL)
    except Exception as e:
        return JsonResponse({"error": f"Error al crear cliente SOAP: {str(e)}"}, safe=False)

    try:
        response = client.service.autorizacionComprobante(claveAccesoComprobante=access_key)
    except Exception as e:
        return JsonResponse({"error": f"Error al consultar estado del comprobante: {str(e)}"}, safe=False)

    # Mostrar resultados
    if response.autorizaciones is None:
        return JsonResponse({"mensaje": "No se encontró autorización en la base del SRI. "
        "Podría ser una autorización errada o una emisión de varios meses atrás."}, safe=False)
    autorizaciones = response.autorizaciones.autorizacion
    resultado = []
    for autorizacion in autorizaciones:
        resultado.append({
            "estado": autorizacion.estado,
            "numeroAutorizacion": autorizacion.numeroAutorizacion,
            "fechaAutorizacion": autorizacion.fechaAutorizacion,
            "ambiente": autorizacion.ambiente,
            "comprobante": autorizacion.comprobante,
        })
    return JsonResponse(resultado, safe=False)

# sri_utils.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def consulta_contribuyente_sri_vps_externo(ruc):
    """
    Consulta el SRI usando proxy autorizado, con manejo de errores y logs.
    """
    url = f"https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc?ruc={ruc}"
    try:
        response = requests.get(
            url,
            proxies=settings.SRI_PROXY,
            timeout=settings.SRI_TIMEOUT,
            verify=settings.SRI_VERIFY_CERT
        )
        response.raise_for_status()  # Lanza excepción si HTTP >=400
        logger.info("Conexión exitosa al SRI, status %s", response.status_code)
        # Verificar si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            # Convertir la respuesta a JSON
            datos_contribuyente = response.json()
            return datos_contribuyente[0]
        else:
            # Si la solicitud no fue exitosa, devolver un mensaje de error
            return {"error": f"Error al consultar el RUC. Código de estado: {response.status_code}"}
    
    except requests.exceptions.SSLError as e:
        logger.error("Error SSL/TLS al conectar con SRI: %s", e)
    except requests.exceptions.ProxyError as e:
        logger.error("Error de proxy al conectar con SRI: %s", e)
    except requests.exceptions.ConnectionError as e:
        logger.error("Error de conexión al SRI: %s", e)
    except requests.exceptions.Timeout as e:
        logger.error("Timeout al conectar con SRI: %s", e)
    except requests.exceptions.HTTPError as e:
        logger.error("Error HTTP al SRI: %s", e)
    except Exception as e:
        logger.error("Error inesperado al conectar con SRI: %s", e)
    
    return None  # En caso de error
