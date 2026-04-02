"""
Schéma OpenAPI : regroupement par table métier (CRUD) et ordre des tags Swagger/Redoc.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

# Texte d’introduction Swagger / Redoc (convention des réponses JSON)
OPENAPI_INTRO = """
## Convention des réponses avec clés étrangères

Pour chaque relation, l’API renvoie **deux champs** :

- l’**identifiant** (`integer`) : nom du champ FK (`expediteur`, `author`, `filiere`, etc.) ;
- l’**objet imbriqué** : même nom suffixé par `_detail` (`expediteur_detail`, `author_detail`, `filiere_detail`, …).

Les listes paginées suivent le format DRF : `count`, `next`, `previous`, `results[]`.

Les schémas sous **Schemas** décomposent les `$ref` (ex. `UserList`, `MessageParentBrief`). Les **Examples** sur chaque opération montrent un JSON complet.

**Authentification** : `POST /api/auth/token/` — fournir `password` et **au moins un** parmi `email` ou `num_tel` (alias `numTel`).
"""

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
    "User": "Table `users_user` — CRUD, inscription publique, profil `/users/me/`.",
    "Institution": "Table `inscription_institution` — CRUD (objet plat, sans FK sortante).",
    "Domaine": "Table `inscription_domaine` — réponses : `institution` + `institution_detail`.",
    "Filière": "Table `inscription_filiere` — réponses : `domaine` + `domaine_detail` (domaine imbriqué avec institution).",
    "AffectFiliere": "Table `inscription_affectfiliere` — `user` + `user_detail`, `filiere` + `filiere_detail`.",
    "CategoriePost": "Table `post_categoriepost` — CRUD (pas de FK dans le schéma de catégorie).",
    "Publication": "Table `post_publication` — `type_pub` : communication | actualité ; `image` optionnelle (URL absolue en JSON) ; `author` + `author_detail`, `categorie` + `categorie_detail`.",
    "Horaire": "Table `post_horaire` — `filiere` + `filiere_detail` (filière avec domaine et institution imbriqués).",
    "Message": "Table `messagerie_message` — `expediteur`/`destinataire`/`parent` + champs `*_detail` ; `parent_detail` sans sous-arbre récursif.",
}

# Texte additionnel sur les opérations list/retrieve (détail de la forme JSON)
TAG_NESTED_DOC = {
    "Domaine": "Chaque élément inclut `institution` (id) et `institution_detail` (objet institution complet).",
    "Filière": "Chaque élément inclut `domaine` et `domaine_detail` (avec `institution` + `institution_detail` à l’intérieur).",
    "AffectFiliere": "Chaque élément inclut `user_detail` et `filiere_detail` en plus des ids.",
    "Publication": "Liste et détail : `author_detail` et `categorie_detail` sont toujours présents. Après POST/PATCH, la réponse reprend la même forme que le détail.",
    "Horaire": "Chaque élément inclut `filiere_detail` (filière + domaine + institution).",
    "Message": "Chaque message inclut `expediteur_detail`, `destinataire_detail`, et si `parent` est défini un objet `parent_detail` (sans `parent_detail` imbriqué dans le parent).",
}


def crud_table(tag: str, **extra):
    """
    Regroupe dans la doc OpenAPI toutes les opérations standard du ViewSet
    sous un même tag (= nom de table métier), avec résumés explicites CRUD.

    Paramètres optionnels (consommés ici, non passés à extend_schema_view) :
    - list_examples, retrieve_examples : listes d’OpenApiExample pour Swagger.
    """
    list_examples = extra.pop("list_examples", None)
    retrieve_examples = extra.pop("retrieve_examples", None)

    nested_line = TAG_NESTED_DOC.get(tag)

    def _op_schema(summary_label: str, examples: list | None):
        kw: dict = {"tags": [tag], "summary": f"{summary_label} - {tag}"}
        if nested_line:
            kw["description"] = nested_line
        if examples:
            kw["examples"] = examples
        return extend_schema(**kw)

    kwargs = {
        "list": _op_schema("Liste", list_examples),
        "retrieve": _op_schema("Lecture (détail)", retrieve_examples),
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
