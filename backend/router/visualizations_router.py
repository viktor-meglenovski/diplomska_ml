from fastapi import APIRouter, HTTPException
from starlette.responses import HTMLResponse
import service.visualizations_service as visualizations_service

router = APIRouter()


@router.get("/{product_id}")
def send_visualization(product_id: int):
    try:
        visualization_json = visualizations_service.create_visualization_for_product(product_id)
    except HTTPException as e:
        raise e
    return visualization_json
