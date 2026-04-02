import django_filters

from post.models import (
    CategoriePost,
    Horaire,
    Publication,
    PublicationStatut,
    PublicationType,
)


class CategoriePostFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CategoriePost
        fields = ("nom", "slug", "students_can_manage")


class PublicationFilter(django_filters.FilterSet):
    statut = django_filters.ChoiceFilter(choices=PublicationStatut.choices)
    type_pub = django_filters.ChoiceFilter(choices=PublicationType.choices)
    categorie = django_filters.NumberFilter()
    author = django_filters.NumberFilter()
    created_after = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Publication
        fields = ("statut", "type_pub", "categorie", "author")


class HoraireFilter(django_filters.FilterSet):
    filiere = django_filters.NumberFilter()
    statut = django_filters.CharFilter()
    date_debut_gte = django_filters.DateFilter(field_name="date_debut", lookup_expr="gte")
    date_fin_lte = django_filters.DateFilter(field_name="date_fin", lookup_expr="lte")

    class Meta:
        model = Horaire
        fields = ("filiere", "statut")
