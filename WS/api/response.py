from rest_framework import status
from rest_framework.response import Response


def success_response(
    data=None, message="Opération réussie", status_code=status.HTTP_200_OK
):
    """
    Réponse standard en cas de succès.
    """
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(
    errors=None,
    message="Une erreur s'est produite",
    status_code=status.HTTP_400_BAD_REQUEST,
):
    """
    Réponse standard en cas d'erreur.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status=status_code,
    )
