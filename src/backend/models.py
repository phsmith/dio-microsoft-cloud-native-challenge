from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    image_id: str
    image_url: str


class Product(BaseModel):
    name: str
    description: str
    price: float
    image_url: str


class Products(BaseModel):
    products: list[Product]


class BaseResponse(BaseModel):
    message: str
