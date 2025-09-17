# from zeep import Client
# from zeep.transports import Transport
# from requests import Session
# import os

# class SRIService:
#     def __init__(self, recepcion_wsdl, autorizacion_wsdl, download_folder, cert_path):
#         self.recepcion_wsdl = recepcion_wsdl
#         self.autorizacion_wsdl = autorizacion_wsdl
#         self.download_folder = download_folder
#         self.cert_path = cert_path
#         self.recepcion_client = self._initialize_client(self.recepcion_wsdl)
#         self.autorizacion_client = self._initialize_client(self.autorizacion_wsdl)

#     def _initialize_client(self, wsdl_url):
#         try:
#             session = Session()
#             # Usar el certificado raíz para la verificación SSL si es necesario
#             if os.path.exists(self.cert_path):
#                 print(f"Usando certificado para verificación SSL: {self.cert_path}")
#             else:
#                 print(f"No se encontró el certificado en: {self.cert_path}. Usando verificación por defecto.")
#             if self.cert_path and os.path.exists(self.cert_path):
#                 session.verify = self.cert_path
            
#             transport = Transport(session=session)
#             client = Client(wsdl=wsdl_url, transport=transport)
#             print(f"Cliente Zeep inicializado para {wsdl_url}")
#             return client
#         except Exception as e:
#             print(f"Error al inicializar el cliente para {wsdl_url}: {e}")
#             return None
        
#     def send_document(self, xml_file_path):
#         try:
#             with open(xml_file_path, 'rb') as xml_file:
#                 xml_content = xml_file.read()
#             response = self.recepcion_client.service.validarComprobante(xml_content)
#             return self._parse_recepcion_response(response)
#         except Exception as e:
#             return {"error": str(e)}

#     def _parse_recepcion_response(self, response):
#         if response.estado == "RECIBIDA":
#             return {"estado": response.estado, "mensajes": []}
#         else:
#             mensajes = [
#                 {
#                     "identificador": mensaje.identificador,
#                     "mensaje": mensaje.mensaje,
#                     "informacionAdicional": getattr(mensaje, 'informacionAdicional', None),
#                     "tipo": mensaje.tipo,
#                 }
#                 for mensaje in response.comprobantes.comprobante[0].mensajes.mensaje
#             ]
#             return {"estado": response.estado, "mensajes": mensajes}

#     def consult_authorization(self, access_key):
#         try:
#             # Usar el nombre de parámetro correcto: claveAccesoComprobante
#             response = self.autorizacion_client.service.autorizacionComprobante(claveAccesoComprobante=access_key)
#             return self._parse_autorizacion_response(response, access_key)
#         except Exception as e:
#             return {"error": str(e)}

#     def _parse_autorizacion_response(self, response, access_key):
#         # La respuesta del SRI puede no tener autorizaciones si no se encuentra el comprobante.
#         if not response or not hasattr(response, 'autorizaciones') or not response.autorizaciones:
#             return {"estado": "NO ENCONTRADO", "mensajes": "No se encontró información para la clave de acceso."}

#         autorizacion_data = response.autorizaciones.autorizacion[0]
#         estado = autorizacion_data.estado
        
#         result = {
#             "estado": estado,
#             "numeroAutorizacion": getattr(autorizacion_data, 'numeroAutorizacion', None),
#             "fechaAutorizacion": getattr(autorizacion_data, 'fechaAutorizacion', None),
#             "ambiente": getattr(autorizacion_data, 'ambiente', None),
#             "mensajes": []
#         }

#         if estado == "AUTORIZADO":
#             comprobante_xml = getattr(autorizacion_data, 'comprobante', None)
#             if comprobante_xml:
#                 self._save_authorized_xml(access_key, comprobante_xml)
        
#         # Parsear mensajes si existen
#         if hasattr(autorizacion_data, 'mensajes') and autorizacion_data.mensajes:
#             for mensaje in autorizacion_data.mensajes.mensaje:
#                 result["mensajes"].append({
#                     "identificador": mensaje.identificador,
#                     "mensaje": mensaje.mensaje,
#                     "informacionAdicional": getattr(mensaje, 'informacionAdicional', None),
#                     "tipo": mensaje.tipo,
#                 })
        
