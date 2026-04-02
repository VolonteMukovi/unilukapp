from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from post.validators import validate_horaire_fichier


class CategoriePost(models.Model):
    nom = models.CharField(_("nom"), max_length=128, unique=True)
    slug = models.SlugField(_("slug"), max_length=140, unique=True)
    description = models.TextField(_("description"), blank=True)
    students_can_manage = models.BooleanField(
        _("étudiants peuvent gérer leurs publications"),
        default=False,
        help_text=_(
            "Si activé, un étudiant auteur peut créer / modifier / supprimer "
            "ses publications dans cette catégorie (ex. recherches scientifiques)."
        ),
    )

    class Meta:
        verbose_name = _("catégorie de publication")
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class PublicationStatut(models.TextChoices):
    ACTIF = "actif", _("Actif")
    ARCHIVE = "archive", _("Archivé")


class Publication(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="publications",
    )
    categorie = models.ForeignKey(
        CategoriePost,
        on_delete=models.PROTECT,
        related_name="publications",
    )
    titre = models.CharField(_("titre"), max_length=255)
    contenu = models.TextField(_("contenu"))
    statut = models.CharField(
        max_length=20,
        choices=PublicationStatut.choices,
        default=PublicationStatut.ACTIF,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("publication")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "statut"]),
        ]

    def __str__(self):
        return self.titre


class HoraireStatut(models.TextChoices):
    ACTIF = "actif", _("Actif")
    EXPIRE = "expire", _("Expiré")


class HoraireQuerySet(models.QuerySet):
    def sync_expired(self):
        today = timezone.now().date()
        return self.filter(
            date_fin__lt=today,
            statut=HoraireStatut.ACTIF,
        ).update(statut=HoraireStatut.EXPIRE)


class Horaire(models.Model):
    filiere = models.ForeignKey(
        "inscription.Filiere",
        on_delete=models.CASCADE,
        related_name="horaires",
    )
    description = models.TextField(_("description"), blank=True)
    fichier = models.FileField(
        _("fichier horaire (PDF ou image)"),
        upload_to="horaires/%Y/%m/",
        max_length=512,
        blank=True,
        null=True,
    )
    date_debut = models.DateField(_("date de début"))
    date_fin = models.DateField(_("date de fin"))
    statut = models.CharField(
        max_length=20,
        choices=HoraireStatut.choices,
        default=HoraireStatut.ACTIF,
        db_index=True,
    )

    objects = HoraireQuerySet.as_manager()

    class Meta:
        verbose_name = _("horaire")
        ordering = ["date_debut", "filiere"]
        indexes = [
            models.Index(fields=["filiere", "date_debut", "date_fin"]),
        ]

    def __str__(self):
        if self.fichier:
            return f"{self.fichier.name.split('/')[-1]} ({self.filiere})"
        return f"Horaire #{self.pk or 'nouveau'} ({self.filiere})"

    def clean(self):
        super().clean()
        if self.fichier:
            validate_horaire_fichier(self.fichier)

    def save(self, *args, **kwargs):
        today = timezone.now().date()
        if self.date_fin < today and self.statut == HoraireStatut.ACTIF:
            self.statut = HoraireStatut.EXPIRE
        super().save(*args, **kwargs)
