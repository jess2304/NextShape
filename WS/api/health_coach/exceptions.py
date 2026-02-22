class HealthCoachError(Exception):
    """Base exception for the health coach domain."""

    pass


class MissingProgressRecord(HealthCoachError):
    """Raised when user has no ProgressRecord and a feature requires it."""

    pass


class MissingNutritionPreferences(HealthCoachError):
    """Raised when user nutrition preferences are missing and required."""

    pass


class InvalidLLMOutput(HealthCoachError):
    """Raised when the LLM output cannot be validated."""

    pass
