from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from inscription.views import (
    AffectFiliereViewSet,
    DomaineViewSet,
    FiliereViewSet,
    InstitutionViewSet,
)
from messagerie.views import MessageViewSet
from post.views import CategoriePostViewSet, HoraireViewSet, PublicationViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r"institutions", InstitutionViewSet, basename="institution")
router.register(r"domaines", DomaineViewSet, basename="domaine")
router.register(r"filieres", FiliereViewSet, basename="filiere")
router.register(r"affectations-filiere", AffectFiliereViewSet, basename="affectation-filiere")
router.register(r"users", UserViewSet, basename="user")
router.register(r"categories-publications", CategoriePostViewSet, basename="categorie-publication")
router.register(r"publications", PublicationViewSet, basename="publication")
router.register(r"horaires", HoraireViewSet, basename="horaire")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("authentication.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
