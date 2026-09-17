from django.db import models
from django.contrib.auth.models import User
from bases.models import ClaseModelo

# Create your models here.
class GoogleCalendarUsuario(models.Model):
    """Persiste el calendario secundario que la app crea en Google Calendar para cada usuario."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_calendar')
    calendar_id = models.CharField(max_length=255)
    dcreacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -> {self.calendar_id}"

class Configuracion_slack (ClaseModelo):
    ctdescripcion = models.CharField(max_length=100)
    ctslackbottoken = models.CharField(max_length=100)
    ctslackchannelname = models.CharField(max_length=50)
    ctslacksigningsecret = models.CharField(max_length=100)
    lactivo = models.BooleanField(default=True)
    ctappid = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.ctdescripcion

    # def save(self):
    #     self.ctdescripcion = self.ctdescripcion.upper()

class Configuracion_twilio_whatsapp(ClaseModelo):
    ctdescripcion = models.CharField(max_length=100)
    ctaccountsid = models.CharField(max_length=100)
    ctauthtoken = models.CharField(max_length=100)
    ctwhatsappnumber = models.CharField(max_length=20)
    lactivo = models.BooleanField(default=True)

    def __str__(self):
        return self.ctdescripcion

    # def save(self):
    #     self.ctdescripcion = self.ctdescripcion.upper()

class InvoiceAIAnalysis(ClaseModelo):
    RISK_CHOICES = (
        ('BAJO', 'Bajo'),
        ('MEDIO', 'Medio'),
        ('ALTO', 'Alto'),
    )

    invoice = models.OneToOneField(
        'solicitudes.Documentos',
        on_delete=models.CASCADE,
        related_name='ai_analysis'
    )
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)
    analysis_text = models.TextField()
    recommendation = models.TextField()
    raw_response = models.JSONField(null=True, blank=True)

