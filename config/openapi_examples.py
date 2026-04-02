"""
Exemples JSON pour Swagger / Redoc (réponses paginées + objets avec FK + *_detail).
"""

USER_LIST = {
    "id": 1,
    "email": "user@example.com",
    "matricule": "MAT-001",
    "num_tel": "+243900000001",
    "first_name": "Jean",
    "troisieme_nom": "",
    "last_name": "Dupont",
    "photo_profil": "http://127.0.0.1:8000/media/profils/2026/04/photo.jpg",
    "role": "etudiant",
    "is_active": True,
    "date_joined": "2019-08-24T14:15:22Z",
}

INSTITUTION = {
    "id": 1,
    "nom": "Université exemple",
    "code": "UNI1",
    "adresse": "Kinshasa",
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z",
}

DOMAINE = {
    "id": 1,
    "institution": 1,
    "institution_detail": INSTITUTION,
    "nom": "Sciences",
    "code": "SCI",
}

FILIERE = {
    "id": 1,
    "domaine": 1,
    "domaine_detail": DOMAINE,
    "nom": "Informatique",
    "code": "INFO",
}

MESSAGE_PARENT = {
    "id": 10,
    "expediteur": 2,
    "expediteur_detail": {**USER_LIST, "id": 2, "email": "autre@example.com"},
    "destinataire": 1,
    "destinataire_detail": USER_LIST,
    "parent": None,
    "sujet": "Fil initial",
    "corps": "Bonjour",
    "lu": True,
    "created_at": "2019-08-24T12:00:00Z",
}

MESSAGE = {
    "id": 11,
    "expediteur": 1,
    "expediteur_detail": USER_LIST,
    "destinataire": 2,
    "destinataire_detail": {**USER_LIST, "id": 2, "email": "dest@example.com"},
    "parent": 10,
    "parent_detail": MESSAGE_PARENT,
    "sujet": "Re: Fil initial",
    "corps": "Réponse",
    "lu": False,
    "created_at": "2019-08-24T14:15:22Z",
}

PAGINATED_MESSAGES = {
    "count": 123,
    "next": "http://api.example.org/api/messages/?page=2",
    "previous": "http://api.example.org/api/messages/?page=1",
    "results": [MESSAGE],
}

CATEGORIE = {
    "id": 1,
    "nom": "Recherche",
    "slug": "recherche",
    "description": "",
    "students_can_manage": True,
}

PUBLICATION = {
    "id": 1,
    "titre": "Publication exemple",
    "type_pub": "actualite",
    "statut": "actif",
    "categorie": 1,
    "categorie_detail": CATEGORIE,
    "author": 1,
    "author_detail": USER_LIST,
    "image": "http://api.example.org/media/publications/2026/04/visuel.jpg",
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z",
    "contenu": "Texte complet…",
}

PAGINATED_PUBLICATIONS = {
    "count": 50,
    "next": None,
    "previous": None,
    "results": [{k: v for k, v in PUBLICATION.items() if k != "contenu"}],
}

HORAIRE = {
    "id": 1,
    "filiere": 1,
    "filiere_detail": FILIERE,
    "description": "Horaire semestre",
    "fichier": "http://api.example.org/media/horaires/2026/04/cours.pdf",
    "date_debut": "2026-01-01",
    "date_fin": "2026-06-30",
    "statut": "actif",
}

PAGINATED_HORAIRES = {
    "count": 5,
    "next": None,
    "previous": None,
    "results": [HORAIRE],
}

AFFECTATION = {
    "id": 1,
    "user": 1,
    "filiere": 1,
    "date_debut": "2026-01-01",
    "date_fin": None,
    "user_detail": USER_LIST,
    "filiere_detail": FILIERE,
}

PAGINATED_AFFECTATIONS = {
    "count": 10,
    "next": None,
    "previous": None,
    "results": [AFFECTATION],
}

PAGINATED_DOMAINES = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [DOMAINE],
}

PAGINATED_FILIERES = {
    "count": 8,
    "next": None,
    "previous": None,
    "results": [FILIERE],
}
