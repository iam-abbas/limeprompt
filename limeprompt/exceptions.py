"""Custom exceptions for the Limeprompt library."""


class LimepromptError(Exception):
    """Base exception for Limeprompt errors."""


class InvalidInputError(LimepromptError):
    """Exception raised for invalid input parameters."""


class APIError(LimepromptError):
    """Exception raised for API-related errors."""


class OutputExtractionError(LimepromptError):
    """Exception raised when unable to extract output from API response."""
