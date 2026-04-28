"""
REDIMENSION — Empirical Validation Tests ("Air Experiment").

These integration tests validate the packing engine against real-world
test cases documented in the REDIMENSION business context.
"""

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Case 1: Micro-product (1 USB stick → Sobre Kraft)
# ---------------------------------------------------------------------------

def test_caso_1_micro_producto(tenant_id: str) -> None:
    """A single tiny product should be packed into the smallest envelope."""
    payload = {
        "tenant_id": tenant_id,
        "items": [{"sku_code": "USB-001", "quantity": 1}],
    }

    response = client.post("/api/v1/pack/TEST-CASO-1", json=payload)
    assert response.status_code == status.HTTP_200_OK, (
        f"Expected 200 but got {response.status_code}: {response.text}"
    )

    data = response.json()
    assert data["status"] == "success", f"Packing failed: {data}"
    assert "Sobre Kraft" in data["selected_bin"]["name"], (
        f"Expected 'Sobre Kraft' but got '{data['selected_bin']['name']}'"
    )
    assert len(data["packed_items"]) == 1
    assert data["packed_items"][0]["sku_code"] == "USB-001"


# ---------------------------------------------------------------------------
# Case 2: Multiple textiles (1 pants + 2 shirts + 1 belt → Caja A)
# ---------------------------------------------------------------------------

def test_caso_2_textil_multiple(tenant_id: str) -> None:
    """Multiple flexible clothing items should fit into a standard box."""
    payload = {
        "tenant_id": tenant_id,
        "items": [
            {"sku_code": "PANTS-01", "quantity": 1},
            {"sku_code": "TSHIRT-01", "quantity": 2},
            {"sku_code": "BELT-01", "quantity": 1},
        ],
    }

    response = client.post("/api/v1/pack/TEST-CASO-2", json=payload)
    assert response.status_code == status.HTTP_200_OK, (
        f"Expected 200 but got {response.status_code}: {response.text}"
    )

    data = response.json()
    assert data["status"] == "success", f"Packing failed: {data}"
    assert data["selected_bin"]["name"] == "Caja A", (
        f"Expected 'Caja A' but got '{data['selected_bin']['name']}'"
    )
    assert len(data["packed_items"]) == 4, (
        f"Expected 4 packed items but got {len(data['packed_items'])}"
    )


# ---------------------------------------------------------------------------
# Case 3: Tetris effect (4 hardcover books → Caja Cúbica)
# ---------------------------------------------------------------------------

def test_caso_3_efecto_tetris(tenant_id: str) -> None:
    """Books stacked with rotation should fit into a cubic box."""
    payload = {
        "tenant_id": tenant_id,
        "items": [{"sku_code": "BOOK-01", "quantity": 4}],
    }

    response = client.post("/api/v1/pack/TEST-CASO-3", json=payload)
    assert response.status_code == status.HTTP_200_OK, (
        f"Expected 200 but got {response.status_code}: {response.text}"
    )

    data = response.json()
    assert data["status"] == "success", f"Packing failed: {data}"
    assert data["selected_bin"]["name"] == "Caja Cúbica", (
        f"Expected 'Caja Cúbica' but got '{data['selected_bin']['name']}'"
    )
    assert len(data["packed_items"]) == 4, (
        f"Expected 4 packed items but got {len(data['packed_items'])}"
    )
