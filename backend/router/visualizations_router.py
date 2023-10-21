from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import HTMLResponse
import service.visualizations_service as visualizations_service
from models.auth_bearer import JWTBearer

router = APIRouter(prefix="/visualize", tags=["Visualizations"], dependencies=[Depends(JWTBearer())])


@router.get("/{product_id}")
def send_visualization(product_id: int):
    try:
        visualization_json = visualizations_service.create_visualization_for_product(product_id)
    except HTTPException as e:
        raise e
    return visualization_json

