import pandas as pd
import random
from datetime import datetime, timedelta

# ── Settings ────────────────────────────────────────────
NUM_ORDERS = 1200
random.seed(42)

# ── Reference Data ───────────────────────────────────────
categories = {
    "Electronics":  {"products": ["Laptop", "Smartphone", "Headphones", "Tablet", "Smartwatch"],
                     "price_range": (200, 1500)},
    "Clothing":     {"products": ["T-Shirt", "Jeans", "Jacket", "Dress", "Sneakers"],
                     "price_range": (20, 200)},
    "Home & Kitchen":{"products": ["Blender", "Coffee Maker", "Vacuum", "Cookware Set", "Lamp"],
                     "price_range": (30, 300)},
    "Books":        {"products": ["Fiction Novel", "Self-Help Book", "Textbook", "Comic Book", "Biography"],
                     "price_range": (10, 80)},
    "Sports":       {"products": ["Yoga Mat", "Dumbbells", "Running Shoes", "Cycling Helmet", "Water Bottle"],
                     "price_range": (15, 250)},
}

# ── Generate Orders ──────────────────────────────────────
start_date = datetime(2023, 1, 1)
end_date   = datetime(2023, 12, 31)

rows = []
for order_id in range(1001, 1001 + NUM_ORDERS):
    # Random date in 2023
    random_days = random.randint(0, (end_date - start_date).days)
    order_date  = start_date + timedelta(days=random_days)

    # Random category and product
    category        = random.choice(list(categories.keys()))
    product_info    = categories[category]
    product_name    = random.choice(product_info["products"])
    min_p, max_p    = product_info["price_range"]
    unit_price      = round(random.uniform(min_p, max_p), 2)
    quantity        = random.randint(1, 5)
    total_price     = round(unit_price * quantity, 2)

    rows.append({
        "order_id":         order_id,
        "customer_id":      f"CUST{random.randint(1, 300):04d}",
        "product_id":       f"PROD{random.randint(1, 50):03d}",
        "order_date":       order_date.strftime("%Y-%m-%d"),
        "product_name":     product_name,
        "product_category": category,
        "quantity":         quantity,
        "unit_price":       unit_price,
        "total_price":      total_price,
    })

# ── Save to CSV ──────────────────────────────────────────
df = pd.DataFrame(rows)
df.to_csv("data.csv", index=False)

print(f"✅ Dataset created successfully!")
print(f"   Total orders : {len(df)}")
print(f"   Date range   : {df['order_date'].min()} to {df['order_date'].max()}")
print(f"   Categories   : {df['product_category'].nunique()}")
print(f"   Unique customers : {df['customer_id'].nunique()}")
print(f"\nFirst 5 rows:")
print(df.head())