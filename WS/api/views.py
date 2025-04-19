from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UpdateProfileSerializer


class RegisterView(generics.CreateAPIView):
    """
    Vue pour l'inscription d'un utilisateur.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Gère la requête POST d'inscription.
        Si tout est valide, crée l'utilisateur et retourne un message de succès.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Inscription réussie. Veuillez vous connecter."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Vue pour la connexion d'un utilisateur.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Gère la requête POST de connexion.
        Vérifie les identifiants et renvoie un token JWT.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(APIView):
    """
    Vue pour modifier les données d'un utilisateur.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Gère la requête PATCH de modification de l'utilisateur.
        """
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    """
    Vue pour supprimer le compte définitivement de la base.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(
            {"detail": "Votre compte a été supprimé avec succès."},
            status=status.HTTP_200_OK,
        )
