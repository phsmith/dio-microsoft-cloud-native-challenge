import json
import logging
import os
import pymssql
import streamlit as st
import uuid
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Storage Config
BLOB_STORAGE_CONNECTION_STRING = os.getenv("BLOB_STORAGE_CONNECTION_STRING")
BLOB_STORAGE_CONTAINER_NAME = os.getenv("BLOB_STORAGE_CONTAINER_NAME")
BLOB_STORAGE_ACCOUNT_NAME = os.getenv("BLOB_STORAGE_ACCOUNT_NAME")
BLOB_STORAGE_ENDPOINT = os.getenv("BLOB_STORAGE_ENDPOINT")

# Azure SQL Server Config
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# Page Title
st.title("Products Register - Cloud E-Commerce")

# Product Registration Form
product_name = st.text_input("Product Name")
description = st.text_area("Product Description")
price = st.number_input("Product Price", min_value=0.0, format="%.2f")
uploaded_file = st.file_uploader("Product Image", type=["png", "jpg", "jpeg"])

# Initialize Azure Blob Storage Client
blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)

try:
    blob_container_client = blob_service_client.get_container_client(BLOB_STORAGE_CONTAINER_NAME)
except Exception as error:
    blob_service_client.create_container(BLOB_STORAGE_CONTAINER_NAME, public_access="blob")

# Upload images to Azure Blob Storage
def upload_image(file):
    try:
        blob_name = f"{uuid.uuid4()}.jpg"
        blob_client = blob_container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file.read(), overwrite=True)
        image_url = f"{BLOB_STORAGE_ENDPOINT}/{BLOB_STORAGE_CONTAINER_NAME}/{blob_name}"
        return image_url
    except Exception as error:
        logging.error(error)
        st.error(f"Failed to upload image: {error}")
        return None

# Insert products into Azure SQL Server
def insert_product_sql(product_data):
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME,
                               password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO dbo.products (name, description, price, image_url)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(insert_query, (product_data["name"], product_data["description"], product_data["price"], product_data["image_url"]))
        conn.commit()

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir no Azure SQL: {e}")
        return False

# List products from Azure SQL Server
def list_products_sql():
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME,
                               password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor(as_dict=True)
        query = "SELECT id, name, description, price, image_url FROM dbo.products"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []

# Display products in the page
def list_products_screen():
    products = list_products_sql()
    if products:
        cards_per_line = 3
        cols = st.columns(cards_per_line)
        for i, product in enumerate(products):
            col = cols[i % cards_per_line]
            with col:
                st.markdown(f"### {product['name']}")
                st.write(f"**description:** {product['description']}")
                st.write(f"**price:** R$ {product['price']:.2f}")
                if product["image_url"]:
                    html_img = f'<img src="{product["image_url"]}" width="200" height="200" alt="Imagem do produto">'
                    st.markdown(html_img, unsafe_allow_html=True)
                st.markdown("---")
            if (i + 1) % cards_per_line == 0 and (i + 1) < len(products):
                cols = st.columns(cards_per_line)
    else:
        st.info("No producst found.")

if st.button("Register Product"):
    if not product_name or not description or price is None:
        st.warning("Fill in all required fields.")
    else:
        image_url = ""
        if uploaded_file is not None:
            image_url = upload_image(uploaded_file)

        product_data = {
            "name": product_name,
            "description": description,
            "price": price,
            "image_url": image_url
        }

        if insert_product_sql(product_data):
            st.success("Product successfully registered!")
        else:
            st.error("Failed to register the product.")

        products_file = "products.json"
        products = []

        if not os.path.exists(products_file):
            with open(products_file, "w", encoding="utf-8") as fd:
                products.append(product_data)
                fd.write(json.dumps(products, ensure_ascii=False, indent=4))
        else:
            with open(products_file, "r+", encoding="utf-8") as fd:
                products = json.loads(fd.read())
                products.append(product_data)
                fd.seek(0)
                fd.truncate()
                fd.write(json.dumps(products, ensure_ascii=False, indent=4))

        st.json(product_data)

st.header("Products List")
list_products_screen()
