# Task 6: FastAPI Assignment
from fastapi import FastAPI

# 1. Initialize the FastAPI app
app = FastAPI()

# 2. This is the products list (starting with 4, then adding IDs 5, 6, and 7)
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 15000, "category": "Electronics", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 299, "category": "Electronics", "in_stock": True},
    
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
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
    
# --- NEW TASK 2 CODE BELOW ---

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
    
# --- TASK 3: SHOW ONLY IN-STOCK PRODUCTS ---

@app.get("/products/instock")
def get_instock():
    # 1. Filter the list to include ONLY products where "in_stock" is True
    available = [p for p in products if p["in_stock"] == True]
    
    # 2. Return the required structure: a list and a count
    return {
        "in_stock_products": available,
        "count": len(available)
    }
    
# --- TASK 4: STORE SUMMARY ENDPOINT ---

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
    
# --- TASK 5: SEARCH PRODUCTS BY NAME (CASE-INSENSITIVE) ---

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
    
# --- BONUS TASK: CHEAPEST & MOST EXPENSIVE ---

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
