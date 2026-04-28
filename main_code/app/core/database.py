"""
Centralized Prisma database client management.

This module provides a single global Prisma instance and helper functions
to manage its connection lifecycle. All repositories should import `prisma`
from this module instead of creating their own instances.
"""

import logging

from prisma import Prisma

logger = logging.getLogger(__name__)

# Single global Prisma client (sync mode, as configured in schema.prisma)
prisma = Prisma()


def connect_db() -> None:
    """Connect the global Prisma client if not already connected."""
    if not prisma.is_connected():
        prisma.connect()
        logger.info("Prisma database client connected.")


def disconnect_db() -> None:
    """Disconnect the global Prisma client if currently connected."""
    if prisma.is_connected():
        prisma.disconnect()
        logger.info("Prisma database client disconnected.")
