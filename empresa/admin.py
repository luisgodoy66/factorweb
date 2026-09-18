from django.contrib import admin

from .models import Claves_webhook

# Register your models here.
@admin.register(Claves_webhook)
class ClavesWebhookAdmin(admin.ModelAdmin):
    list_display = ('ctnombre', 'ctprefijo', 'empresa', 'lactiva', 'dexpiracion', 'dultimouso')
    list_filter = ('empresa', 'lactiva')
    search_fields = ('ctnombre', 'ctprefijo')
    readonly_fields = ('ctprefijo', 'ctclavehash', 'dultimouso')
