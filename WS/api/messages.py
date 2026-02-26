from __future__ import annotations

from typing import Final

MESSAGES_FR: Final[dict[str, str]] = {
    "COMMON_SUCCESS": "Opération réussie.",
    "COMMON_ERROR": "Une erreur est survenue.",
    "AUTH_REGISTER_SUCCESS": "Inscription réussie. Veuillez vous connecter.",
    "AUTH_REGISTER_FAILED": "Échec de l'inscription.",
    "AUTH_LOGIN_SUCCESS": "Connexion réussie.",
    "AUTH_LOGIN_FAILED": "Échec de la connexion.",
    "AUTH_LOGOUT_SUCCESS": "Déconnecté.",
    "AUTH_CHECK_SUCCESS": "Statut d'authentification récupéré.",
    "AUTH_REFRESH_MISSING": "Refresh token manquant.",
    "AUTH_REFRESH_INVALID": "Refresh token invalide.",
    "AUTH_REFRESH_SUCCESS": "Nouveau token généré avec succès.",
    "PROFILE_UPDATE_SUCCESS": "Profil mis à jour avec succès.",
    "PROFILE_UPDATE_FAILED": "Échec de la mise à jour du profil.",
    "ACCOUNT_DELETE_SUCCESS": "Votre compte a été supprimé avec succès.",
    "VERIFICATION_CODE_SENT": "Code envoyé avec succès.",
    "VERIFICATION_CODE_SEND_FAILED": "Échec de l'envoi du code.",
    "VERIFICATION_CODE_INVALID_REQUEST": "Ce code est invalide.",
    "VERIFICATION_CODE_INCORRECT": "Code incorrect.",
    "VERIFICATION_CODE_EXPIRED": "Code expiré.",
    "VERIFICATION_CODE_VALID": "Code vérifié avec succès.",
    "PASSWORD_RESET_SUCCESS": "Mot de passe mis à jour avec succès.",
    "PASSWORD_RESET_FAILED": "Échec de la réinitialisation du mot de passe.",
    "CALORIES_RECORD_SUCCESS": "Enregistrement calorique effectué avec succès.",
    "CALORIES_RECORD_FAILED": "Échec de l'enregistrement des besoins caloriques.",
    "PROGRESS_RECORDS_FETCH_SUCCESS": "Historique récupéré avec succès.",
    "PROGRESS_RECORD_UPDATE_SUCCESS": "Enregistrement mis à jour avec succès.",
    "PROGRESS_RECORD_UPDATE_FAILED": "Échec de la mise à jour de l'enregistrement.",
    "PROGRESS_RECORD_DELETE_SUCCESS": "Enregistrement supprimé avec succès.",
    "PROGRESS_RECORD_NOT_FOUND": "Enregistrement introuvable.",
    "CONTACT_SUCCESS": "Message reçu avec succès.",
    "CONTACT_FAILED": "Échec de l'envoi du message.",
    "NUTRITION_PREFS_FETCH_SUCCESS": "Préférences récupérées avec succès.",
    "NUTRITION_PREFS_UPDATE_SUCCESS": "Préférences mises à jour avec succès.",
    "NUTRITION_PREFS_UPDATE_FAILED": "Échec de la mise à jour des préférences.",
    "COACH_WEEK_PLAN_SUCCESS": "Programme nutritionnel généré avec succès.",
    "COACH_WEEK_PLAN_SERVICE_UNAVAILABLE": "Service coach indisponible. Vérifiez la configuration IA.",
    "COACH_WEEK_PLAN_MISSING_PROGRESS": "Veuillez d'abord enregistrer vos informations (poids/taille/objectif) avant de générer un programme.",
    "COACH_WEEK_PLAN_MISSING_PREFS": "Veuillez renseigner vos préférences nutritionnelles avant de générer un programme.",
    "COACH_WEEK_PLAN_FAILED": "Une erreur est survenue lors de la génération.",
}


def resolve_message(code: str, fallback: str) -> str:
    return MESSAGES_FR.get(code, fallback)
