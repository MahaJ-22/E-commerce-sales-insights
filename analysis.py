import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Create folder to save charts ─────────────────────────
os.makedirs("static/charts", exist_ok=True)

# ── Load Data ─────────────────────────────────────────────
df = pd.read_csv("data.csv")

print("✅ Data loaded successfully!")
print(f"   Shape: {df.shape}")
print(f"\nColumn types before cleaning:")
print(df.dtypes)

# ══════════════════════════════════════════════════════════
# STEP 1 — DATA CLEANING
# ══════════════════════════════════════════════════════════

# Convert order_date to datetime format
df["order_date"] = pd.to_datetime(df["order_date"])

# Extract month and quarter for grouping
df["month"]   = df["order_date"].dt.to_period("M")
df["quarter"] = df["order_date"].dt.to_period("Q")

# Check for missing values
print(f"\nMissing values:")
print(df.isnull().sum())

# Standardize category names (strip whitespace)
df["product_category"] = df["product_category"].str.strip()

print(f"\n✅ Data cleaned successfully!")
print(f"\nColumn types after cleaning:")
print(df.dtypes)

# ══════════════════════════════════════════════════════════
# STEP 2 — KEY METRICS / KPIs
# ══════════════════════════════════════════════════════════

total_sales       = round(df["total_price"].sum(), 2)
total_orders      = len(df)
avg_order_value   = round(df["total_price"].mean(), 2)
unique_customers  = df["customer_id"].nunique()

print("\n" + "="*45)
print("         KEY PERFORMANCE INDICATORS")
print("="*45)
print(f"  Total Sales        : $ {total_sales:,.2f}")
print(f"  Total Orders       : {total_orders}")
print(f"  Avg Order Value    : $ {avg_order_value:,.2f}")
print(f"  Unique Customers   : {unique_customers}")
print("="*45)

# ══════════════════════════════════════════════════════════
# STEP 3 — EXPLORATORY DATA ANALYSIS & CHARTS
# ══════════════════════════════════════════════════════════

sns.set_theme(style="whitegrid")

# ── Chart 1: Monthly Sales Trend ─────────────────────────
monthly_sales = (
    df.groupby("month")["total_price"]
    .sum()
    .reset_index()
)
monthly_sales["month"] = monthly_sales["month"].astype(str)

plt.figure(figsize=(12, 5))
sns.lineplot(data=monthly_sales, x="month", y="total_price",
             marker="o", color="#4F46E5", linewidth=2.5)
plt.title("Monthly Sales Trend (2023)", fontsize=16, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Total Sales ($)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("static/charts/monthly_sales.png", dpi=150)
plt.close()
print("\n✅ Chart 1 saved: Monthly Sales Trend")

# ── Chart 2: Sales by Category ───────────────────────────
category_sales = (
    df.groupby("product_category")["total_price"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

plt.figure(figsize=(10, 5))
sns.barplot(data=category_sales, x="product_category", y="total_price",
            palette="viridis")
plt.title("Total Sales by Category (2023)", fontsize=16, fontweight="bold")
plt.xlabel("Category")
plt.ylabel("Total Sales ($)")
plt.tight_layout()
plt.savefig("static/charts/category_sales.png", dpi=150)
plt.close()
print("✅ Chart 2 saved: Sales by Category")

# ── Chart 3: Top 10 Products ─────────────────────────────
top_products = (
    df.groupby("product_name")["total_price"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

plt.figure(figsize=(12, 6))
sns.barplot(data=top_products, x="total_price", y="product_name",
            palette="magma")
plt.title("Top 10 Products by Revenue (2023)", fontsize=16, fontweight="bold")
plt.xlabel("Total Sales ($)")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig("static/charts/top_products.png", dpi=150)
plt.close()
print("✅ Chart 3 saved: Top 10 Products")

# ── Chart 4: Quarterly Sales ──────────────────────────────
quarterly_sales = (
    df.groupby("quarter")["total_price"]
    .sum()
    .reset_index()
)
quarterly_sales["quarter"] = quarterly_sales["quarter"].astype(str)

plt.figure(figsize=(8, 5))
sns.barplot(data=quarterly_sales, x="quarter", y="total_price",
            palette="Blues_d")
plt.title("Quarterly Sales (2023)", fontsize=16, fontweight="bold")
plt.xlabel("Quarter")
plt.ylabel("Total Sales ($)")
plt.tight_layout()
plt.savefig("static/charts/quarterly_sales.png", dpi=150)
plt.close()
print("✅ Chart 4 saved: Quarterly Sales")

# ── Chart 5: Customer Purchase Frequency ─────────────────
customer_orders = df.groupby("customer_id")["order_id"].count()

plt.figure(figsize=(10, 5))
sns.histplot(customer_orders, bins=20, color="#F59E0B", kde=True)
plt.title("Customer Purchase Frequency (2023)", fontsize=16, fontweight="bold")
plt.xlabel("Number of Orders per Customer")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig("static/charts/customer_frequency.png", dpi=150)
plt.close()
print("✅ Chart 5 saved: Customer Frequency")

print("\n✅ All analysis complete! Charts saved to static/charts/")
print("\nSummary of monthly sales:")
print(monthly_sales.to_string(index=False))