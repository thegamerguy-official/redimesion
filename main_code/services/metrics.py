from datetime import datetime
from prisma import Prisma
from typing import Dict, Any

async def get_monthly_metrics(db: Prisma, tenant_id: str, month_start: datetime, month_end: datetime) -> Dict[str, Any]:
    """
    Calcula las métricas de ESG (Ahorro de cartón) y la reducción en peso volumétrico
    para un Tenant en un rango de fechas.
    
    :param db: Instancia del cliente Prisma
    :param tenant_id: ID del Tenant (Cliente)
    :param month_start: Fecha y hora de inicio del periodo
    :param month_end: Fecha y hora de fin del periodo
    :return: Diccionario con los KPIs calculados
    """
    
    # Consultamos todos los pedidos procesados en ese periodo, incluyendo los datos de la caja seleccionada
    orders = await db.orderhistory.find_many(
        where={
            "tenantId": tenant_id,
            "processedAt": {
                "gte": month_start,
                "lte": month_end
            }
        },
        include={
            "selectedBox": True
        }
    )

    saved_cardboard_kg = 0.0
    saved_volumetric_weight_kg = 0.0
    total_orders = len(orders)

    for order in orders:
        # --- 1. Cálculo de Ahorro de Cartón (Kg) ---
        # Área de prisma rectangular = 2 * (L*W + L*H + W*H)
        # Multiplicamos por el factor 1.5 por las solapas adicionales de una caja tipo RSC
        # Dividimos por 10,000 para pasar de cm2 a m2
        area_theo_m2 = (2 * (
            order.theoLength_cm * order.theoWidth_cm +
            order.theoLength_cm * order.theoHeight_cm +
            order.theoWidth_cm * order.theoHeight_cm
        ) * 1.5) / 10000.0
        
        area_red_m2 = (2 * (
            order.redLength_cm * order.redWidth_cm +
            order.redLength_cm * order.redHeight_cm +
            order.redWidth_cm * order.redHeight_cm
        ) * 1.5) / 10000.0
        
        # El gramaje viene del catálogo de cajas del tenant (si no existe, usamos 0.5 kg/m2 por defecto)
        grammage = order.selectedBox.grammage_kg_m2 if order.selectedBox else 0.5
        
        # Ahorro = (Área base teórica - Área óptima REDIMENSION) * gramaje del cartón
        saved_cardboard_kg += (area_theo_m2 - area_red_m2) * grammage
        
        
        # --- 2. Cálculo de Ahorro en Peso Volumétrico (Kg facturables) ---
        # Fórmula estándar logística: Volumen en cm3 / 5000
        saved_volumetric_weight_kg += (order.theoVolume_cm3 - order.redVolume_cm3) / 5000.0

    return {
        "tenantId": tenant_id,
        "period": {
            "start": month_start.isoformat(),
            "end": month_end.isoformat()
        },
        "totalOrdersProcessed": total_orders,
        "savedCardboardKg": round(saved_cardboard_kg, 4),
        "savedVolumetricWeightKg": round(saved_volumetric_weight_kg, 4)
    }
