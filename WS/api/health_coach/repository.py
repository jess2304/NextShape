from __future__ import annotations

from typing import Optional

from api.models import CustomUser, ProgressRecord  # noqa


class ProgressRepository:
    """
    Data access layer for progress records.
    """

    @staticmethod
    def get_latest_progress(user_id: int) -> Optional[ProgressRecord]:
        return ProgressRecord.objects.filter(user_id=user_id).order_by("-date").first()
