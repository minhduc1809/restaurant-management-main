# File: backend/core/database.py

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='lethithao082006',       
        database='restaurant_db'          
    )

# Kiểm tra kết nối nếu chạy trực tiếp
if __name__ == "__main__":
    try:
        conn = get_db_connection()
        if conn.is_connected():
            print("✅ Kết nối đến medical_system thành công!")
        else:
            print("❌ Không thể kết nối đến MySQL.")
    except mysql.connector.Error as err:
        print(f"❌ Lỗi khi kết nối: {err}")