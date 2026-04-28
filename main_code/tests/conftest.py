"""
Shared test fixtures for the REDIMENSION test suite.
"""

import pytest
from prisma import Prisma


@pytest.fixture(scope="module")
def tenant_id() -> str:
    """
    Retrieve the first tenant ID from the database.

    This fixture requires the seed script to have been run beforehand.
    It connects/disconnects its own Prisma client to avoid interfering
    with the application's global instance.
    """
    db = Prisma()
    db.connect()

    try:
        tenant = db.tenant.find_first()
        if not tenant:
            pytest.fail(
                "No tenant found in the database. "
                "Run the seed script first: npx ts-node seed.ts"
            )
        return tenant.id
    finally:
        db.disconnect()
