from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import math

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: int
    category: str
    in_stock: bool

class Order(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    customer_name: str

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

orders = []
order_counter = 1


@app.get("/products")
def get_products():
    return products


@app.post("/orders")
def create_order(order: Order):
    global order_counter
    order.order_id = order_counter
    order_counter += 1
    orders.append(order.dict())
    return order


@app.get("/products/search")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p["name"].lower()]
    if not result:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(result), "products": result}


@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):
    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False

    sorted_list = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_list
    }


@app.get("/products/page")
def paginate_products(
    page: int = 1,
    limit: int = 2
):
    total = len(products)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    paginated = products[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_products": total,
        "total_pages": total_pages,
        "products": paginated
    }


@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    if not result:
        return {"message": f"No orders found for: {customer_name}"}
    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }

@app.get("/products/{product_id}")
@app.get("/products/sort-by-category")
def sort_by_category():
    sorted_list = sorted(products, key=lambda x: (x["category"], x["price"]))
    return sorted_list

@app.get("/products/{product_id}")
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = products.copy()

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    total = len(result)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "products": paginated
    }

@app.get("/products/{product_id}")
@app.get("/orders/page")
def paginate_orders(
    page: int = 1,
    limit: int = 3
):
    total = len(orders)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    paginated = orders[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_orders": total,
        "total_pages": total_pages,
        "orders": paginated
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")