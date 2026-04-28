"""
Metrics Service — ESG & Sustainability KPI Calculations.

Calculates cardboard savings (kg) and volumetric weight reduction
for a given tenant over a date range, based on processed order history.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from app.core.database import prisma, connect_db

logger = logging.getLogger(__name__)

# Default grammage (kg/m²) when box type data is unavailable
_DEFAULT_GRAMMAGE_KG_M2 = 0.5

# Standard logistics divisor for volumetric weight (cm³ → kg)
_VOLUMETRIC_WEIGHT_DIVISOR = 5000.0

# RSC box flap factor (extra surface area from flaps)
_RSC_FLAP_FACTOR = 1.5

# cm² to m² conversion divisor
_CM2_TO_M2_DIVISOR = 10_000.0


def _calculate_box_surface_area_m2(
    length_cm: float, width_cm: float, height_cm: float
) -> float:
    """
    Calculate the surface area of a rectangular box in m², adjusted
    for RSC (Regular Slotted Container) flaps.

    Formula: 2 * (L*W + L*H + W*H) * flap_factor / 10000
    """
    raw_area_cm2 = 2 * (
        length_cm * width_cm
        + length_cm * height_cm
        + width_cm * height_cm
    )
    return (raw_area_cm2 * _RSC_FLAP_FACTOR) / _CM2_TO_M2_DIVISOR


class MetricsService:
    """Service for computing sustainability and logistics KPIs."""

    @staticmethod
    def get_monthly_metrics(
        tenant_id: str,
        month_start: datetime,
        month_end: datetime,
    ) -> Dict[str, Any]:
        """
        Calculate ESG metrics (cardboard savings) and volumetric weight
        reduction for a tenant within a date range.

        Args:
            tenant_id: UUID of the tenant.
            month_start: Start of the reporting period (inclusive).
            month_end: End of the reporting period (inclusive).

        Returns:
            Dictionary containing the computed KPIs.
        """
        connect_db()

        orders: List[Any] = prisma.orderhistory.find_many(
            where={
                "tenantId": tenant_id,
                "processedAt": {
                    "gte": month_start,
                    "lte": month_end,
                },
            },
            include={"selectedBox": True},
        )

        saved_cardboard_kg = 0.0
        saved_volumetric_weight_kg = 0.0
        total_orders = len(orders)

        logger.info(
            "Computing metrics for tenant=%s, orders=%d, period=%s→%s",
            tenant_id, total_orders, month_start.isoformat(), month_end.isoformat(),
        )

        for order in orders:
            # 1. Cardboard savings (kg)
            area_theo_m2 = _calculate_box_surface_area_m2(
                order.theoLength_cm, order.theoWidth_cm, order.theoHeight_cm,
            )
            area_red_m2 = _calculate_box_surface_area_m2(
                order.redLength_cm, order.redWidth_cm, order.redHeight_cm,
            )

            grammage = (
                order.selectedBox.grammage_kg_m2
                if order.selectedBox
                else _DEFAULT_GRAMMAGE_KG_M2
            )
            saved_cardboard_kg += (area_theo_m2 - area_red_m2) * grammage

            # 2. Volumetric weight savings (billable kg)
            saved_volumetric_weight_kg += (
                (order.theoVolume_cm3 - order.redVolume_cm3)
                / _VOLUMETRIC_WEIGHT_DIVISOR
            )

        return {
            "tenantId": tenant_id,
            "period": {
                "start": month_start.isoformat(),
                "end": month_end.isoformat(),
            },
            "totalOrdersProcessed": total_orders,
            "savedCardboardKg": round(saved_cardboard_kg, 4),
            "savedVolumetricWeightKg": round(saved_volumetric_weight_kg, 4),
        }
