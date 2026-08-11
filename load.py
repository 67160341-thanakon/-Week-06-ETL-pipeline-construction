import os
import sqlite3
import pandas as pd

def load_data(transformed_data, db_path="data/warehouse/warehouse.db"):
    # 1. สร้างโฟลเดอร์สำหรับเก็บฐานข้อมูลหากยังไม่มี
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # 2. เตรียมข้อมูล dim_customer
    customers_df = transformed_data["customers"][[
        "customer_id", "name", "province", "email"
    ]].copy()
    
    # 3. เตรียมข้อมูล dim_product
    products_df = transformed_data["products"][[
        "product_id", "product_name", "category", "price"
    ]].copy()
    
    # 4. เตรียมข้อมูล fact_sales
    sales_df = transformed_data["transformed_orders"][[
        "order_id", "customer_id", "product_id", "order_date", 
        "qty", "unit_price", "discount_pct", "sales_amount"
    ]].copy()
    
    # 5. บันทึกลง SQLite (ใช้ if_exists="replace" เพื่อให้รันกี่ครั้งจำนวน record ก็เท่าเดิม)
    customers_df.to_sql("dim_customer", conn, if_exists="replace", index=False)
    products_df.to_sql("dim_product", conn, if_exists="replace", index=False)
    sales_df.to_sql("fact_sales", conn, if_exists="replace", index=False)
    
    conn.close()
