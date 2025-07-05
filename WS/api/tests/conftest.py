import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="djazz@domain.com",
        username="djazz@domain.com",
        password="password",
    )
