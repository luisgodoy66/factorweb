# views.py
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development!
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # evita error 'Scope has changed' cuando Google agrega scopes ya otorgados antes
SCOPES = ['https://www.googleapis.com/auth/calendar.app.created']  # solo eventos creados por esta app
APP_CALENDAR_SUMMARY = 'Factorweb - Recordatorios de Cobranza'

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
        # prompt='consent'  # <-- AÑADIR ESTA LÍNEA
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
        request.session['google_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }

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

def _get_or_create_app_calendar(service, request):
    """Obtiene el ID del calendario secundario propio de la app, creándolo si aún no existe."""
    calendar_id = request.session.get('google_calendar_id')
    if calendar_id:
        return calendar_id

    # calendar.app.created solo expone calendarios creados por esta app, así que
    # cualquier resultado aquí ya pertenece a la aplicación.
    calendar_list = service.calendarList().list().execute()
    for entry in calendar_list.get('items', []):
        if entry.get('summary') == APP_CALENDAR_SUMMARY:
            calendar_id = entry['id']
            request.session['google_calendar_id'] = calendar_id
            return calendar_id

    nuevo_calendario = {
        'summary': APP_CALENDAR_SUMMARY,
        'timeZone': 'America/Guayaquil',
    }
    creado = service.calendars().insert(body=nuevo_calendario).execute()
    calendar_id = creado['id']
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
        # Verificar si las credenciales son válidas
        creds = Credentials(**credentials)
        if not creds.valid:
            return HttpResponse('Credenciales de Google no válidas.', status=401)
        # if creds.expired and creds.refresh_token:
        #     creds.refresh(Request())
        #     # Actualizar las credenciales en la sesión
        #     request.session['google_credentials'] = {
        #         'token': creds.token,
        #         'refresh_token': creds.refresh_token,
        #         'token_uri': creds.token_uri,
        #         'client_id': creds.client_id,
        #         'client_secret': creds.client_secret,
        #         'scopes': creds.scopes,
        #     }
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
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
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
            creds = Credentials(**credentials)
            if creds.valid:
                active = True
    return JsonResponse({'active': active, 'reconnect_required': reconnect_required})
