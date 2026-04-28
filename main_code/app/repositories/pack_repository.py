"""
REDIMENSION — Pack Repository.

Handles all database interactions for the packing workflow:
fetching box types and SKUs, and persisting packing results.
"""

import logging
from typing import List, Tuple

from app.core.database import connect_db, prisma
from app.core.exceptions import REDIMENSIONException
from app.models.domain import DomainBin, DomainItem
from app.models.schemas import PackRequest, PackResponse

logger = logging.getLogger(__name__)

# Default max weight (kg) when not specified in box catalog
_DEFAULT_MAX_WEIGHT_KG = 100.0


class PackRepository:
    """Data-access layer for the packing engine."""

    @staticmethod
    def get_bins_and_items(
        request: PackRequest,
    ) -> Tuple[List[DomainBin], List[DomainItem]]:
        """
        Fetch BoxTypes and SKUs for the given tenant from the database.

        Args:
            request: Validated packing request with tenant_id and item list.

        Returns:
            Tuple of (available bins, requested items) as domain models.

        Raises:
            REDIMENSIONException: If no boxes exist or a requested SKU is missing.
        """
        connect_db()

        tenant_id = request.tenant_id

        # 1. Fetch BoxTypes for the tenant
        boxes = prisma.boxtype.find_many(where={"tenantId": tenant_id})
        if not boxes:
            raise REDIMENSIONException(
                "No BoxTypes found for this tenant.", 400
            )

        domain_bins = [
            DomainBin(
                id=b.id,
                name=b.name,
                width=b.width_cm,
                height=b.height_cm,
                depth=b.length_cm,
                max_weight=_DEFAULT_MAX_WEIGHT_KG,
            )
            for b in boxes
        ]
        logger.info(
            "Loaded %d box types for tenant %s", len(domain_bins), tenant_id
        )

        # 2. Fetch requested SKUs
        sku_codes = [item.sku_code for item in request.items]
        skus = prisma.sku.find_many(
            where={
                "tenantId": tenant_id,
                "skuCode": {"in": sku_codes},
            }
        )

        sku_map = {sku.skuCode: sku for sku in skus}

        domain_items: List[DomainItem] = []
        for req_item in request.items:
            sku_db = sku_map.get(req_item.sku_code)
            if not sku_db:
                raise REDIMENSIONException(
                    f"SKU '{req_item.sku_code}' not found for tenant.", 404
                )

            domain_items.append(
                DomainItem(
                    sku_id=sku_db.id,
                    sku_code=sku_db.skuCode,
                    width=sku_db.width_cm,
                    height=sku_db.height_cm,
                    depth=sku_db.length_cm,
                    weight=sku_db.weight_g / 1000.0,
                    quantity=req_item.quantity,
                )
            )

        logger.info(
            "Resolved %d SKU line(s) → %d total unit(s)",
            len(domain_items),
            sum(i.quantity for i in domain_items),
        )
        return domain_bins, domain_items

    @staticmethod
    def save_packing_result(
        response: PackResponse,
        request: PackRequest,
        domain_items: List[DomainItem],
    ) -> str:
        """
        Persist the packing result as an OrderHistory record.

        Args:
            response: The computed packing response.
            request: The original packing request.
            domain_items: The resolved domain items.

        Returns:
            The created OrderHistory ID, or empty string if no bin was selected.
        """
        connect_db()

        if not response.selected_bin:
            return ""

        items_to_create = [
            {"skuId": d_item.sku_id, "quantity": d_item.quantity}
            for d_item in domain_items
        ]

        history = prisma.orderhistory.create(
            data={
                "tenantId": request.tenant_id,
                "orderReference": response.order_reference,
                "selectedBoxId": response.selected_bin.id,
                "redLength_cm": response.selected_bin.depth,
                "redWidth_cm": response.selected_bin.width,
                "redHeight_cm": response.selected_bin.height,
                "redVolume_cm3": response.selected_bin.volume,
                "theoLength_cm": response.selected_bin.depth,
                "theoWidth_cm": response.selected_bin.width,
                "theoHeight_cm": response.selected_bin.height,
                "theoVolume_cm3": response.selected_bin.volume,
                "items": {"create": items_to_create},
            }
        )

        logger.info(
            "Saved OrderHistory id=%s for order '%s'",
            history.id, response.order_reference,
        )
        return history.id
