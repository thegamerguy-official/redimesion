"""
REDIMENSION — Custom Exception Hierarchy and Global Error Handlers.

All domain-specific exceptions inherit from REDIMENSIONException,
which is caught by a single global handler returning consistent JSON errors.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class REDIMENSIONException(Exception):
    """Base exception for all REDIMENSION domain errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.status_code = status_code


class OrderNotFoundException(REDIMENSIONException):
    """Raised when a requested order does not exist in the database."""

    def __init__(self, order_reference: str):
        super().__init__(
            message=f"Order with reference '{order_reference}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnpackableItemsException(REDIMENSIONException):
    """Raised when the packing engine cannot fit all items into any available box."""

    def __init__(
        self,
        message: str = "Could not pack all items into the available boxes.",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def _redimension_exception_handler(
    request: Request, exc: REDIMENSIONException
) -> JSONResponse:
    """Global handler that converts REDIMENSIONException into a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "message": exc.message},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI application."""
    app.add_exception_handler(REDIMENSIONException, _redimension_exception_handler)
