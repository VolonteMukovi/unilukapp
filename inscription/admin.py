from django.contrib import admin

from inscription.models import AffectFiliere, Domaine, Filiere, Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("nom", "code", "created_at")
    search_fields = ("nom", "code")


@admin.register(Domaine)
class DomaineAdmin(admin.ModelAdmin):
    list_display = ("nom", "code", "institution")
    list_filter = ("institution",)
    search_fields = ("nom", "code")


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ("nom", "code", "domaine")
    list_filter = ("domaine",)
    search_fields = ("nom", "code")


@admin.register(AffectFiliere)
class AffectFiliereAdmin(admin.ModelAdmin):
    list_display = ("user", "filiere", "date_debut", "date_fin")
    list_filter = ("filiere",)
    autocomplete_fields = ("user", "filiere")
