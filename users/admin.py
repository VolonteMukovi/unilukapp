from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from inscription.models import AffectFiliere
from users.models import User


class AffectFiliereInline(admin.TabularInline):
    model = AffectFiliere
    extra = 0
    autocomplete_fields = ("filiere",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    inlines = (AffectFiliereInline,)
    list_display = (
        "email",
        "matricule",
        "num_tel",
        "first_name",
        "troisieme_nom",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "role")
    search_fields = (
        "email",
        "matricule",
        "num_tel",
        "first_name",
        "troisieme_nom",
        "last_name",
    )
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Profil",
            {
                "fields": (
                    "first_name",
                    "troisieme_nom",
                    "last_name",
                    "photo_profil",
                    "matricule",
                    "num_tel",
                    "role",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "matricule",
                    "num_tel",
                    "first_name",
                    "troisieme_nom",
                    "last_name",
                    "photo_profil",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
