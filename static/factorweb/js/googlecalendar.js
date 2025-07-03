// Reemplaza con tus propias credenciales
const CLIENT_ID = '633238482960-utp39tr0solvvnkus5i8ve8bissaq67e.apps.googleusercontent.com'; // Tu ID de Cliente de Google Cloud
const API_KEY = 'AIzaSyAM4zQIIU_282vUm0DngU7e6Cd14uT_dQw';   // Tu Clave de API de Google Cloud

// Alcances (scopes) necesarios para acceder al calendario
const SCOPES = 'https://www.googleapis.com/auth/calendar.events';

let gapiInited = false;
let gisInited = false;
let tokenClient;

// Elementos HTML
const connectGoogleBtn = document.getElementById('googleSignIn');
const sendEventBtn = document.getElementById('createEvent');

// Carga la librería de Google API Client
function loadGapiClient() {
    gapi.load('client', initializeGapiClient);
}

// Inicializa el cliente de la API de Google
async function initializeGapiClient() {
    await gapi.client.init({
        apiKey: API_KEY,
        discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
    });
    gapiInited = true;
    maybeEnableButtons();
}

// Carga la librería de Google Identity Services
function loadGisClient() {
    tokenClient = google.accounts.oauth2.initTokenClient({
        client_id: CLIENT_ID,
        scope: SCOPES,
        callback: '', // Se establecerá dinámicamente
    });
    gisInited = true;
    maybeEnableButtons();
}

// Habilita los botones si ambas librerías están cargadas
function maybeEnableButtons() {
    if (gapiInited && gisInited) {
        connectGoogleBtn.disabled = false;
    }
}

// Función para conectar la cuenta de Google
async function connectGoogleAccount() {
    tokenClient.callback = async (resp) => {
        if (resp.error) {
            console.error('Error al iniciar sesión:', resp.error);
            return;
        }
        sendEventBtn.disabled = false; // Habilita el botón de enviar evento
        console.log('Cuenta de Google conectada exitosamente.');
    };
    if (gapi.client.getToken() === null) {
        // Pide consentimiento si no hay un token existente
        console.log('no hay token...');
        tokenClient.requestAccessToken({prompt: 'consent'});
    } else {
        // Si ya hay un token, intenta usarlo
        console.log('ya hay token...');
        tokenClient.requestAccessToken({prompt: ''});
    }
}

// Función para enviar el evento "Recordatorio de Cobranza"
async function sendEvent() {
    console.log('tokenClient.token', tokenClient.token);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowISO = tomorrow.toISOString().split('T')[0];

    const event = {
        'summary': 'Recordatorio de cobranza',
        'start': {
            'date': tomorrowISO,
            'timeZone': 'America/Guayaquil', // Zona horaria de Guayaquil, Ecuador
        },
        'end': {
            'date': tomorrowISO,
            'timeZone': 'America/Guayaquil',
        },
        'description': 'Recordatorio para contactar al cliente para la cobranza.',
    };

    try {
        const response = await gapi.client.calendar.events.insert({
            'calendarId': 'primary', // 'primary' se refiere al calendario principal del usuario
            'resource': event,
        });
        console.log('Evento creado:', response.result);
        alert('Evento "Recordatorio de cobranza" creado con éxito para mañana.');
    } catch (err) {
        console.error('Error al crear el evento:', err);
        alert('Hubo un error al crear el evento. Revisa la consola para más detalles.');
    }
}

// Asigna los event listeners
connectGoogleBtn.addEventListener('click', connectGoogleAccount);
sendEventBtn.addEventListener('click', sendEvent);

// Carga las librerías al iniciar
// Asegúrate de incluir los scripts de la API de Google en tu HTML:
// <script async defer src="https://apis.google.com/js/api.js" onload="loadGapiClient()"></script>
// <script async defer src="https://accounts.google.com/gsi/client" onload="loadGisClient()"></script>