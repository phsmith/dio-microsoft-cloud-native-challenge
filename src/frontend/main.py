import json
import logging
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("STREAMLIT_API_URL")

# Page Title
st.title("Cloud E-Commerce")
st.header("Product Register")

# Product Registration Form
product_name = st.text_input("Product Name")
description = st.text_area("Product Description")
price = st.number_input("Product Price", min_value=0.0, format="%.2f")
uploaded_file = st.file_uploader("Product Image", type=["png", "jpg", "jpeg"])


# Display products in the page
def producst_list():
    products = []

    try:
        products = requests.get(f"{API_URL}/products").json()
    except Exception as error:
        logging.error(error)

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
                    st.html(f'<a href="{product["image_url"]}" target="_blank"><img src="{product["image_url"]}" alt="Product Image" style="border-radius: 10px; width: 100%; height: 300px;"></a>')
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
            image_upload = requests.post(
                f"{API_URL}/image/upload", files={"file": uploaded_file.getvalue()})

            if image_upload.status_code != 200:
                st.error(image_upload.json().get("detail"))
                st.stop()

            image_url = image_upload.json().get("image_url")

        product_data = [{
            "name": product_name,
            "description": description,
            "price": price,
            "image_url": image_url
        }]

        add_product = requests.post(f"{API_URL}/products", json=product_data)

        if add_product.status_code != 200:
            st.error(add_product.json().get("detail"))
            st.stop()

        st.success(add_product.json().get("message"))

st.header("Products List")
producst_list()
