"""
REDIMENSION — Domain Models.

Pure domain entities used internally by the packing engine and services.
These are decoupled from both the API schemas and the database models.
"""

from pydantic import BaseModel, ConfigDict


class DomainItem(BaseModel):
    """A single product item to be packed, with physical dimensions."""

    model_config = ConfigDict(frozen=True)

    sku_id: str
    sku_code: str
    width: float
    height: float
    depth: float
    weight: float
    quantity: int


class DomainBin(BaseModel):
    """A candidate box/container that items can be packed into."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    width: float
    height: float
    depth: float
    max_weight: float
