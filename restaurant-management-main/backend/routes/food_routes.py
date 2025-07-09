# ✅ food_routes.py (Sửa theo cấu trúc CSDL KHÔNG có Mô tả và Hình ảnh)
from flask import Blueprint, request, jsonify
from db_config import get_db_connection

food_bp = Blueprint('food_bp', __name__)

@food_bp.route('/', methods=['GET'])
def get_all_foods():
    ten_mon = request.args.get('search')
    loai = request.args.get('loai')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM monan WHERE 1=1"
    params = []

    if ten_mon:
        query += " AND TenMonAn LIKE %s"
        params.append(f"%{ten_mon}%")
    if loai:
        query += " AND Loai = %s"
        params.append(loai)

    cursor.execute(query, params)
    foods = cursor.fetchall()
    db.close()
    return jsonify(foods)

@food_bp.route('/', methods=['POST'])
def add_food():
    data = request.json
    ten_mon = data.get('TenMonAn')
    gia = data.get('Gia')
    loai = data.get('Loai')

    if not ten_mon or not gia or not loai:
        return jsonify({'message': 'Thiếu thông tin món ăn'}), 400

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO monan (TenMonAn, Gia, Loai)
        VALUES (%s, %s, %s)
    """, (ten_mon, gia, loai))
    db.commit()
    db.close()
    return jsonify({'message': 'Thêm món ăn thành công'}), 201

@food_bp.route('/<int:mon_an_id>', methods=['PUT'])
def update_food(mon_an_id):
    data = request.json
    ten_mon = data.get('TenMonAn')
    gia = data.get('Gia')
    loai = data.get('Loai')

    if not ten_mon or not gia or not loai:
        return jsonify({'message': 'Thiếu thông tin món ăn'}), 400

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE monan
        SET TenMonAn = %s, Gia = %s, Loai = %s
        WHERE MonAnID = %s
    """, (ten_mon, gia, loai, mon_an_id))
    db.commit()
    db.close()
    return jsonify({'message': 'Cập nhật món ăn thành công'})

@food_bp.route('/<int:mon_an_id>', methods=['DELETE'])
def delete_food(mon_an_id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM monan WHERE MonAnID = %s", (mon_an_id,))
    if cursor.fetchone() is None:
        db.close()
        return jsonify({'message': 'Món ăn không tồn tại'}), 404

    cursor.execute("DELETE FROM monan WHERE MonAnID = %s", (mon_an_id,))
    db.commit()
    db.close()
    return jsonify({'message': 'Xóa món ăn thành công'})
