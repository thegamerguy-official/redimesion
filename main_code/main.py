from fastapi import FastAPI, HTTPException
from models import PackRequest, PackResponse
from packer_service import PackerService

app = FastAPI(
    title="REDIMENSION API",
    description="Motor de Cálculo MVP (3D Bin Packing) para optimización espacial de cajas.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "REDIMENSION API is running. Access /docs for Swagger UI."}

@app.post("/api/v1/pack", response_model=PackResponse)
def pack_items(request: PackRequest):
    try:
        if not request.bins:
            raise HTTPException(status_code=400, detail="At least one bin must be provided.")
        if not request.items:
            raise HTTPException(status_code=400, detail="At least one item must be provided.")

        response = PackerService.calculate_packing(request)
        return response
    except Exception as e:
        # In a real app we'd log this exception
        raise HTTPException(status_code=500, detail=str(e))
