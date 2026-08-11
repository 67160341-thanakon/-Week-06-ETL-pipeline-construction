import os
import pandas as pd

def transform_data(raw):
    customers = raw["customers"].copy()
    orders = raw["orders"].copy()
    products = raw["products"].copy()

    # -------------------------------------------------------------
    # 1. Transform Customers
    # -------------------------------------------------------------
    # ลบข้อมูลซ้ำ customer_id
    customers = customers.drop_duplicates(subset=["customer_id"])
    
    # Standardize province และจัดการ missing values
    customers["province"] = customers["province"].fillna("Unknown").astype(str).str.strip().str.title()
    customers = customers.fillna("Unknown")

    # -------------------------------------------------------------
    # 2. Transform Products
    # -------------------------------------------------------------
    # เปลี่ยนชื่อ column ให้ใช้ง่าย
    col_map = {
        "category.name": "category",
        "pricing.price": "price"
    }
    products = products.rename(columns=col_map)
    
    # แปลง price เป็น numeric
    if "price" in products.columns:
        products["price"] = pd.to_numeric(
            products["price"].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce"
        )
    
    # missing category -> "Unknown"
    if "category" in products.columns:
        products["category"] = products["category"].fillna("Unknown")
    products = products.fillna("Unknown")

    # -------------------------------------------------------------
    # 3. Transform Orders & Check Reject Conditions
    # -------------------------------------------------------------
    # ลบข้อมูลซ้ำ order_id
    orders = orders.drop_duplicates(subset=["order_id"])

    # Parse mixed date formats
    orders["parsed_date"] = pd.to_datetime(orders["order_date"], format="mixed", errors="coerce")

    # Standardize status เป็น lowercase
    orders["status"] = orders["status"].astype(str).str.strip().str.lower()

    # กฎการ Reject ข้อมูล (Business Rules)
    cond_qty = orders["qty"] <= 0
    cond_price = orders["unit_price"] <= 0
    cond_discount = (orders["discount_pct"] < 0) | (orders["discount_pct"] > 100)
    cond_date = orders["parsed_date"].isna()

    # ตรวจสอบว่ามีอยู่ใน Master Data หรือไม่ (Customers & Products)
    valid_cust_ids = set(customers["customer_id"])
    valid_prod_ids = set(products["product_id"])
    cond_no_cust = ~orders["customer_id"].isin(valid_cust_ids)
    cond_no_prod = ~orders["product_id"].isin(valid_prod_ids)

    # กรองเฉพาะ status ที่เป็น paid หรือ completed
    cond_invalid_status = ~orders["status"].isin(["paid", "completed"])

    # รวมเงื่อนไข Reject ทั้งหมด
    reject_mask = cond_qty | cond_price | cond_discount | cond_date | cond_no_cust | cond_no_prod | cond_invalid_status

    # แยกชุดข้อมูล Reject และ Valid
    rejects_df = orders[reject_mask].copy()
    valid_orders = orders[~reject_mask].copy()

    # บันทึกไฟล์ output/rejects.csv
    os.makedirs("output", exist_ok=True)
    rejects_df.drop(columns=["parsed_date"], errors="ignore").to_csv("output/rejects.csv", index=False)

    # -------------------------------------------------------------
    # 4. Merge Data & Calculations
    # -------------------------------------------------------------
    # ฟอร์แมตวันที่ให้ถูกต้อง
    valid_orders["order_date"] = valid_orders["parsed_date"].dt.strftime("%Y-%m-%d")
    valid_orders = valid_orders.drop(columns=["parsed_date"])

    # Join orders + customers + products
    merged_df = valid_orders.merge(customers, on="customer_id", how="left")
    merged_df = merged_df.merge(products, on="product_id", how="left")

    # คำนวณยอดเงิน
    merged_df["gross_amount"] = merged_df["qty"] * merged_df["unit_price"]
    merged_df["discount_amount"] = merged_df["gross_amount"] * merged_df["discount_pct"] / 100.0
    merged_df["sales_amount"] = merged_df["gross_amount"] - merged_df["discount_amount"]

    return {
        "transformed_orders": merged_df,
        "rejects": rejects_df,
        "customers": customers,
        "products": products
    }
