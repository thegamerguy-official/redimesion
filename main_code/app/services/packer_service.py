"""
REDIMENSION — 3D Bin Packing Service.

Evaluates all available bins in parallel using ProcessPoolExecutor
to determine the smallest container that fits all order items.
"""

import concurrent.futures
import logging
import time
from typing import List, Optional, Tuple

from py3dbp import Bin as PyBin, Item as PyItem, Packer

from app.models.domain import DomainBin, DomainItem
from app.models.schemas import (
    Coordinates,
    Dimensions,
    PackedItemSchema,
    PackResponse,
    SelectedBinSchema,
)

logger = logging.getLogger(__name__)

# Mapping from py3dbp rotation type index → human-readable axis label
_ROTATION_MAP: dict[int, str] = {
    0: "WxHxD",
    1: "HxWxD",
    2: "HxDxW",
    3: "WxDxH",
    4: "DxHxW",
    5: "DxWxH",
}


def _parse_sku_code(item_name: str) -> str:
    """
    Extract the original SKU code from an item name that may have
    a '_N' suffix appended for duplicate units.

    Examples:
        "USB-001"     → "USB-001"
        "USB-001_0"   → "USB-001"
        "USB-001_1"   → "USB-001"
    """
    if "_" in item_name:
        base, suffix = item_name.rsplit("_", 1)
        if suffix.isdigit():
            return base
    return item_name


def _evaluate_bin(
    bin_spec: DomainBin, domain_items: List[DomainItem]
) -> Tuple[bool, Optional[SelectedBinSchema], List[PackedItemSchema], List[str]]:
    """
    Evaluate whether all items fit into a single bin candidate.

    This function is defined at module level (not as a method) so it can
    be pickled by ProcessPoolExecutor for parallel execution.

    Args:
        bin_spec: The candidate container to evaluate.
        domain_items: All items to attempt packing.

    Returns:
        Tuple of (success, selected_bin_schema, packed_items, unpacked_skus).
    """
    packer = Packer()
    packer.add_bin(
        PyBin(
            bin_spec.id,
            bin_spec.width,
            bin_spec.height,
            bin_spec.depth,
            bin_spec.max_weight,
        )
    )

    # Expand items by quantity and add to packer
    for item in domain_items:
        for i in range(item.quantity):
            item_id = (
                f"{item.sku_code}_{i}" if item.quantity > 1 else item.sku_code
            )
            packer.add_item(
                PyItem(item_id, item.width, item.height, item.depth, item.weight)
            )

    packer.pack()

    evaluated_bin = packer.bins[0]

    # Check which items did NOT fit by comparing against packed items
    unfitted = [
        item for item in packer.items if item not in evaluated_bin.items
    ]

    if unfitted:
        unfitted_names = list({_parse_sku_code(i.name) for i in unfitted})
        return False, None, [], unfitted_names

    # All items fit — compute utilization metrics
    bin_volume = bin_spec.width * bin_spec.height * bin_spec.depth
    utilized_volume = sum(
        float(item.width) * float(item.height) * float(item.depth)
        for item in evaluated_bin.items
    )
    total_weight = sum(float(item.weight) for item in evaluated_bin.items)
    utilization_pct = (
        (utilized_volume / bin_volume) * 100 if bin_volume > 0 else 0
    )

    selected_bin = SelectedBinSchema(
        id=bin_spec.id,
        name=bin_spec.name,
        width=bin_spec.width,
        height=bin_spec.height,
        depth=bin_spec.depth,
        volume=bin_volume,
        utilization_percentage=round(utilization_pct, 2),
        total_weight=round(total_weight, 2),
    )

    packed_items_res = [
        PackedItemSchema(
            sku_code=_parse_sku_code(b_item.name),
            coordinates=Coordinates(
                x=float(b_item.position[0]),
                y=float(b_item.position[1]),
                z=float(b_item.position[2]),
            ),
            dimensions_used=Dimensions(
                width=float(b_item.width),
                height=float(b_item.height),
                depth=float(b_item.depth),
            ),
            rotation_type=_ROTATION_MAP.get(b_item.rotation_type, "Unknown"),
        )
        for b_item in evaluated_bin.items
    ]

    return True, selected_bin, packed_items_res, []


class PackerService:
    """3D Bin Packing engine with parallel bin evaluation."""

    @staticmethod
    def calculate_packing_parallel(
        order_reference: str,
        tenant_id: str,
        bins: List[DomainBin],
        items: List[DomainItem],
    ) -> PackResponse:
        """
        Evaluate all candidate bins in parallel and return the smallest
        bin that successfully fits all items.

        Args:
            order_reference: Unique order identifier.
            tenant_id: UUID of the tenant.
            bins: Available container types sorted by volume.
            items: Items to pack.

        Returns:
            PackResponse with status 'success' or 'failure'.
        """
        sorted_bins = sorted(
            bins, key=lambda b: b.width * b.height * b.depth
        )

        logger.info(
            "Starting parallel packing for order='%s' — %d bins × %d item lines",
            order_reference, len(sorted_bins), len(items),
        )
        start_time = time.perf_counter()

        success_results: List[Tuple[SelectedBinSchema, List[PackedItemSchema]]] = []
        best_failure_unpacked: List[str] = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_bin = {
                executor.submit(_evaluate_bin, b, items): b
                for b in sorted_bins
            }

            for future in concurrent.futures.as_completed(future_to_bin):
                success, selected_bin, packed, unpacked = future.result()
                if success and selected_bin is not None:
                    success_results.append((selected_bin, packed))
                elif not best_failure_unpacked or len(unpacked) < len(
                    best_failure_unpacked
                ):
                    best_failure_unpacked = unpacked

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if success_results:
            # Choose the smallest successful bin by volume
            success_results.sort(key=lambda x: x[0].volume)
            best_bin, best_packed = success_results[0]

            logger.info(
                "Packing SUCCESS for order='%s' — bin='%s' (%.1f%% util) in %.1fms",
                order_reference,
                best_bin.name,
                best_bin.utilization_percentage,
                elapsed_ms,
            )
            return PackResponse(
                order_reference=order_reference,
                tenant_id=tenant_id,
                status="success",
                selected_bin=best_bin,
                packed_items=best_packed,
                unpacked_items=[],
            )

        # No bin could fit all items
        all_skus = [i.sku_code for i in items]
        logger.warning(
            "Packing FAILURE for order='%s' — unpacked: %s (%.1fms)",
            order_reference,
            best_failure_unpacked or all_skus,
            elapsed_ms,
        )
        return PackResponse(
            order_reference=order_reference,
            tenant_id=tenant_id,
            status="failure",
            selected_bin=None,
            packed_items=[],
            unpacked_items=best_failure_unpacked if best_failure_unpacked else all_skus,
        )
