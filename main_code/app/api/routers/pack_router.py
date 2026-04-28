"""
REDIMENSION — Pack Router.

REST endpoints for the 3D bin packing engine.
"""

import logging

from fastapi import APIRouter, status

from app.models.schemas import PackRequest, PackResponse
from app.repositories.pack_repository import PackRepository
from app.services.packer_service import PackerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/pack/{order_reference}",
    response_model=PackResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate optimal packing for an order",
)
def pack_items(order_reference: str, request: PackRequest) -> PackResponse:
    """
    Evaluate all items for the given order and determine the optimal
    packing box.

    **Workflow:**
    1. Fetch the tenant's box catalog and resolve requested SKUs from the DB.
    2. Run the 3D bin packing algorithm in parallel across all candidate bins.
    3. Persist the result to OrderHistory and return the response.
    """
    logger.info(
        "Received pack request: order='%s', tenant='%s', items=%d",
        order_reference, request.tenant_id, len(request.items),
    )

    # 1. Fetch domain data from PostgreSQL (via Prisma)
    domain_bins, domain_items = PackRepository.get_bins_and_items(request)

    # 2. Run parallel 3D bin packing
    response = PackerService.calculate_packing_parallel(
        order_reference=order_reference,
        tenant_id=request.tenant_id,
        bins=domain_bins,
        items=domain_items,
    )

    # 3. Persist result to database
    history_id = PackRepository.save_packing_result(
        response, request, domain_items
    )
    response.history_id = history_id

    return response
