import io

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import Integer
from starlette.responses import HTMLResponse, StreamingResponse
from helpers.data_scraping.scripts.scrape_all import scrape_all
from service import data_service
import repository.data_repository as data_repository

router = APIRouter()


@router.get("")
async def root():
    # populate_products()
    return {"message": "Hello World"}


@router.get("/scrape_data")
async def scrape_data():
    csv_content, file_name, stats, total_number = scrape_all()

    response = {
        "file_name": file_name,
        "scraping_stats": stats,
        "total_number": total_number,
        "csv_file": csv_content
    }
    return response


@router.post("/add_new_data")
async def add_new_data(file: UploadFile):
    existing_products, new_products = data_service.add_new_data(file.file)
    return {'response': {'existing_products': existing_products, 'new_products': new_products}}


@router.get("/cluster_products")
async def cluster_products():
    data_service.cluster_products()
    return {"message": "Clustering Finished!"}


@router.get("/create_training_df")
async def create_training_df():
    data_service.train_model()
