import datetime

import pytest
from api.models import EmailVerificationCode
from django.utils import timezone


@pytest.mark.django_db
def test_code_is_expired_true():
    """
    Verify that is_expired returns True after 10 minutes.
    """
    code = EmailVerificationCode.objects.create(
        email="expired@test.com",
        code="111111",
    )
    # Force created_at to be more than 10 minutes old
    code.created_at = timezone.now() - datetime.timedelta(minutes=11)
    code.save(update_fields=["created_at"])
    assert code.is_expired() is True


@pytest.mark.django_db
def test_code_is_expired_false():
    """
    Verify that is_expired returns False when the code is less than 10 minutes old.
    """
    code = EmailVerificationCode.objects.create(
        email="valid@test.com",
        code="222222",
        created_at=timezone.now() - datetime.timedelta(minutes=5),
    )
    assert code.is_expired() is False
