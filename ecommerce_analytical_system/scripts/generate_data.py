import csv
import random
from datetime import datetime, timedelta
import string

# Constants
NUM_ORDERS = 500
NUM_CUSTOMERS = 100
NUM_PRODUCTS = 50
NUM_ORDER_ITEMS = 800

# Lists for random data
FIRST_NAMES = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
CATEGORIES = ["Electronics", "Clothing", "Home", "Books"]
SUBCATEGORIES = {
    "Electronics": ["Phones", "Laptops", "Tablets"],
    "Clothing": ["Men", "Women", "Kids"],
    "Home": ["Kitchen", "Furniture", "Decor"],
    "Books": ["Fiction", "Non-Fiction", "Educational"]
}
PRODUCT_NAMES = ["Laptop", "Phone", "Shirt", "Desk", "Novel", "Monitor", "Keyboard", "Backpack", "Lamp", "Headphones"]
STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
REGIONS = ["US", "EU", "ASIA", "LATAM"]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]

def generate_customers():
    """Generate customers.csv"""
    customers = []
    for i in range(NUM_CUSTOMERS):
        customer_id = f"CUST{i+1:04d}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        # 2% invalid emails
        if random.random() < 0.02:
            if random.random() < 0.5:
                email = f"{name.replace(' ', '').lower()}{random.randint(1000, 9999)}"  # Missing @ 
            else:
                email = f"{name.replace(' ', '').lower()}@{random.randint(1000, 9999)}"  # Missing domain
        else:
            email = f"{name.replace(' ', '').lower()}{random.randint(1000, 9999)}@email.com"
        
        reg_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
        customer_type = random.choice(CUSTOMER_TYPES)
        customers.append([customer_id, name, email, reg_date, customer_type])
    
    with open("customers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "customer_name", "email", "registration_date", "customer_type"])
        writer.writerows(customers)
    
    return customers

def generate_products():
    """Generate products.csv"""
    products = []
    product_ids = []
    for i in range(NUM_PRODUCTS):
        product_id = f"PROD{i+1:04d}"
        product_ids.append(product_id)
        category = random.choice(CATEGORIES)
        subcategory = random.choice(SUBCATEGORIES[category])
        
        # Some product names with extra spaces or mixed case
        base_name = f"{random.choice(PRODUCT_NAMES)} {category}"
        if random.random() < 0.1:
            product_name = f"  {base_name}  ".title() if random.random() < 0.5 else base_name.lower()
        else:
            product_name = base_name.title()
        
        cost_price = round(random.uniform(10, 500), 2)
        products.append([product_id, product_name, category, subcategory, cost_price])
    
    with open("products.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category", "subcategory", "cost_price"])
        writer.writerows(products)
    
    return products, product_ids

def generate_orders(customers, products):
    """Generate orders.csv"""
    orders = []
    order_ids = []
    for i in range(NUM_ORDERS):
        order_id = f"ORD{i+1:05d}"
        order_ids.append(order_id)
        
        # 5% NULL customer_id
        if random.random() < 0.05:
            customer_id = ""
        else:
            customer_id = random.choice(customers)[0]
        
        # Some dates in wrong format (DD-MM-YYYY) or correct format
        base_date = datetime.now() - timedelta(days=random.randint(0, 365))
        if random.random() < 0.08:
            order_date = base_date.strftime("%d-%m-%Y %H:%M:%S")  # Wrong format
        else:
            order_date = base_date.strftime("%Y-%m-%d %H:%M:%S")  # Correct format
        
        status = random.choice(STATUSES)
        region_code = random.choice(REGIONS)
        
        orders.append([order_id, customer_id, order_date, status, region_code])
    
    with open("orders.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "customer_id", "order_date", "status", "region_code"])
        writer.writerows(orders)
    
    return orders, order_ids

def generate_order_items(order_ids, product_ids):
    """Generate order_items.csv"""
    order_items = []
    item_id = 1
    for i in range(NUM_ORDER_ITEMS):
        item_id_str = f"ITEM{item_id:06d}"
        item_id += 1
        
        order_id = random.choice(order_ids)
        product_id = random.choice(product_ids)
        
        # 3% negative quantity (returns)
        if random.random() < 0.03:
            quantity = random.randint(-5, -1)
        else:
            quantity = random.randint(1, 10)
        
        unit_price = round(random.uniform(5, 500), 2)
        discount_percent = random.randint(0, 50)  # 0-50% discount (valid range)
        
        order_items.append([item_id_str, order_id, product_id, quantity, unit_price, discount_percent])
    
    with open("order_items.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])
        writer.writerows(order_items)

def main():
    print("Generating customers...")
    customers = generate_customers()
    print(f"✓ Generated {len(customers)} customers")
    
    print("Generating products...")
    products, product_ids = generate_products()
    print(f"✓ Generated {len(products)} products")
    
    print("Generating orders...")
    orders, order_ids = generate_orders(customers, products)
    print(f"✓ Generated {len(orders)} orders")
    
    print("Generating order items...")
    generate_order_items(order_ids, product_ids)
    print(f"✓ Generated {NUM_ORDER_ITEMS} order items")
    
    print("\n✓ All CSV files generated successfully!")
    print("Files created: customers.csv, products.csv, orders.csv, order_items.csv")

if __name__ == "__main__":
    main()
