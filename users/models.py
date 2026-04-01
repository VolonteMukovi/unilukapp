from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("L’adresse e-mail est obligatoire."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser doit avoir is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser doit avoir is_superuser=True."))
        return self._create_user(email, password, **extra_fields)


class UserRole(models.TextChoices):
    ADMIN = "admin", _("Admin (secrétariat principal)")
    SECRETAIRE = "secretaire", _("Secrétaire")
    ETUDIANT = "etudiant", _("Étudiant")


class User(AbstractUser):
    username = None
    objects = UserManager()

    email = models.EmailField(_("adresse e-mail"), unique=True, db_index=True)
    matricule = models.CharField(_("matricule"), max_length=64, unique=True, db_index=True)
    num_tel = models.CharField(_("numéro de téléphone"), max_length=32, unique=True, db_index=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.ETUDIANT,
        db_index=True,
    )
    troisieme_nom = models.CharField(_("troisième nom"), max_length=150, blank=True)
    photo_profil = models.ImageField(
        _("photo de profil"),
        upload_to="profils/%Y/%m/",
        blank=True,
        null=True,
    )
    filieres = models.ManyToManyField(
        "inscription.Filiere",
        through="inscription.AffectFiliere",
        related_name="utilisateurs",
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["matricule", "num_tel", "first_name", "last_name"]

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")
        ordering = ["-date_joined"]

    def get_full_name(self):
        parts = [self.first_name or "", self.troisieme_nom or "", self.last_name or ""]
        name = " ".join(p for p in parts if p).strip()
        return name

    def save(self, *args, **kwargs):
        if self.num_tel:
            from users.phone_utils import parse_phone_to_e164

            normalized = parse_phone_to_e164(self.num_tel)
            if normalized:
                self.num_tel = normalized
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.matricule})"
