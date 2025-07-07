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

def google_login(request):
    if os.path.exists("client_secret.json"):
        print("🔑 Cargando credenciales desde client_secret.json...")
    else:
        print("❌ No se encontró client_secret.json. Asegúrate de tener el archivo correcto.")
        return HttpResponse('No se encontró client_secret.json. Asegúrate de tener el archivo correcto.', status=401)

    flow = Flow.from_client_secrets_file(
        'client_secret.json',  # Replace with the actual path to your client_secret.json file
        scopes=['https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar'],  # Adjust scopes as needed
        redirect_uri=settings.GOOGLE_OAUTH2_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)

def oauth2callback(request):
    state = request.session['oauth_state']
    flow = Flow.from_client_secrets_file(
        'client_secret.json',  # Replace with the actual path to your client_secret.json file
        scopes=['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar'],
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

    # crear_evento_recordatorio_cobranza(request)  # Call the function to create the event
    return HttpResponse('Conexión exitosa! Puede cerrar esta ventana.')

@login_required(login_url='/login/')
def crear_evento_recordatorio_cobranza(request, cliente):
    # por GET mostrar el modal para ingresar datos del evento
    print(request.method, request.GET)
    if request.method != 'POST':
        contexto = {
            'cliente': cliente,
        }
        return render(request, 'operaciones/datoseventocalendario_modal.html', contexto)

    # Suponiendo que ya tienes las credenciales OAuth2 en la sesión (ajusta según tu flujo)
    credentials = request.session.get('google_credentials')
    if not credentials:
        return HttpResponse('No hay credenciales de Google disponibles.', status=401)

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
        # Insertar el evento en el calendario
        if 'google_calendar_id' in request.session:
            calendar_id = request.session['google_calendar_id']
        else:
            calendar_id = 'primary'
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    except Exception as e:
        return HttpResponse(f"Error al crear el evento: {e}", status=500)
    
    return HttpResponse("OK")  # Return a simple response for now
        
def google_session_active(request):
    """
    Retorna un JSON con el elemento 'active' indicando si hay una sesión de Google activa.
    """
    credentials = request.session.get('google_credentials')
    active = False
    if credentials:
        creds = Credentials(**credentials)
        if creds.valid:
            active = True
    return JsonResponse({'active': active})
