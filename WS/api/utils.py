import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from django.utils.crypto import get_random_string

from .models import EmailVerificationCode


def send_html_email(
    subject: str, to_email: str, html_content: str, reply_to: str | None = None
):
    """
    Envoie un email HTML via SMTP configuré dans settings.
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(html_content, "html"))

    context = ssl._create_unverified_context()
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls(context=context)
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(from_email, [to_email], msg.as_string())


def send_verification_email(email: str, code: str):
    """
    Email de vérification de compte.
    """
    subject = "NextShape - Vérification de votre adresse email"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
        <p>Bonjour,</p>
        <p>Nous devons vérifier que cette adresse email vous appartient bien pour poursuivre.</p>
        <p>Voici votre <strong>code de vérification personnel</strong> :</p>
        <h2 style="color: #2c3e50;">{code}</h2>
        <p>Ce code est <strong>valable pendant 10 minutes</strong>. Pour des raisons de sécurité, ne le partagez avec personne.</p>
        <p style="margin-top: 30px;">Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.</p>
        <p>Merci de votre confiance,</p>
        <p><strong>L'équipe NextShape</strong><br/>Prenez soin de vous, chaque jour.</p>
    </body>
    </html>
    """
    send_html_email(subject, email, html_content)


def send_contact_email(data: dict):
    """
    Email envoyé depuis le formulaire de contact.
    """
    subject = f"[Contact] Message de {data['name']}"
    to_email = getattr(settings, "CONTACT_INBOX", settings.DEFAULT_FROM_EMAIL)

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
        <h2>Vous avez reçu un nouveau message de {data['name']} via le formulaire de contact.</h2>
        <p><strong>Nom :</strong> {data['name']}</p>
        <p><strong>Email :</strong> {data['email']}</p>
        <p><strong>Message :</strong></p>
        <p style="white-space: pre-line;">{data['message']}</p>
    </body>
    </html>
    """
    send_html_email(subject, to_email, html_content, reply_to=data["email"])


def generate_and_send_verification_code(email):
    code = get_random_string(length=6, allowed_chars="0123456789")
    EmailVerificationCode.objects.create(email=email, code=code)
    send_verification_email(email, code)


def calculs_calories(weight, height, age, gender, activity_level, goal):
    # BMR (Mifflin-St Jeor)
    if gender == "H":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_factors = {
        "sedentaire": 1.2,
        "leger": 1.375,
        "modere": 1.55,
        "intense": 1.725,
        "tres_intense": 1.9,
    }
    tdee = bmr * activity_factors.get(activity_level, 1.2)

    if goal == "perte":
        calories = tdee - 300
    elif goal == "prise":
        calories = tdee + 300
    else:
        calories = tdee

    imc = weight / ((height / 100) ** 2)

    return {
        "imc": round(imc, 2),
        "bmr": round(bmr),
        "tdee": round(tdee),
        "calories_recommandees": round(calories),
    }
