"""
Database Schemas for Drago Decor

Each Pydantic model below represents a MongoDB collection. The collection
name is the lowercase class name (e.g., Product -> "product").
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl

# ---------- Core Domain ----------

class Category(BaseModel):
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Category description")
    hero_image: Optional[HttpUrl] = Field(None, description="Category image URL")

class ProductVariant(BaseModel):
    color_name: str = Field(..., description="Variant color name")
    hex: str = Field(..., description="HEX color (e.g., #AABBCC)")
    finish: Literal["opaco", "seta", "lucido", "satinato", "opaco-prof"] = Field(
        "opaco", description="Finitura"
    )
    stock: int = Field(0, ge=0, description="Disponibilità in magazzino")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: str = Field(..., description="Technical description")
    category: str = Field(..., description="Category slug")
    usage: Literal["interno", "esterno", "entrambi"] = Field("interno")
    base_price: float = Field(..., ge=0, description="Base price")
    variants: List[ProductVariant] = Field(default_factory=list)
    tech_sheet_url: Optional[HttpUrl] = Field(None, description="Scheda tecnica URL")
    images: List[HttpUrl] = Field(default_factory=list)

class Review(BaseModel):
    product_id: str = Field(..., description="Product _id string")
    rating: int = Field(..., ge=1, le=5)
    author: str = Field(...)
    comment: Optional[str] = Field(None)

# ---------- Commerce ----------

class CartItem(BaseModel):
    product_id: str
    variant_hex: Optional[str] = None
    quantity: int = Field(1, ge=1)
    unit_price: float = Field(..., ge=0)

class Order(BaseModel):
    user_email: str
    items: List[CartItem]
    total: float = Field(..., ge=0)
    status: Literal["pending", "paid", "shipped"] = "pending"

# ---------- Content ----------

class BlogPost(BaseModel):
    title: str
    slug: str
    content: str
    cover: Optional[HttpUrl] = None
    tags: List[str] = Field(default_factory=list)

class ContactMessage(BaseModel):
    name: str
    email: str
    message: str

# ---------- Professionals ----------

class Professional(BaseModel):
    business_name: str
    vat: Optional[str] = None
    email: str
    tier: Literal["standard", "pro", "elite"] = "standard"
