# import zeep
from zeep import Client
from zeep.transports import Transport
from requests import Session
from django.http import HttpResponse, JsonResponse

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
                    # "comprobante": autorizacion.comprobante,
                } for autorizacion in autorizaciones.autorizacion]
        return {"mensaje": "No se encontraron autorizaciones."}

# # Ejemplo de uso
# if __name__ == "__main__":
#     wsdl_url = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
#     access_key = "0701202501179143070000120010020000060524117597515"  # Reemplazar con clave de acceso real

#     service = SRIConsultationService(wsdl_url)
#     result = service.consult_document_status(access_key)
#     print(result)

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


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de uso
    ruc = "0993220167001"  # Reemplaza con el RUC que deseas consultar
    datos = obtener_datos_contribuyente(None,ruc)

    # Imprimir los datos obtenidos
    print(datos)
    datos = [{'numeroRuc': '0993220167001'
              , 'razonSocial': 'CODIGO BAMBÚ COBAMBUSA S.A.'
              , 'estadoContribuyenteRuc': 'ACTIVO'
              , 'actividadEconomicaPrincipal': 'VENTA AL POR MAYOR DE ARTÍCULOS DE LIMPIEZA.'
              , 'tipoContribuyente': 'SOCIEDAD'
              , 'regimen': 'GENERAL', 'categoria': None, 'obligadoLlevarContabilidad': 'SI', 'agenteRetencion': 'NO'
              , 'contribuyenteEspecial': 'NO'
              , 'informacionFechasContribuyente': {'fechaInicioActividades': '2019-08-21 00:00:00.0', 'fechaCese': ''
                                                   , 'fechaReinicioActividades': '', 'fechaActualizacion': '2019-08-22 18:37:25.0'}
              , 'representantesLegales': [{'identificacion': '0910487388', 'nombre': 'GODOY CHOCA LUIS ANTONIO'}]
              , 'motivoCancelacionSuspension': None, 'contribuyenteFantasma': 'NO', 'transaccionesInexistente': 'NO'}
              ]