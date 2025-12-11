"""
Custom exceptions for the application
"""


class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class ValidationError(DomainException):
    """Raised when validation fails."""
    pass


class PredictionError(DomainException):
    """Raised when prediction fails."""
    pass


class ModelNotFoundError(DomainException):
    """Raised when ML model is not found."""
    pass


class RepositoryError(Exception):
    """Raised when repository operations fail."""
    pass
