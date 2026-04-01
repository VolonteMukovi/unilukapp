import django_filters

from inscription.models import AffectFiliere, Domaine, Filiere, Institution


class InstitutionFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr="icontains")
    code = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Institution
        fields = ("nom", "code")


class DomaineFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr="icontains")
    institution = django_filters.NumberFilter()

    class Meta:
        model = Domaine
        fields = ("nom", "code", "institution")


class FiliereFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr="icontains")
    domaine = django_filters.NumberFilter()
    institution = django_filters.NumberFilter(field_name="domaine__institution")

    class Meta:
        model = Filiere
        fields = ("nom", "code", "domaine", "institution")


class AffectFiliereFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter()
    filiere = django_filters.NumberFilter()

    class Meta:
        model = AffectFiliere
        fields = ("user", "filiere")
