class DomainError(Exception):
    """Base domain exception."""

    def __init__(self, message: str = "A domain error occurred") -> None:
        super().__init__(message)
        self.message = message


class EntityNotFoundError(DomainError):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_name: str, entity_id: str | int) -> None:
        super().__init__(f"{entity_name} with id '{entity_id}' not found.")
        self.entity_name = entity_name
        self.entity_id = entity_id


class EntityConflictError(DomainError):
    """Raised when an entity already exists or conflicts with existing state."""


class AuthenticationError(DomainError):
    """Raised when a caller presents a missing or invalid credential."""

    def __init__(self, message: str = "Invalid or missing API key.") -> None:
        super().__init__(message)


class ServiceUnavailableError(DomainError):
    """Raised when an upstream dependency or critical service is unavailable."""
