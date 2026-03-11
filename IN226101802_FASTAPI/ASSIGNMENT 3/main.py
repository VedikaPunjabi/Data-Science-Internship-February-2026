from fastapi import FastAPI, HTTPException, status, Query
from typing import List, Optional 
from pydantic import BaseModel, Field

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_length=1) 

class NewProduct(BaseModel):
    name: str = Field(..., min_length=1)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    in_stock: bool = True
    

# 1. Initialize the FastAPI app
app = FastAPI()

feedback = []

order_history = []

# 2. This is the products list (starting with 4, then adding IDs 5, 6, and 7)
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 15000, "category": "Electronics", "in_stock": True},
    {"id": 4, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": True},
    
    {"id": 5, "name": "Laptop", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
    
    # Adding some Stationery items to test the filter
    {"id": 8, "name": "Notebook", "price": 199, "category": "Stationery", "in_stock": True},
    {"id": 9, "name": "Gel Pen", "price": 49, "category": "Stationery", "in_stock": True},
]

# 3. Create the route that shows the products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products) # This calculates the total (which will be 7)
    }

@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    # 1. Create a list of products that match the category_name
    result = [p for p in products if p["category"].lower() == category_name.lower()]
    
    # 2. Check if the list is empty
    if not result:
        return {"error": "No products found in this category"}
    
    # 3. Return the filtered results
    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }
    
@app.get("/products/instock")
def get_instock():
    # 1. Filter the list to include ONLY products where "in_stock" is True
    available = [p for p in products if p["in_stock"] == True]
    
    # 2. Return the required structure: a list and a count
    return {
        "in_stock_products": available,
        "count": len(available)
    }
    
@app.get("/store/summary")
def get_store_summary():
    # 1. Count how many are in stock
    in_stock_count = len([p for p in products if p["in_stock"]])
    
    # 2. Calculate out of stock (Total minus In-Stock)
    out_stock_count = len(products) - in_stock_count
    
    # 3. Get unique categories
    # We use set() because it automatically removes duplicate names
    unique_categories = list(set([p["category"] for p in products]))
    
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": unique_categories
    }
    
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    # 1. Search for products where the keyword is INSIDE the name
    results = [
        p for p in products 
        if keyword.lower() in p["name"].lower()
    ]
    
    # 2. Handle the "Not Found" case
    if not results:
        return {"message": "No products matched your search"}
    
    # 3. Return the results and total count
    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }
    
@app.get("/products/deals")
def get_deals():
    # 1. Find the product with the lowest price
    # key=lambda p: p["price"] tells Python to compare the "price" values
    cheapest = min(products, key=lambda p: p["price"])
    
    # 2. Find the product with the highest price
    expensive = max(products, key=lambda p: p["price"])
    
    # 3. Return them in the requested format
    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
    

@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    min_price: Optional[int] = Query(None, description="Minimum price"),
    max_price: Optional[int] = Query(None, description="Maximum price")
):
    # Start with all products
    result = products
    
    # 1. Filter by category if provided
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]
        
    # 2. Filter by minimum price if provided (the new task!)
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
        
    # 3. Filter by maximum price if provided (used in your test URLs)
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
        
    return {
        "filters_applied": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price
        },
        "results": result,
        "count": len(result)
    }
    

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    # 1. Loop through our products list to find the matching ID
    for product in products:
        if product["id"] == product_id:
            # 2. Return ONLY the name and price as a new dictionary
            return {
                "name": product["name"],
                "price": product["price"]
            }
    
    # 3. If the loop finishes without finding the ID, return the error
    return {"error": "Product not found"}



@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    # 1. Convert the Pydantic model to a dictionary and save it
    feedback.append(data.dict())
    
    # 2. Return confirmation as requested
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }
    

@app.get("/products/summary")
def get_product_summary():
    # 1. Calculate stock counts using list comprehensions
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]
    
    # 2. Find the most expensive and cheapest products
    # We use key=lambda to tell Python to compare the "price" field
    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])
    
    # 3. Get unique categories using set() to remove duplicates
    categories = list(set(p["category"] for p in products))
    
    # 4. Return the aggregated data in the requested format
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {
            "name": expensive["name"], 
            "price": expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"], 
            "price": cheapest["price"]
        },
        "categories": categories
    }
    
# --- TASK 5: INVENTORY AUDIT ---