#         return result

#     def _save_authorized_xml(self, access_key, xml_content):
#         if not os.path.exists(self.download_folder):
#             os.makedirs(self.download_folder)
#         file_path = os.path.join(self.download_folder, f"{access_key}.xml")
#         with open(file_path, "w", encoding="utf-8") as file:
#             file.write(xml_content)

# # Ejemplo de uso
# if __name__ == "__main__":
#     recepcion_wsdl = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
#     autorizacion_wsdl = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
#     download_folder = "./autorizados"
#     cert_path = "E:/Django/margaritaenv/factorweb/cel.sri.gob.ec.crt"  # Reemplazar con la ruta al certificado raíz

#     service = SRIService(recepcion_wsdl, autorizacion_wsdl, download_folder, cert_path)

#     # xml_file_path = "E:/Codigo bambu/Facturacion electronica/FIRMADOS/2001202501099322016700120010010000001890000018917.xml"  # Reemplazar con la ruta del archivo XML
#     # send_result = service.send_document(xml_file_path)
#     # print("Resultado del envío:", send_result)

#     # if send_result.get("estado") == "RECIBIDA":
#     access_key = "0107202501098765432100120010010000010060000100610"  # Reemplazar con la clave de acceso real
#     auth_result = service.consult_authorization(access_key)
#     print("Resultado de la autorización:", auth_result)

#     if auth_result and auth_result.get("estado") == "AUTORIZADO":
#         print("Documento autorizado y guardado.")
#     elif auth_result:
#         print("El documento no está autorizado. Estado:", auth_result.get("estado"))
#         if auth_result.get("mensajes"):
#             print("Mensajes de error:", auth_result["mensajes"])
# # from zeep import Client

# # # URL del WSDL del servicio de autorización en el ambiente de pruebas
# # wsdl_url = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'

# # # Crear un cliente SOAP
# # client = Client(wsdl=wsdl_url)

# # # Clave de acceso de la factura electrónica que deseas consultar
# # clave_acceso = '2911202401099037901700120010050498822290990379011'

# # # Llamar al método del servicio web para obtener la autorización
# # response = client.service.autorizacionComprobante(claveAccesoComprobante=clave_acceso)

# # # Procesar la respuesta
# # print(f"Estado: {response}")
# # if response.numeroComprobantes == '0':
# #     print('No se encontró información para la clave de acceso proporcionada.')
# # else:
# #     for autorizacion in response.autorizaciones.autorizacion:
# #         print(f"Estado: {autorizacion.estado}")
# #         if autorizacion.estado == 'AUTORIZADO':
# #             print(f"Fecha de Autorización: {autorizacion.fechaAutorizacion}")
# #             print(f"Ambiente: {autorizacion.ambiente}")
# #             print(f"Comprobante: {autorizacion.comprobante}")
# #         else:
# #             print("Mensajes de error:")
# #             for mensaje in autorizacion.mensajes.mensaje:
# #                 print(f"Identificador: {mensaje.identificador}")
# #                 print(f"Mensaje: {mensaje.mensaje}")
# #                 print(f"Información Adicional: {mensaje.informacionAdicional}")
# #                 print(f"Tipo: {mensaje.tipo}")

from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth

# URL del WSDL del ambiente de producción
wsdl_url = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'

# Crear cliente SOAP
client = Client(wsdl=wsdl_url)

# Clave de acceso del comprobante (49 dígitos)
clave_acceso = '1107202501099210689100121640510000387271234567819'

# Invocar el método de autorización
response = client.service.autorizacionComprobante(claveAccesoComprobante=clave_acceso)
print(response)
# Mostrar resultados
for autorizacion in response.autorizaciones.autorizacion:
    print("Estado:", autorizacion.estado)
    print("Número de Autorización:", autorizacion.numeroAutorizacion)
    print("Fecha de Autorización:", autorizacion.fechaAutorizacion)
    print("Ambiente:", autorizacion.ambiente)
    print("Comprobante XML:")
    print(autorizacion.comprobante)
