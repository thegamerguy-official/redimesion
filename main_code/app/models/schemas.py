"""
REDIMENSION — API Request/Response Schemas.

Pydantic v2 models that define the public API contract.
These are serialized/deserialized at the HTTP boundary and are
separate from internal domain models.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class OrderItemRequest(BaseModel):
    """A single SKU line within a packing request."""

    sku_code: str = Field(..., description="Código de SKU (ej. USB-001)")
    quantity: int = Field(default=1, ge=1, description="Cantidad de este SKU")


class PackRequest(BaseModel):
    """Top-level packing request containing tenant context and items to pack."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                    "items": [
                        {"sku_code": "USB-001", "quantity": 1},
                        {"sku_code": "TSHIRT-01", "quantity": 2},
                    ],
                }
            ]
        }
    )

    tenant_id: str = Field(..., description="UUID del Tenant")
    items: List[OrderItemRequest] = Field(
        ..., min_length=1, description="Lista de SKUs a empacar"
    )


# ---------------------------------------------------------------------------
# Response Sub-Schemas
# ---------------------------------------------------------------------------

class Coordinates(BaseModel):
    """3D position of a packed item within its container (cm)."""

    x: float
    y: float
    z: float


class Dimensions(BaseModel):
    """Physical dimensions of a packed item after rotation (cm)."""

    width: float
    height: float
    depth: float


class PackedItemSchema(BaseModel):
    """A single item successfully placed inside the selected bin."""

    sku_code: str
    coordinates: Coordinates
    dimensions_used: Dimensions
    rotation_type: str


class SelectedBinSchema(BaseModel):
    """The optimal bin chosen by the packing engine."""

    id: str
    name: str
    width: float
    height: float
    depth: float
    volume: float
    utilization_percentage: float
    total_weight: float


# ---------------------------------------------------------------------------
# Top-Level Response
# ---------------------------------------------------------------------------

class PackResponse(BaseModel):
    """Complete packing result returned to the client."""

    order_reference: str
    tenant_id: str
    status: str
    history_id: Optional[str] = None
    selected_bin: Optional[SelectedBinSchema] = None
    packed_items: List[PackedItemSchema] = []
    unpacked_items: List[str] = []
