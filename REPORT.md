# ETL Pipeline Summary Report

## ตอบคำถามการทำ ETL Pipeline

### 1. พบ Data Quality Problem อะไรบ้าง
- **ข้อมูลซ้ำซ้อน (Duplicates)**: พบ `customer_id` และ `order_id` ซ้ำกัน
- **ข้อมูลสูญหาย (Missing Values)**: ค่าว่างในคอลัมน์ `province` และ `category`
- **ชนิดและรูปแบบข้อมูลไม่ถูกต้อง (Data Type & Format)**: คอลัมน์ `price` มีสัญลักษณ์ที่ไม่ใช่ตัวเลข และ `order_date` มีรูปแบบวันที่ผสมกันหลายแบบ
- **ข้อมูลไม่ผ่านเงื่อนไขทางธุรกิจ (Invalid Business Rules)**: `qty` <= 0, `discount_pct` นอกช่วง 0-100%, `status` ไม่ใช่ paid/completed, และไม่พบ Foreign Key ใน Master Table

---

### 2. แก้แต่ละปัญหาอย่างไร
- **ข้อมูลซ้ำซ้อน**: ใช้ `drop_duplicates()` ลบแถวที่ซ้ำซ้อนออก
- **Missing Values & Text Cleaning**: ใช้ `fillna("Unknown")` แทนค่าว่าง และตัดสัญลักษณ์พิเศษออกจาก `price` ด้วย Regex แล้วแปลงเป็น Numeric
- **รูปแบบวันที่**: แปลงด้วย `pd.to_datetime(format="mixed")` แล้วจัดฟอร์แมตเป็น `YYYY-MM-DD`
- **ข้อมูลผิดเงื่อนไข**: คัดแยกแถวที่ไม่ผ่าน Validation (เช่น qty <= 0, status ไม่ถูกต้อง, วันที่ผิดพลาด, Key ไม่ตรง) ไปเก็บไว้ที่ `output/rejects.csv`

---

### 3. มี record ถูก reject กี่รายการ
- ถูก Reject ทั้งหมด **80 รายการ** (บันทึกอยู่ในไฟล์ `output/rejects.csv`)

---

### 4. ยอดขายรวมหลัง Transform เท่าไร
- ยอดขายรวม (`sales_amount`) หลัง Transform เท่ากับ **192,074.66 บาท** (จากรายการขายที่สมบูรณ์ 100 รายการ)

---

### 5. เมื่อลอง run pipeline ซ้ำ fact_sales เพิ่มหรือไม่ เพราะอะไร
- **ไม่เพิ่ม** (จำนวน Record ในตาราง `fact_sales` ยังคงเท่าเดิมที่ 100 รายการ)
- **เพราะ**: ในขั้นตอน Load มีการทำ **Idempotency** โดยใช้ `if_exists="replace"` ของ pandas `.to_sql()` ซึ่งจะทำการเขียนทับตารางเดิมเสมอ ทำให้ข้อมูลไม่เกิดการเพิ่มซ้ำจากการรันหลายครั้ง
