from flask import Blueprint, request, jsonify
from db_config import get_db_connection

search_bp = Blueprint('search_bp', __name__)

# 🔍 Tìm kiếm món ăn theo tên
@search_bp.route('/monan', methods=['GET'])
def search_monan():
    keyword = request.args.get('keyword', '')
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM monan WHERE TenMonAn LIKE %s", (f"%{keyword}%",))
    results = cursor.fetchall()
    db.close()
    return jsonify(results)

# 🔍 Tìm kiếm khách hàng theo tên hoặc số điện thoại
@search_bp.route('/khachhang', methods=['GET'])
def search_khachhang():
    keyword = request.args.get('keyword', '')
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM khachhang
        WHERE HoTenKhachHang LIKE %s OR SoDienThoai LIKE %s
    """, (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    db.close()
    return jsonify(results)

# 🔍 Tìm kiếm hóa đơn theo tên khách hàng
@search_bp.route('/hoadon', methods=['GET'])
def search_hoadon():
    keyword = request.args.get('keyword', '')
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM hoadon
        WHERE HoTenKhachHang LIKE %s
    """, (f"%{keyword}%",))
    results = cursor.fetchall()
    db.close()
    return jsonify(results)
