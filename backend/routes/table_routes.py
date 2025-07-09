from flask import Blueprint, request, jsonify
from db_config import get_db_connection

table_bp = Blueprint('table_bp', __name__)

# 📋 Lấy danh sách tất cả bàn ăn
@table_bp.route('/', methods=['GET'])
def get_all_tables():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT BanAnID, SoBan, TrangThai FROM banan ORDER BY SoBan")
    tables = cursor.fetchall()
    db.close()
    return jsonify(tables)

# ➕ Thêm bàn mới
@table_bp.route('/', methods=['POST'])
def add_table():
    data = request.json
    so_ban = data.get('SoBan')
    trang_thai = data.get('TrangThai')

    if so_ban is None or not trang_thai:
        return jsonify({'message': 'Thiếu thông tin'}), 400

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO banan (SoBan, TrangThai)
        VALUES (%s, %s)
    """, (so_ban, trang_thai))

    db.commit()
    db.close()
    return jsonify({'message': 'Thêm bàn thành công'}), 201

# ✏️ Cập nhật trạng thái bàn ăn (VD: từ \"Trống\" sang \"Đang có khách\")
@table_bp.route('/<int:ban_an_id>', methods=['PUT'])
def update_table_status(ban_an_id):
    data = request.json
    trang_thai = data.get('TrangThai')

    if not trang_thai:
        return jsonify({'message': 'Thiếu trạng thái'}), 400

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE banan SET TrangThai = %s WHERE BanAnID = %s
    """, (trang_thai, ban_an_id))

    db.commit()
    db.close()
    return jsonify({'message': 'Cập nhật trạng thái thành công'})

# ❌ Xóa bàn ăn
@table_bp.route('/<int:ban_an_id>', methods=['DELETE'])
def delete_table(ban_an_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM banan WHERE BanAnID = %s", (ban_an_id,))
    db.commit()
    db.close()
    return jsonify({'message': 'Xóa bàn thành công'})
