import logging
import os
from src.extract import extract_data
from src.transform import transform_data
from src.load import load_data
from src.validate import validate_data

def run_pipeline():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # ล้าง Handler เก่าออกเพื่อป้องกัน Duplicate Logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(
        filename="logs/etl.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
    
    logging.info("เริ่มการทำงานของ ETL Pipeline...")
    try:
        raw_data = extract_data()
        logging.info("การดึงข้อมูล (Extract) สำเร็จ")
        
        transformed_data = transform_data(raw_data)
        logging.info("การแปลงและทำความสะอาดข้อมูล (Transform) สำเร็จ")
        
        load_data(transformed_data)
        logging.info("การนำข้อมูลเข้าคลัง (Load) สำเร็จ")
        
        val_summary = validate_data(transformed_data)
        logging.info(f"การตรวจสอบข้อมูล (Validate) เสร็จสิ้น ผลลัพธ์: {val_summary['status']}")
        
        print("ETL Pipeline Executed Successfully!")
        print("Validation Result:", val_summary)
    except Exception as e:
        logging.error(f"เกิดข้อผิดพลาดในการทำงานของ ETL Pipeline: {str(e)}")
        raise e

if __name__ == "__main__":
    run_pipeline()
