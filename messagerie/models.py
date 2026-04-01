from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Message(models.Model):
    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_envoyes",
    )
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_recus",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reponses",
    )
    sujet = models.CharField(_("sujet"), max_length=255, blank=True)
    corps = models.TextField(_("corps"))
    lu = models.BooleanField(_("lu"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("message")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["expediteur", "destinataire", "created_at"]),
        ]

    def __str__(self):
        return self.sujet or f"Message #{self.pk}"
