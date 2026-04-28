from py3dbp import Packer, Bin as PyBin, Item as PyItem
from models import PackRequest, PackResponse, SelectedBin, PackedItem, Coordinates, Dimensions

class PackerService:
    @staticmethod
    def calculate_packing(request: PackRequest) -> PackResponse:
        # Sort bins by volume ascending to find the smallest possible bin
        sorted_bins = sorted(
            request.bins,
            key=lambda b: b.width * b.height * b.depth
        )

        total_items_to_pack = sum(item.quantity for item in request.items)

        # Iterate through bins from smallest to largest
        for bin_spec in sorted_bins:
            packer = Packer()
            # Add the current bin being evaluated
            packer.add_bin(PyBin(
                bin_spec.id,
                bin_spec.width,
                bin_spec.height,
                bin_spec.depth,
                bin_spec.max_weight
            ))

            # Add all items to the packer
            for item in request.items:
                for i in range(item.quantity):
                    # Append index to ID to make it unique for py3dbp if quantity > 1
                    item_id = f"{item.id}_{i}" if item.quantity > 1 else item.id
                    packer.add_item(PyItem(
                        item_id,
                        item.width,
                        item.height,
                        item.depth,
                        item.weight
                    ))

            # Perform the packing calculation
            packer.pack()

            # Check if all items fit in this bin
            evaluated_bin = packer.bins[0]
            unfitted = packer.unfit_items

            if len(unfitted) == 0:
                # We found the smallest bin that fits everything!
                bin_volume = bin_spec.width * bin_spec.height * bin_spec.depth
                
                # Calculate utilized volume based on item dimensions
                utilized_volume = sum(
                    float(item.width) * float(item.height) * float(item.depth) 
                    for item in evaluated_bin.items
                )
                
                total_weight = sum(float(item.weight) for item in evaluated_bin.items)
                
                utilization_pct = (utilized_volume / bin_volume) * 100 if bin_volume > 0 else 0

                selected_bin = SelectedBin(
                    id=bin_spec.id,
                    width=bin_spec.width,
                    height=bin_spec.height,
                    depth=bin_spec.depth,
                    volume=bin_volume,
                    utilization_percentage=round(utilization_pct, 2),
                    total_weight=round(total_weight, 2)
                )

                packed_items_res = []
                for b_item in evaluated_bin.items:
                    # Py3dbp defines rotation type implicitly by mapping WHD.
                    # We can use rotation type as a string based on its current dimensions vs original.
                    # py3dbp stores rotation_type as integer from 0 to 5.
                    rotation_map = {
                        0: "WxHxD",
                        1: "HxWxD",
                        2: "HxDxW",
                        3: "WxDxH",
                        4: "DxHxW",
                        5: "DxWxH"
                    }
                    
                    packed_items_res.append(PackedItem(
                        id=b_item.name.rsplit('_', 1)[0] if '_' in b_item.name and b_item.name.rsplit('_', 1)[1].isdigit() else b_item.name,
                        coordinates=Coordinates(x=float(b_item.position[0]), y=float(b_item.position[1]), z=float(b_item.position[2])),
                        dimensions_used=Dimensions(width=float(b_item.width), height=float(b_item.height), depth=float(b_item.depth)),
                        rotation_type=rotation_map.get(b_item.rotation_type, "Unknown")
                    ))

                return PackResponse(
                    order_id=request.order_id,
                    status="success",
                    selected_bin=selected_bin,
                    packed_items=packed_items_res,
                    unpacked_items=[]
                )

        # If we reach here, no single bin could hold all items
        # Let's find the bin that could hold the MOST items, or just return failure.
        # For MVP, we return status failure and the list of items that couldn't be packed in the largest bin.
        
        largest_bin_packer = Packer()
        largest_bin_spec = sorted_bins[-1] if sorted_bins else None
        
        if largest_bin_spec:
            largest_bin_packer.add_bin(PyBin(
                largest_bin_spec.id,
                largest_bin_spec.width,
                largest_bin_spec.height,
                largest_bin_spec.depth,
                largest_bin_spec.max_weight
            ))
            for item in request.items:
                for i in range(item.quantity):
                    item_id = f"{item.id}_{i}" if item.quantity > 1 else item.id
                    largest_bin_packer.add_item(PyItem(
                        item_id,
                        item.width,
                        item.height,
                        item.depth,
                        item.weight
                    ))
            largest_bin_packer.pack()
            unfitted_names = [i.name.rsplit('_', 1)[0] if '_' in i.name and i.name.rsplit('_', 1)[1].isdigit() else i.name for i in largest_bin_packer.unfit_items]
            
            return PackResponse(
                order_id=request.order_id,
                status="failure",
                selected_bin=None,
                packed_items=[],
                unpacked_items=list(set(unfitted_names))
            )
            
        return PackResponse(
            order_id=request.order_id,
            status="failure",
            selected_bin=None,
            packed_items=[],
            unpacked_items=[item.id for item in request.items]
        )
