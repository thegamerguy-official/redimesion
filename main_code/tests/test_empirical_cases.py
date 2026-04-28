import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_caso_1_micro_producto():
    # Input: 1 Memoria USB. Output esperado: Sobre Kraft Acolchado A5
    payload = {
        "order_id": "TEST-CASO-1",
        "items": [
            {
                "id": "usb",
                "width": 5.0,
                "height": 2.0,
                "depth": 1.0,
                "weight": 0.05,
                "quantity": 1
            }
        ],
        "bins": [
            {
                "id": "Caja Estándar",
                "width": 30.0,
                "height": 20.0,
                "depth": 15.0,
                "max_weight": 5.0
            },
            {
                "id": "Sobre Kraft Acolchado A5",
                "width": 25.0,
                "height": 17.0,
                "depth": 3.0,
                "max_weight": 1.0
            }
        ]
    }
    
    response = client.post("/api/v1/pack", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["selected_bin"]["id"] == "Sobre Kraft Acolchado A5"
    assert len(data["packed_items"]) == 1
    assert data["packed_items"][0]["id"] == "usb"
    assert len(data["unpacked_items"]) == 0

def test_caso_2_textil_multiple():
    # Input: 1 pantalón, 2 camisetas, 1 cinturón. Output esperado: Caja compacta
    payload = {
        "order_id": "TEST-CASO-2",
        "items": [
            {
                "id": "pantalon",
                "width": 30.0,
                "height": 20.0,
                "depth": 5.0,
                "weight": 0.6,
                "quantity": 1
            },
            {
                "id": "camiseta",
                "width": 25.0,
                "height": 15.0,
                "depth": 3.0,
                "weight": 0.3,
                "quantity": 2
            },
            {
                "id": "cinturon",
                "width": 10.0,
                "height": 10.0,
                "depth": 5.0,
                "weight": 0.2,
                "quantity": 1
            }
        ],
        "bins": [
            {
                "id": "Caja Grande Sobredimensionada",
                "width": 50.0,
                "height": 40.0,
                "depth": 30.0,
                "max_weight": 10.0
            },
            {
                "id": "Caja Compacta",
                "width": 40.0,
                "height": 30.0,
                "depth": 15.0,
                "max_weight": 5.0
            }
        ]
    }
    
    response = client.post("/api/v1/pack", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["selected_bin"]["id"] == "Caja Compacta"
    assert len(data["packed_items"]) == 4 # 1 pantalón + 2 camisetas + 1 cinturón
    assert len(data["unpacked_items"]) == 0

def test_caso_3_efecto_tetris():
    # Input: 3 libros tapa dura y 1 libreta. Output esperado: Caja cúbica
    payload = {
        "order_id": "TEST-CASO-3",
        "items": [
            {
                "id": "libro",
                "width": 24.0,
                "height": 16.0,
                "depth": 3.0,
                "weight": 0.8,
                "quantity": 3
            },
            {
                "id": "libreta",
                "width": 21.0,
                "height": 15.0,
                "depth": 1.0,
                "weight": 0.3,
                "quantity": 1
            }
        ],
        "bins": [
            {
                "id": "Caja Larga Plana",
                "width": 60.0,
                "height": 40.0,
                "depth": 5.0,
                "max_weight": 10.0
            },
            {
                "id": "Caja Cúbica",
                "width": 26.0,
                "height": 18.0,
                "depth": 15.0, # 15 is enough depth for 3*3 + 1
                "max_weight": 10.0
            }
        ]
    }
    
    response = client.post("/api/v1/pack", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["selected_bin"]["id"] == "Caja Cúbica"
    assert len(data["packed_items"]) == 4
    assert len(data["unpacked_items"]) == 0
