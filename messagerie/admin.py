from django.contrib import admin

from messagerie.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "expediteur", "destinataire", "sujet", "lu", "created_at")
    list_filter = ("lu",)
    search_fields = ("sujet", "corps")
    autocomplete_fields = ("expediteur", "destinataire", "parent")
