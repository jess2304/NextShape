from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response

from .messages import resolve_message


def success_response(
    data=None,
    *,
    code="COMMON_SUCCESS",
    message: str | None = None,
    status_code=status.HTTP_200_OK,
):
    """
    Standard success response wrapper.
    """
    resolved_message = resolve_message(code, message or "Opération réussie.")
    return Response(
        {
            "success": True,
            "code": code,
            "message": resolved_message,
            "data": data,
        },
        status=status_code,
    )


def error_response(
    *,
    code="COMMON_ERROR",
    errors=None,
    data=None,
    message: str | None = None,
    status_code=status.HTTP_400_BAD_REQUEST,
):
    """
    Standard error response wrapper.
    """
    resolved_message = resolve_message(code, message or "Une erreur est survenue.")
    return Response(
        {
            "success": False,
            "code": code,
            "message": resolved_message,
            "data": data,
            "errors": errors,
        },
        status=status_code,
    )
