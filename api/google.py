# views.py
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development!
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # evita error 'Scope has changed' cuando Google agrega scopes ya otorgados antes
SCOPES = ['https://www.googleapis.com/auth/calendar.app.created']  # solo eventos creados por esta app
APP_CALENDAR_SUMMARY = 'Margarita - Recordatorios'

def google_login(request):
    if os.path.exists("client_secret.json"):
        print("🔑 Cargando credenciales desde client_secret.json...")
    else:
        print("❌ No se encontró client_secret.json. Asegúrate de tener el archivo correcto.")
        return HttpResponse('No se encontró client_secret.json. Asegúrate de tener el archivo correcto.', status=401)

    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_OAUTH2_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',  # fuerza a Google a emitir refresh_token en cada conexión
    )
    request.session['oauth_state'] = state
    request.session['oauth_scopes'] = SCOPES  # Guardar los scopes usados
    return redirect(authorization_url)

def oauth2callback(request):
    try:
        state = request.session['oauth_state']
        # Recuperar los scopes originales usados en la autorización
        original_scopes = request.session.get('oauth_scopes', SCOPES)
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=original_scopes,  # Usar los mismos scopes que en google_login
            redirect_uri=settings.GOOGLE_OAUTH2_REDIRECT_URI,
            state=state
        )
        flow.fetch_token(code=request.GET.get('code'))
        credentials = flow.credentials

        # Almacenar las credenciales serializadas en la sesión
        request.session['google_credentials'] = _credentials_to_session_dict(credentials)

        return HttpResponse('Conexión exitosa! Puede cerrar esta ventana.')
    except Exception as e:
        print(f"Error en oauth2callback: {e}")
        # Si el error es por cambio de scopes, limpiar la sesión y pedir al usuario que vuelva a conectar
        if "Scope has changed" in str(e):
            request.session.pop('oauth_state', None)
            request.session.pop('google_credentials', None)
            request.session.pop('oauth_scopes', None)
            return HttpResponse('Error: Los permisos (scopes) han cambiado. Por favor, vuelva a conectar su cuenta de Google.', status=400)
        return HttpResponse('Error al procesar la solicitud de OAuth2.', status=500)

