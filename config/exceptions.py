import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            detail = response.data.get("detail")
            if isinstance(detail, list):
                response.data["detail"] = detail[0] if detail else None
        return response

    if isinstance(exc, Http404):
        return Response(
            {"detail": "Ressource introuvable.", "code": "not_found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if isinstance(exc, DjangoPermissionDenied):
        return Response(
            {"detail": "Permission refusée.", "code": "permission_denied"},
            status=status.HTTP_403_FORBIDDEN,
        )

    request = context.get("request")
    logger.exception("Unhandled exception: %s", exc, extra={"path": getattr(request, "path", None)})
    return Response(
        {
            "detail": "Une erreur interne s'est produite.",
            "code": "server_error",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporairement indisponible."
    default_code = "service_unavailable"
