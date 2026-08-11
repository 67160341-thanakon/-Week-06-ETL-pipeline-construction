import json
import sqlite3
import pandas as pd

def extract_data(
    customers_path="customers.csv",
    orders_path="orders.csv",
    products_path="products.json",
    db_path="store.db"
):
    # อ่านไฟล์ CSV
    customers = pd.read_csv(customers_path)
    orders = pd.read_csv(orders_path)

    # อ่านไฟล์ JSON และ flatten ด้วย pd.json_normalize()
    with open(products_path, "r", encoding="utf-8") as f:
        products_json = json.load(f)
    products = pd.json_normalize(products_json)

    # อ่านตาราง stores จาก SQLite
    conn = sqlite3.connect(db_path)
    stores = pd.read_sql_query("SELECT * FROM stores", conn)
    conn.close()

    return {
        "customers": customers,
        "orders": orders,
        "products": products,
        "stores": stores
    }
