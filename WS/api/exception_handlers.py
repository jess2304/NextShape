from __future__ import annotations

from django.http import Http404
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.views import exception_handler as drf_exception_handler

from .response import error_response


def _extract_message(payload) -> str:
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, list) and detail:
            return str(detail[0])
        if detail is not None:
            return str(detail)

        for value in payload.values():
            if isinstance(value, list) and value:
                return str(value[0])
            if isinstance(value, str):
                return value
        return "Une erreur est survenue."

    if isinstance(payload, list) and payload:
        return str(payload[0])

    if isinstance(payload, str):
        return payload

    return "Une erreur est survenue."


def _resolve_code(exc, status_code: int) -> str:
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return "AUTH_REQUIRED"
    if isinstance(exc, PermissionDenied):
        return "PERMISSION_DENIED"
    if isinstance(exc, (Http404, NotFound)):
        return "NOT_FOUND"
    if isinstance(exc, Throttled) or status_code == 429:
        return "THROTTLED"
    if isinstance(exc, (ParseError, ValidationError)):
        return "BAD_REQUEST"
    return "COMMON_ERROR"


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    code = _resolve_code(exc, response.status_code)
    message = _extract_message(response.data)

    return error_response(
        code=code,
        message=message,
        errors=response.data,
        status_code=response.status_code,
    )
