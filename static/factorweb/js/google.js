// Cargar la API de Google
function loadGoogleAPI() {
  const script = document.createElement('script');
  script.src = 'https://apis.google.com/js/api.js';
  script.onload = () => {
    gapi.load('client:auth2', initClient);
  };
  document.body.appendChild(script);
}

// Inicializar el cliente
function initClient() {
  gapi.client.init({
    apiKey: 'AIzaSyAM4zQIIU_282vUm0DngU7e6Cd14uT_dQw',
    clientId: '633238482960-utp39tr0solvvnkus5i8ve8bissaq67e.apps.googleusercontent.com',
    discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
    scope: 'https://www.googleapis.com/auth/calendar.events'
  }).then(() => {
    // Aquí puedes manejar la autenticación
  });
}

// Autenticar al usuario
function handleAuthClick() {
  return gapi.auth2.getAuthInstance().signIn();
}

// Crear un evento
function createEvent() {
  const event = {
    'summary': 'Título del evento',
    'description': 'Descripción del evento',
    'start': {
      'dateTime': '2025-12-31T09:00:00-07:00',
      'timeZone': 'America/Los_Angeles'
    },
    'end': {
      'dateTime': '2025-12-31T17:00:00-07:00',
      'timeZone': 'America/Los_Angeles'
    }
  };

  gapi.client.calendar.events.insert({
    'calendarId': 'primary',
    'resource': event
  }).then(response => {
    console.log('Evento creado:', response.result.htmlLink);
  });
}