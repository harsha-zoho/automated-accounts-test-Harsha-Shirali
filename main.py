import sqlite3
import os
from mindee import Client, PredictResponse, product
from PIL import Image
from pdf2image import convert_from_path

from dotenv import load_dotenv
load_dotenv()
MINDEE_API_KEY = os.getenv("MINDEE_API_KEY")

if not MINDEE_API_KEY:
    raise ValueError("MINDEE_API_KEY environment variable not set. Please get one from mindee.com and set it.")

DATABASE_NAME = 'receipts.db'

def setup_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_name TEXT,
            purchased_at TEXT,
            total_amount REAL,
            currency TEXT,
            receipt_type TEXT,
            file_name TEXT,
            raw_data TEXT -- To store the full JSON response from Mindee
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS line_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER,
            description TEXT,
            quantity REAL,
            unit_price REAL,
            total_price REAL,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' set up successfully.")

def extract_receipt_data(file_path):
    mindee_client = Client(api_key=MINDEE_API_KEY)
    
    try:
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            if not images:
                print(f"Could not convert PDF: {file_path} to images.")
                return None
            input_doc = mindee_client.source_from_bytes(images[0].tobytes(), filename=os.path.basename(file_path))
        else:
            input_doc = mindee_client.source_from_path(file_path)

        result: PredictResponse = mindee_client.parse(product.ReceiptV5, input_doc)
        
        receipt = result.document.inference.prediction
        
        extracted_data = {
            'merchant_name': receipt.supplier_name.value if receipt.supplier_name else None,
            'purchased_at': receipt.date.value if receipt.date else None,
            'total_amount': receipt.total_amount.value if receipt.total_amount else None,
            'currency': receipt.locale.currency if receipt.locale and receipt.locale.currency else None,
            'receipt_type': receipt.receipt_type.value if receipt.receipt_type else None,
            'line_items': [],
            'raw_data': result.to_json() # Store the full JSON for debugging/future use
        }

        if receipt.line_items:
            for item in receipt.line_items:
                extracted_data['line_items'].append({
                    'description': item.description if item.description else None,
                    'quantity': item.quantity if item.quantity else None,
                    'unit_price': item.unit_price if item.unit_price else None,
                    'total_price': item.total_amount if item.total_amount else None,
                })
        
        print(f"Successfully extracted data from {os.path.basename(file_path)}")
        return extracted_data

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def store_data_in_db(extracted_data, file_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO receipts (merchant_name, purchased_at, total_amount, currency, receipt_type, file_name, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            extracted_data['merchant_name'],
            extracted_data['purchased_at'],
            extracted_data['total_amount'],
            extracted_data['currency'],
            extracted_data['receipt_type'],
            file_name,
            str(extracted_data['raw_data'])
        ))
        receipt_id = cursor.lastrowid
