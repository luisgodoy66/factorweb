# import zeep
import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from zeep import Client
from zeep.transports import Transport

WSDL_URL = getattr(
    settings,
    "SRI_WSDL_URL",
    "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
)
DEFAULT_SRI_CONTRIBUYENTE_URL = (
    "https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/"
    "ConsolidadoContribuyente/obtenerPorNumerosRuc?ruc={ruc}"
)

logger = logging.getLogger(__name__)

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


def _build_retry_session():
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _get_sri_contribuyente_endpoints(ruc):
    endpoints = getattr(settings, "SRI_CONTRIBUYENTE_ENDPOINTS", None)
    if not endpoints:
        endpoints = [DEFAULT_SRI_CONTRIBUYENTE_URL]

    if isinstance(endpoints, str):
        endpoints = [endpoints]

    normalized = []
    for endpoint in endpoints:
        normalized.append(endpoint.format(ruc=ruc) if "{ruc}" in endpoint else endpoint)
    return normalized


def _extract_contribuyente(payload):
    if isinstance(payload, list) and payload:
        first = payload[0]
        if isinstance(first, dict):
            return first
    if isinstance(payload, dict) and payload.get("razonSocial"):
        return payload
    return None

def obtener_datos_contribuyente(request, ruc):
    datos = consulta_contribuyente_sri(ruc)
    return JsonResponse(datos)


def consulta_contribuyente_sri(ruc):
    if not ruc or not str(ruc).isdigit() or len(str(ruc)) != 13:
        return {"error": "RUC invalido. Debe tener 13 digitos numericos."}

    cache_key = f"sri:ruc:{ruc}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    proxies = getattr(settings, "SRI_PROXY", None)
    timeout = getattr(settings, "SRI_TIMEOUT", 20)
    verify_cert = getattr(settings, "SRI_VERIFY_CERT", True)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "factorweb/1.0",
    }

    session = _build_retry_session()
    endpoints = _get_sri_contribuyente_endpoints(ruc)

    for endpoint in endpoints:
        try:
            response = session.get(
                endpoint,
                headers=headers,
                proxies=proxies,
                timeout=timeout,
                verify=verify_cert,
            )

            if response.status_code == 200:
                payload = response.json()
                datos_contribuyente = _extract_contribuyente(payload)
                if datos_contribuyente:
                    cache_ttl = getattr(settings, "SRI_RUC_CACHE_SECONDS", 12 * 60 * 60)
                    cache.set(cache_key, datos_contribuyente, timeout=cache_ttl)
                    return datos_contribuyente

                logger.warning("SRI respondio 200 pero sin estructura esperada. endpoint=%s", endpoint)
                continue

            if response.status_code in (403, 451):
                logger.warning(
                    "Posible bloqueo geografico del SRI. endpoint=%s status=%s",
                    endpoint,
                    response.status_code,
                )
                continue

            logger.warning("Fallo consulta SRI endpoint=%s status=%s", endpoint, response.status_code)

        except requests.exceptions.Timeout:
            logger.warning("Timeout consultando SRI endpoint=%s", endpoint)
        except requests.exceptions.ProxyError as exc:
            logger.warning("Error de proxy al consultar SRI endpoint=%s error=%s", endpoint, exc)
        except requests.exceptions.SSLError as exc:
            logger.warning("Error SSL al consultar SRI endpoint=%s error=%s", endpoint, exc)
        except requests.exceptions.RequestException as exc:
            logger.warning("Error de red al consultar SRI endpoint=%s error=%s", endpoint, exc)

    return {
        "error": (
            "No fue posible consultar el SRI desde este servidor. "
            "Configura SRI_CONTRIBUYENTE_ENDPOINTS con un endpoint en Ecuador "
            "(proxy o relay) y verifica SRI_PROXY/SRI_TIMEOUT."
        )
    }

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

def consulta_contribuyente_sri_vps_externo(ruc):
    """Compatibilidad: usa la misma estrategia robusta para VPS externo."""
    return consulta_contribuyente_sri(ruc)
