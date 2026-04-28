from pydantic import BaseModel, Field
from typing import List, Optional

# --- Request Models ---

class Item(BaseModel):
    id: str
    width: float
    height: float
    depth: float
    weight: float
    quantity: int = Field(default=1, ge=1)

class Bin(BaseModel):
    id: str
    width: float
    height: float
    depth: float
    max_weight: float

class PackRequest(BaseModel):
    order_id: str
    items: List[Item]
    bins: List[Bin]

# --- Response Models ---

class Coordinates(BaseModel):
    x: float
    y: float
    z: float

class Dimensions(BaseModel):
    width: float
    height: float
    depth: float

class PackedItem(BaseModel):
    id: str
    coordinates: Coordinates
    dimensions_used: Dimensions
    rotation_type: str

class SelectedBin(BaseModel):
    id: str
    width: float
    height: float
    depth: float
    volume: float
    utilization_percentage: float
    total_weight: float

class PackResponse(BaseModel):
    order_id: str
    status: str
    selected_bin: Optional[SelectedBin] = None
    packed_items: List[PackedItem] = []
    unpacked_items: List[str] = []