@app.get("/products/audit")
def get_inventory_audit():
    # 1. Separate in-stock and out-of-stock items
    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]
    
    # 2. Calculate total value: (Sum of all in-stock prices) * 10
    total_stock_value = sum(p["price"] * 10 for p in in_stock_list)
    
    # 3. Find the most expensive product
    priciest = max(products, key=lambda p: p["price"])
    
    # 4. Return the summary
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }
    
# --- BONUS TASK: CATEGORY-WIDE DISCOUNT ---

@app.put("/products/discount")
def apply_category_discount(
    category: str = Query(..., description="Category to apply discount to"),
    discount_percent: int = Query(..., ge=1, le=99, description="Discount percentage (1-99)")
):
    updated_products = []
    
    # 1. Loop through all products
    for product in products:
        # 2. Check for matching category (case-insensitive)
        if product["category"].lower() == category.lower():
            # 3. Calculate new price: price * (1 - discount/100)
            old_price = product["price"]
            new_price = int(old_price * (1 - discount_percent / 100))
            
            product["price"] = new_price
            updated_products.append(product)
            
    # 4. If no products were found in that category
    if not updated_products:
        return {"message": f"No products found in the category '{category}'"}
    
    # 5. Return success summary
    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated_products),
        "updated_products": updated_products
    }
    


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    # Search for the product in the list
    product = next((p for p in products if p["id"] == product_id), None)
    
    # If not found, return 404
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0
    
    for item in order.items:
        # Search for the product in our products list
        product = next((p for p in products if p["id"] == item.product_id), None)
        
        if not product:
            failed.append({
                "product_id": item.product_id, 
                "reason": "Product not found"
            })
        elif not product["in_stock"]:
            failed.append({
                "product_id": item.product_id, 
                "reason": f"{product['name']} is out of stock"
            })
        else:
            # Calculate pricing
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })
            
    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }
    

# 1. POST /orders - New orders start as "pending"
@app.post("/orders")
def place_new_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    
    # Create the order object with a status
    new_order = {
        "order_id": len(order_history) + 1,
        "company": order.company_name,
        "items": confirmed,
        "failed": failed,
        "grand_total": grand_total,
        "status": "pending"  # Starts as pending
    }
    
    order_history.append(new_order)
    return new_order

# 2. GET /orders/{order_id} - Retrieve order by ID
@app.get("/orders/{order_id}")
def get_order_by_id(order_id: int):
    for order in order_history:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}

# 3. PATCH /orders/{order_id}/confirm - Change status to "confirmed"
@app.patch("/orders/{order_id}/confirm")
def confirm_order_status(order_id: int):
    for order in order_history:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"  # State change
            return {"message": "Order confirmed", "order": order}
            
    return {"error": "Order not found"}


# --- TASK 1: ADD 2 NEW PRODUCTS USING POST ---

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(item: NewProduct):
    # 1. Duplicate Check (Case-insensitive)
    for p in products:
        if p["name"].lower() == item.name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with name '{item.name}' already exists"
            )
    
    # 2. Auto-generate ID (e.g., current total + 1)
    if not products:
        new_id = 1
    else:
        new_id = max(p['id'] for p in products) + 1
    
    # 3. Create the dictionary and append to the list
    new_item = item.dict()
    new_item["id"] = new_id
    products.append(new_item)
    
    # 4. Return success response
    return {
        "message": "Product added",
        "product": new_item
    }
    

# --- TASK 2: UPDATE PRODUCT (PUT) ---

@app.put("/products/{product_id}")
def update_product(
    product_id: int, 
    price: Optional[int] = Query(None, gt=0), 
    in_stock: Optional[bool] = Query(None)
):
    # 1. Find the product in the list
    for product in products:
        if product["id"] == product_id:
            
            # 2. Update price if provided
            if price is not None:
                product["price"] = price
            
            # 3. Update stock status if provided
            # We use "is not None" because False is a valid value we might want to save
            if in_stock is not None:
                product["in_stock"] = in_stock
                
            return {
                "message": "Product updated successfully",
                "product": product
            }
            
    # 4. If ID doesn't exist, return 404
    raise HTTPException(status_code=404, detail="Product not found")



# --- TASK 3: DELETE A PRODUCT ---

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    # 1. Try to find the product in the list
    product = next((p for p in products if p["id"] == product_id), None)
    
    # 2. If it doesn't exist, return 404
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"error": "Product not found"}
        )
    
    # 3. Remove the product from the list
    products.remove(product)
    
    # 4. Return success message with the product name
    return {"message": f"Product '{product['name']}' deleted"}