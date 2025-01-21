from zeep import Client
from zeep.transports import Transport
from requests import Session
import os

class SRIService:
    def __init__(self, recepcion_wsdl, autorizacion_wsdl, download_folder, cert_path):
        self.recepcion_wsdl = recepcion_wsdl
        self.autorizacion_wsdl = autorizacion_wsdl
        self.download_folder = download_folder
        self.cert_path = cert_path
        self.recepcion_client = self._initialize_client(self.recepcion_wsdl)
        self.autorizacion_client = self._initialize_client(self.autorizacion_wsdl)

    def _initialize_client(self, wsdl_url):
        try:
            session = Session()
            session.verify = self.cert_path  # Usar el certificado raíz para la verificación SSL
            transport = Transport(session=session)
            
            # Verificar si la URL del WSDL es accesible y devuelve un XML válido
            response = session.get(wsdl_url)
            print("Client initialized 1")
            response.raise_for_status()  # Lanza una excepción si la respuesta HTTP es un error
            print("Client initialized 2")
            if not response.headers['Content-Type'].startswith('text/xml'):
                raise ValueError(f"Contenido no válido recibido desde {wsdl_url}: {response.text[:200]}")
            return Client(wsdl=wsdl_url, transport=transport)
        except Exception as e:
            print(f"Error al inicializar el cliente para {wsdl_url}: {e}")
            return None
        
    def send_document(self, xml_file_path):
        try:
            with open(xml_file_path, 'rb') as xml_file:
                xml_content = xml_file.read()
            response = self.recepcion_client.service.validarComprobante(xml_content)
            return self._parse_recepcion_response(response)
        except Exception as e:
            return {"error": str(e)}

    def _parse_recepcion_response(self, response):
        if response.estado == "RECIBIDA":
            return {"estado": response.estado, "mensajes": []}
        else:
            mensajes = [
                {
                    "identificador": mensaje.identificador,
                    "mensaje": mensaje.mensaje,
                    "informacionAdicional": getattr(mensaje, 'informacionAdicional', None),
                    "tipo": mensaje.tipo,
                }
                for mensaje in response.comprobantes.comprobante[0].mensajes.mensaje
            ]
            return {"estado": response.estado, "mensajes": mensajes}

    def consult_authorization(self, access_key):
        try:
            response = self.autorizacion_client.service.autorizacionComprobante(access_key)
            return self._parse_autorizacion_response(response)
        except Exception as e:
            return {"error": str(e)}

    def _parse_autorizacion_response(self, response):
        if hasattr(response, 'autorizaciones'):
            autorizaciones = response.autorizaciones
            if autorizaciones and hasattr(autorizaciones, 'autorizacion'):
                result = []
                for autorizacion in autorizaciones.autorizacion:
                    estado = autorizacion.estado
                    numero_autorizacion = getattr(autorizacion, 'numeroAutorizacion', None)
                    fecha_autorizacion = getattr(autorizacion, 'fechaAutorizacion', None)
                    ambiente = getattr(autorizacion, 'ambiente', None)

                    if estado == "AUTORIZADO":
                        comprobante = autorizacion.comprobante
                        self._save_authorized_xml(access_key, comprobante)

                    result.append({
                        "estado": estado,
                        "numeroAutorizacion": numero_autorizacion,
                        "fechaAutorizacion": fecha_autorizacion,
                        "ambiente": ambiente,
                        "mensajes": [
                            {
                                "identificador": mensaje.identificador,
                                "mensaje": mensaje.mensaje,
                                "informacionAdicional": getattr(mensaje, 'informacionAdicional', None),
                                "tipo": mensaje.tipo,
                            }
                            for mensaje in getattr(autorizacion, 'mensajes', {}).mensaje or []
                        ],
                    })
                return result
        return {"mensaje": "No se encontraron autorizaciones o respuesta inválida."}

    def _save_authorized_xml(self, access_key, xml_content):
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        file_path = os.path.join(self.download_folder, f"{access_key}.xml")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(xml_content)

# Ejemplo de uso
if __name__ == "__main__":
    recepcion_wsdl = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl"
    autorizacion_wsdl = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl"
    download_folder = "./autorizados"
    cert_path = "E:/Django/factorweb25env/certificadosri/cel.sri.gob.ec.crt"  # Reemplazar con la ruta al certificado raíz

    service = SRIService(recepcion_wsdl, autorizacion_wsdl, download_folder, cert_path)

    xml_file_path = "E:/Codigo bambu/Facturacion electronica/FIRMADOS/2001202501099322016700120010010000001890000018917.xml"  # Reemplazar con la ruta del archivo XML
    send_result = service.send_document(xml_file_path)
    print("Resultado del envío:", send_result)

    if send_result.get("estado") == "RECIBIDA":
        access_key = "2001202501099322016700120010010000001890000018917"  # Reemplazar con la clave de acceso real
        auth_result = service.consult_authorization(access_key)
        print("Resultado de la autorización:", auth_result)

        for auth in auth_result:
            if auth["estado"] == "AUTORIZADO":
                print("Documento autorizado y guardado.")
            else:
                print("Mensajes de error:", auth["mensajes"])