def _credentials_to_session_dict(credentials):
    """Serializa las credenciales para guardarlas en la sesión (JSON-serializable)."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
    }

def _credentials_from_session_dict(data):
    """Reconstruye Credentials a partir de lo guardado en sesión, restaurando expiry."""
    data = dict(data)
    expiry = data.pop('expiry', None)
    creds = Credentials(**data)
    if expiry:
        creds.expiry = datetime.datetime.fromisoformat(expiry)
    return creds

def _get_or_create_app_calendar(service, request, forzar_nuevo=False):
    """Obtiene el ID del calendario secundario propio de la app, creándolo si aún no existe.

    Se persiste en BD (por usuario) porque calendar.app.created no autoriza
    calendarList().list(), así que no se puede recuperar buscando entre los calendarios.
    """
    from api.models import GoogleCalendarUsuario

    if not forzar_nuevo:
        registro = GoogleCalendarUsuario.objects.filter(user=request.user).first()
        if registro:
            request.session['google_calendar_id'] = registro.calendar_id
            return registro.calendar_id

    nuevo_calendario = {
        'summary': APP_CALENDAR_SUMMARY,
        'timeZone': 'America/Guayaquil',
    }
    creado = service.calendars().insert(body=nuevo_calendario).execute()
    calendar_id = creado['id']
    GoogleCalendarUsuario.objects.update_or_create(
        user=request.user, defaults={'calendar_id': calendar_id}
    )
    request.session['google_calendar_id'] = calendar_id
    return calendar_id

@login_required(login_url='/login/')
def crear_evento_recordatorio_cobranza(request, cliente):
    # por GET mostrar el modal para ingresar datos del evento
    if request.method != 'POST':
        contexto = {
            'cliente': cliente,
        }
        return render(request, 'operaciones/datoseventocalendario_modal.html', contexto)

    # Suponiendo que ya tienes las credenciales OAuth2 en la sesión (ajusta según tu flujo)
    credentials = request.session.get('google_credentials')
    if not credentials:
        return HttpResponse('No hay credenciales de Google disponibles. Conecte a una cuenta desde el menú de usuario'
                            , status=401)

    try:
        creds = _credentials_from_session_dict(credentials)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            request.session['google_credentials'] = _credentials_to_session_dict(creds)
        if not creds.valid:
            # Token vencido y sin refresh_token disponible: no hay forma de renovarlo automáticamente.
            request.session.pop('google_credentials', None)
            return HttpResponse('Su conexión con Google expiró. Por favor, vuelva a conectar su cuenta de Google.', status=401)
        service = build('calendar', 'v3', credentials=creds)

    except Exception as e:
        print(f"Error al procesar las credenciales: {e}")
        return HttpResponse('Error al procesar las credenciales de Google.', status=500)

    # Grabar el evento en el calendario
    descripcion = request.POST.get('motivo', 'Recordatorio de cobranza')
    fecha = request.POST.get('fecha', None)
    if fecha:
        # Si la fecha viene del formulario, parsearla y asignar zona horaria de Quito
        try:
            # fecha formato: "YYYY-MM-DD HH:MM"
            naive_dt = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M")
            # Asignar zona horaria de Quito (America/Guayaquil)
            import pytz
            quito_tz = pytz.timezone('America/Guayaquil')
            fecha_evento = quito_tz.localize(naive_dt)
        except ValueError:
            return HttpResponse('Formato de fecha inválido.', status=400)
    else:
        # Si no hay fecha, usar mañana por defecto a las 9:00 en Quito
        import pytz
        quito_tz = pytz.timezone('America/Guayaquil')
        tomorrow = datetime.datetime.now(quito_tz) + datetime.timedelta(days=1)
        fecha_evento = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)

    start = fecha_evento
    end = start + datetime.timedelta(hours=1)
    event = {
        'summary': cliente,
        'description': descripcion,
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'America/Guayaquil',
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'America/Guayaquil',
        },
    }

    try:
        # Insertar el evento en el calendario propio de la app (requerido por el scope calendar.app.created)
        calendar_id = _get_or_create_app_calendar(service, request)
        try:
            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        except HttpError as e:
            if e.resp.status == 404:
                # El calendario guardado ya no existe (borrado o de una cuenta de Google distinta): recrear y reintentar
                calendar_id = _get_or_create_app_calendar(service, request, forzar_nuevo=True)
                created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            else:
                raise
    except Exception as e:
        return HttpResponse(f"Error al crear el evento: {e}", status=500)
    
    return HttpResponse("OK")  # Return a simple response for now
        
def google_session_active(request):
    """
    Retorna un JSON con el elemento 'active' indicando si hay una sesión de Google activa
    y con permisos (scopes) vigentes.
    """
    credentials = request.session.get('google_credentials')
    active = False
    reconnect_required = False
    if credentials:
        # include_granted_scopes puede sumar scopes ya otorgados antes; basta con que
        # los scopes requeridos actuales estén incluidos, no que coincidan exactamente.
        scopes_otorgados = set(credentials.get('scopes') or [])
        if not set(SCOPES).issubset(scopes_otorgados):
            request.session.pop('google_credentials', None)
            request.session.pop('google_calendar_id', None)
            reconnect_required = True
        else:
            creds = _credentials_from_session_dict(credentials)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                request.session['google_credentials'] = _credentials_to_session_dict(creds)
            if creds.valid:
                active = True
            elif creds.expired and not creds.refresh_token:
                request.session.pop('google_credentials', None)
                request.session.pop('google_calendar_id', None)
                reconnect_required = True
    return JsonResponse({'active': active, 'reconnect_required': reconnect_required})
