import imaplib
import email
from email.header import decode_header
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from empresa.models import Empresa  # Ajusta a tu modelo real de Empresa
from solicitudes.servicios import procesar_adjuntos_xml_de_correo, encontrar_cliente_por_remitente  # Importa tus funciones

User = get_user_model()

class Command(BaseCommand):
    help = "Lee correos entrantes, busca facturas XML y crea las asignaciones en el sistema."

    def handle(self, *args, **options):
        # 1. Configuración de credenciales de correo (Idealmente desde variables de entorno)
        IMAP_SERVER = "imap.hostinger.com"  # O tu servidor IMAP (Gmail, Outlook, etc.)
        EMAIL_ACCOUNT = "facturas@tudominio.com"
        PASSWORD = "TuPasswordSegura"

        # Cargar usuario de sistema y empresa para asignar las operaciones en la BD
        user_sistema = User.objects.filter(is_superuser=True).first()
        empresa_default = Empresa.objects.first()

        if not user_sistema or not empresa_default:
            self.stderr.write("No se encontró usuario o empresa por defecto para asociar las facturas.")
            return

        try:
            # 2. Conexión al servidor IMAP
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            mail.select("INBOX")

            # Buscar solo correos no leídos
            status, messages = mail.search(None, 'UNSEEN')
            mail_ids = messages[0].split()

            if not mail_ids:
                self.stdout.write("No hay correos nuevos por procesar.")
                return

            self.stdout.write(f"Se encontraron {len(mail_ids)} correos nuevos.")

            for m_id in mail_ids:
                status, data = mail.fetch(m_id, '(RFC822)')
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Extraer Asunto y Remitente
                        asunto = self.decode_str(msg.get("Subject", ""))
                        sender = msg.get("From", "")

                        self.stdout.write(f"Procesando correo de: {sender} | Asunto: {asunto}")

                        # Extraer adjuntos
                        attachments = []
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_disposition = str(part.get("Content-Disposition"))
                                if "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        filename = self.decode_str(filename)
                                        content = part.get_payload(decode=True)
                                        attachments.append({'filename': filename, 'content': content})

                        if not attachments:
                            self.stdout.write("El correo no contiene archivos adjuntos.")
                            continue

                        # 3. Invocar tu función de procesamiento de XMLs
                        try:
                            resultados = procesar_adjuntos_xml_de_correo(
                                attachments=attachments,
                                sender_email=sender,
                                empresa=empresa_default,
                                user=user_sistema,
                                asunto=asunto
                            )

                            if resultados:
                                self.stdout.write(self.style.SUCCESS(
                                    f"Éxito: Se crearon {len(resultados)} asignaciones para {sender}."
                                ))
                                # Marcar correo como visto/leído
                                mail.store(m_id, '+FLAGS', '\\Seen')
                            else:
                                self.stdout.write("No se encontraron XMLs válidos o estructurados correctamente en los adjuntos.")

                        except ValueError as ve:
                            # Captura errores de negocio predefinidos (ej. "No se encontró cliente para el remitente")
                            self.stderr.write(f"Error de validación al procesar {sender}: {str(ve)}")
                            # Aquí puedes disparar una alerta a la IA o enviar un correo de notificación

            mail.close()
            mail.logout()

        except Exception as e:
            self.stderr.write(f"Ocurrió un error en el worker de correos: {str(e)}")

    def decode_str(self, header_value):
        """Decodifica encabezados de correo codificados en UTF-8 o ISO."""
        decoded_header = decode_header(header_value)
        header_text = ""
        for text, encoding in decoded_header:
            if isinstance(text, bytes):
                header_text += text.decode(encoding or 'utf-8', errors='ignore')
            else:
                header_text += str(text)
        return header_text