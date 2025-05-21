import datetime

import pytest
from api.models import EmailVerificationCode
from django.utils import timezone


@pytest.mark.django_db
def test_code_is_expired_true():
    """
    Teste que la vérif du code is_expired retourne True après 10 minutes.
    """
    code = EmailVerificationCode.objects.create(
        email="expired@test.com",
        code="111111",
    )
    # forcer la date après sa création pour avoir un temps supérieur à 10 minutes
    code.created_at = timezone.now() - datetime.timedelta(minutes=11)
    code.save(update_fields=["created_at"])
    assert code.is_expired() is True


@pytest.mark.django_db
def test_code_is_expired_false():
    """
    Teste que la véfif du code is_expired retourne False si le code a moins de 10 minutes.
    """
    code = EmailVerificationCode.objects.create(
        email="valid@test.com",
        code="222222",
        created_at=timezone.now() - datetime.timedelta(minutes=5),
    )
    assert code.is_expired() is False
