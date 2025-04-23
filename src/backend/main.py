import logging
import os
import pymssql
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException
from typing import Annotated, List
from .models import *

# Load environment variables from .env file
load_dotenv()

# Azure Storage Config
BLOB_STORAGE_CONNECTION_STRING = os.getenv("BLOB_STORAGE_CONNECTION_STRING")
BLOB_STORAGE_CONTAINER_NAME = os.getenv("BLOB_STORAGE_CONTAINER_NAME")
BLOB_STORAGE_ENDPOINT = os.getenv("BLOB_STORAGE_ENDPOINT")

# Azure SQL Server Config
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

app = FastAPI(
    title="Products Register - Cloud E-Commerce API",
    root_path="/api"
)


@app.get("/products")
def get_products():
    try:
        with pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE) as conn:
            with conn.cursor(as_dict=True) as cursor:
                query = "SELECT id, name, description, price, image_url FROM dbo.products"
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
    except Exception as error:
        error_message = f"Failed to list products: {error}"
        logging.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@app.post("/products")
def add_product(products: List[Product]) -> BaseResponse:
    try:
        with pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE) as conn:
            with conn.cursor() as cursor:
                query = "INSERT INTO dbo.products (name, description, price, image_url) VALUES (%s, %s, %s, %s)"

                cursor.executemany(query, [(product.name, product.description, product.price, product.image_url) for product in products])
                conn.commit()
                return {"message": "Product inserted successfully"}
    except Exception as error:
        error_message = f"Failed to insert product: {error}"
        logging.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@app.post("/image/upload")
def upload_image(file: Annotated[bytes, File()]) -> ImageUploadResponse:
    try:
        blob_name = f"{uuid.uuid4()}.jpg"
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)
        blob_container_client = blob_service_client.get_container_client(BLOB_STORAGE_CONTAINER_NAME)
        blob_image_url = f"{BLOB_STORAGE_ENDPOINT}/{BLOB_STORAGE_CONTAINER_NAME}/{blob_name}"

        if not blob_container_client.exists():
            blob_service_client.create_container(BLOB_STORAGE_CONTAINER_NAME, public_access="blob")

        blob_client = blob_container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file, overwrite=True, content_settings=ContentSettings(content_type="image/jpg"))

        return {
            "image_id": blob_name,
            "image_url": blob_image_url
        }
    except Exception as error:
        error_message = f"Failed to upload image: {error}"
        logging.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)
