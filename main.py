import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Optional
from io import BytesIO

from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import Product, Category, Review, BlogPost, ContactMessage, Order, Professional

app = FastAPI(title="Drago Decor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"brand": "Drago Decor", "status": "ok"}

# --------- Catalog Endpoints ---------

@app.get("/api/categories")
def list_categories():
    return get_documents("category", {}, 50)

@app.post("/api/categories")
def create_category(category: Category):
    _id = create_document("category", category)
    return {"id": _id}

@app.get("/api/products")
def list_products(
    category: Optional[str] = None,
    color: Optional[str] = None,
    finish: Optional[str] = None,
    usage: Optional[str] = None,
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 50,
):
    flt = {}
    if category:
        flt["category"] = category
    if usage:
        flt["usage"] = usage
    # Text search simulation
    if q:
        flt["title"] = {"$regex": q, "$options": "i"}
    if color:
        flt["variants.hex"] = color
    if finish:
        flt["variants.finish"] = finish
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        flt["base_price"] = price_filter

    return get_documents("product", flt, limit)

@app.post("/api/products")
def create_product(product: Product):
    _id = create_document("product", product)
    return {"id": _id}

@app.get("/api/reviews/{product_id}")
def get_reviews(product_id: str):
    return get_documents("review", {"product_id": product_id}, 100)

@app.post("/api/reviews")
def create_review(review: Review):
    _id = create_document("review", review)
    return {"id": _id}

# --------- Commerce ---------

@app.post("/api/orders")
def create_order(order: Order):
    _id = create_document("order", order)
    return {"id": _id}

# --------- Content ---------

@app.get("/api/blog")
def list_blog(limit: int = 20):
    return get_documents("blogpost", {}, limit)

@app.post("/api/blog")
def create_blog(post: BlogPost):
    _id = create_document("blogpost", post)
    return {"id": _id}

@app.post("/api/contact")
def contact(msg: ContactMessage):
    _id = create_document("contactmessage", msg)
    return {"id": _id, "status": "received"}

# --------- Professionals ---------

@app.get("/api/professionals")
def list_professionals(limit: int = 50):
    return get_documents("professional", {}, limit)

@app.post("/api/professionals")
def create_professional(pro: Professional):
    _id = create_document("professional", pro)
    return {"id": _id}

# --------- Utilities ---------

class CoverageRequest(BaseModel):
    mq: float
    mano: int = 2
    resa_mq_litro: float = 10.0  # default average coverage

@app.post("/api/coverage")
def coverage(data: CoverageRequest):
    litri = (data.mq * data.mano) / max(0.1, data.resa_mq_litro)
    return {"litri": round(litri, 2)}

# --------- Color Visualizer (simplified mock) ---------

@app.post("/api/visualizer/apply")
async def apply_color(
    image: UploadFile = File(...),
    color: Optional[str] = Query(None),
    finish: Optional[str] = Query(None),
):
    # For demo purposes, we just return the uploaded image as-is
    # In a real implementation, you'd segment walls and apply color mapping.
    data = await image.read()
    buffer = BytesIO(data)
    return StreamingResponse(buffer, media_type=image.content_type)

@app.get("/api/visualizer/complementary")
def complementary(color: str):
    # compute complementary HEX
    if not color.startswith("#") or len(color) != 7:
        raise HTTPException(400, detail="Formato colore non valido. Usa HEX #RRGGBB")
    r = 255 - int(color[1:3], 16)
    g = 255 - int(color[3:5], 16)
    b = 255 - int(color[5:7], 16)
    comp = f"#{r:02X}{g:02X}{b:02X}"
    # simple palette suggestions
    triad = [comp, f"#{r:02X}{b:02X}{g:02X}", f"#{g:02X}{r:02X}{b:02X}"]
    return {"complementary": comp, "suggestions": triad}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
