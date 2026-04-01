"""
Schéma OpenAPI : regroupement par table métier (CRUD) et ordre des tags Swagger/Redoc.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

# Ordre d’affichage des sections (une section = une table / domaine fonctionnel)
TAG_ORDER = [
    "Authentification",
    "User",
    "Institution",
    "Domaine",
    "Filière",
    "AffectFiliere",
    "CategoriePost",
    "Publication",
    "Horaire",
    "Message",
]

TAG_DESCRIPTIONS = {
    "Authentification": "Jetons JWT (connexion, refresh). Pas une table SQL.",
    "User": "Table `users_user` - CRUD + profil connecté (`/users/me/`).",
    "Institution": "Table `inscription_institution` - CRUD.",
    "Domaine": "Table `inscription_domaine` - CRUD.",
    "Filière": "Table `inscription_filiere` - CRUD.",
    "AffectFiliere": "Table `inscription_affectfiliere` - liaison utilisateur / filière - CRUD.",
    "CategoriePost": "Table `post_categoriepost` - CRUD.",
    "Publication": "Table `post_publication` - CRUD.",
    "Horaire": "Table `post_horaire` - CRUD.",
    "Message": "Table `messagerie_message` - lecture, envoi, marquer lu.",
}


def crud_table(tag: str, **extra):
    """
    Regroupe dans la doc OpenAPI toutes les opérations standard du ViewSet
    sous un même tag (= nom de table métier), avec résumés explicites CRUD.
    """
    kwargs = {
        "list": extend_schema(tags=[tag], summary=f"Liste - {tag}"),
        "retrieve": extend_schema(tags=[tag], summary=f"Lecture (détail) - {tag}"),
        "create": extend_schema(tags=[tag], summary=f"Création - {tag}"),
        "update": extend_schema(tags=[tag], summary=f"Mise à jour complète (PUT) - {tag}"),
        "partial_update": extend_schema(tags=[tag], summary=f"Mise à jour partielle (PATCH) - {tag}"),
        "destroy": extend_schema(tags=[tag], summary=f"Suppression - {tag}"),
    }
    kwargs.update(extra)
    return extend_schema_view(**kwargs)


def reorder_tags_hook(result, generator, request, public):
    """Réordonne les tags dans Swagger/Redoc selon TAG_ORDER."""
    tags = list(result.get("tags") or [])
    rank = {name: i for i, name in enumerate(TAG_ORDER)}
    tags.sort(key=lambda t: rank.get(t.get("name", ""), 999))
    result["tags"] = tags
    return result
