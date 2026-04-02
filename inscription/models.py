from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Institution(models.Model):
    # max_length 191 : limite index utf8mb4 sous MySQL/MariaDB (WAMP, etc.) — ~764 octets
    nom = models.CharField(_("nom"), max_length=191, unique=True)
    code = models.CharField(_("code"), max_length=32, unique=True, blank=True, null=True)
    adresse = models.TextField(_("adresse"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("institution")
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Domaine(models.Model):
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="domaines",
    )
    nom = models.CharField(_("nom"), max_length=191)
    code = models.CharField(_("code"), max_length=32, blank=True)

    class Meta:
        verbose_name = _("domaine")
        ordering = ["institution", "nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "nom"],
                name="uniq_inscription_domaine_institution_nom",
            ),
        ]

    def __str__(self):
        return f"{self.nom} ({self.institution})"


class Filiere(models.Model):
    domaine = models.ForeignKey(
        Domaine,
        on_delete=models.CASCADE,
        related_name="filieres",
    )
    nom = models.CharField(_("nom"), max_length=191)
    code = models.CharField(_("code"), max_length=32, blank=True)

    class Meta:
        verbose_name = _("filière")
        verbose_name_plural = _("filières")
        ordering = ["domaine", "nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["domaine", "nom"],
                name="uniq_inscription_filiere_domaine_nom",
            ),
        ]

    def __str__(self):
        return f"{self.nom} ({self.domaine})"


class AffectFiliere(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="affectations_filiere",
    )
    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name="affectations",
    )
    date_debut = models.DateField(_("date de début"), null=True, blank=True)
    date_fin = models.DateField(_("date de fin"), null=True, blank=True)

    class Meta:
        verbose_name = _("affectation filière")
        verbose_name_plural = _("affectations filière")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "filiere"],
                name="uniq_affect_user_filiere",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} → {self.filiere_id}"
