import json
import os
import sqlite3

def validate_data(transformed_data, db_path="data/warehouse/warehouse.db"):
    df_transformed = transformed_data["transformed_orders"]
    
    # 1. ตรวจสอบจำนวนและยอดขายจาก Transformed Data
    source_valid_rows = int(len(df_transformed))
    source_total_sales = float(df_transformed["sales_amount"].sum())
    
    # 2. ตรวจสอบจำนวนและยอดขายจาก Data Warehouse (SQLite)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*), SUM(sales_amount) FROM fact_sales")
    wh_row = c.fetchone()
    warehouse_rows = int(wh_row[0]) if wh_row[0] is not None else 0
    warehouse_total_sales = float(wh_row[1]) if wh_row[1] is not None else 0.0
    
    # 3. ตรวจสอบ duplicate order_id ใน fact_sales
    c.execute("SELECT COUNT(order_id) - COUNT(DISTINCT order_id) FROM fact_sales")
    dup_row = c.fetchone()
    duplicate_order_ids = int(dup_row[0]) if dup_row[0] is not None else 0
    conn.close()
    
    # 4. ประเมินผล PASS / FAIL
    is_rows_match = (source_valid_rows == warehouse_rows)
    is_sales_match = abs(source_total_sales - warehouse_total_sales) < 1e-4
    is_no_duplicates = (duplicate_order_ids == 0)
    
    status = "PASS" if (is_rows_match and is_sales_match and is_no_duplicates) else "FAIL"
    
    summary = {
        "source_valid_rows": source_valid_rows,
        "warehouse_rows": warehouse_rows,
        "duplicate_order_ids": duplicate_order_ids,
        "source_total_sales": round(source_total_sales, 2),
        "warehouse_total_sales": round(warehouse_total_sales, 2),
        "status": status
    }
    
    # บันทึกเป็นไฟล์ output/validation.json
    os.makedirs("output", exist_ok=True)
    with open("output/validation.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
        
    return summary
