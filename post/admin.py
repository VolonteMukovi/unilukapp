from django.contrib import admin

from post.models import CategoriePost, Horaire, Publication


@admin.register(CategoriePost)
class CategoriePostAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug", "students_can_manage")
    prepopulated_fields = {"slug": ("nom",)}
    search_fields = ("nom", "slug")


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "author", "statut", "created_at")
    list_filter = ("statut", "categorie")
    search_fields = ("titre", "contenu")
    autocomplete_fields = ("author", "categorie")


@admin.register(Horaire)
class HoraireAdmin(admin.ModelAdmin):
    list_display = ("id", "filiere", "date_debut", "date_fin", "statut", "a_fichier")
    list_filter = ("statut", "filiere")
    search_fields = ("description",)

    @admin.display(description="Fichier", boolean=True)
    def a_fichier(self, obj):
        return bool(obj.fichier)
