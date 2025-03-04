from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HealthRecord
from .serializers import HealthRecordSerializer, LoginSerializer, RegisterSerializer


class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer


class RegisterView(generics.CreateAPIView):
    """
    Vue pour l'inscription d'un utilisateur.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
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

    def post(self, request, *args, **kwargs):
        """
        Gère la requête POST de connexion.
        Vérifie les identifiants et renvoie un token JWT.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
