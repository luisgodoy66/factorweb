# import zeep
from zeep import Client
from zeep.transports import Transport
from requests import Session

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

# Ejemplo de uso
if __name__ == "__main__":
    wsdl_url = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
    access_key = "2211202401099337376100120060010000123590001235917"  # Reemplazar con clave de acceso real

    service = SRIConsultationService(wsdl_url)
    result = service.consult_document_status(access_key)
    print(result)
