import io

from fastapi import APIRouter, UploadFile, HTTPException
from helpers.data_scraping.scripts.scrape_all import scrape_all
from service import data_service, training_service, visualizations_service

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


@router.get("/train")
async def create_training_df():
    training_service.train_model_and_make_predictions(5)
    response = {
        "message": "Perfect! :)"
    }
    return response


@router.get("/modelStatistics")
def model_statistics_visualization():
    try:
        visualization_json = visualizations_service.create_model_statistics_visualization()
    except HTTPException as e:
        raise e
    return visualization_json


@router.get("/neptunDataset")
def neptun_dataset():
    training_service.create_research_training_df()
