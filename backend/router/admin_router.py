from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import Integer
from starlette.responses import HTMLResponse
from helpers.data_scraping.scripts.scrape_all import scrape_all
from service import data_service

router = APIRouter()

@router.get("")
async def root():
    # populate_products()
    return {"message": "Hello World"}


@router.get("/scrape_data")
async def scrape_data():
    scrape_all()
    return {"message": "Scraping Complete!"}


@router.post("/add_new_data")
async def add_new_data(file: UploadFile):
    data_service.add_new_data(file.file)
    return {"message": "New Data Added!"}


@router.get("/cluster_products")
async def cluster_products():
    data_service.cluster_products()
    return {"message": "Clustering Finished!"}