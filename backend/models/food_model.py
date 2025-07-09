from flask import Blueprint, request, jsonify
from db_config import get_db_connection

food_bp = Blueprint('food_bp', __name__)

@food_bp.route('/', methods=['GET'])
def get_all_foods():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Lấy tham số lọc từ query string
    ten_mon_an = request.args.get('ten', '')
    loai = request.args.get('loai', '')

    # Truy vấn có lọc
    query = "SELECT * FROM monan WHERE TenMonAn LIKE %s AND Loai LIKE %s"
    cursor.execute(query, (f"%{ten_mon_an}%", f"%{loai}%"))

    foods = cursor.fetchall()
    db.close()
    return jsonify(foods)

@food_bp.route('/', methods=['POST'])
def add_food():
    data = request.json
    ten = data.get('TenMonAn')
    gia = data.get('Gia')
    loai = data.get('Loai')

    db = get_db_connection()
    cursor = db.cursor()
    query = "INSERT INTO monan (TenMonAn, Gia, Loai) VALUES (%s, %s, %s)"
    cursor.execute(query, (ten, gia, loai))
    db.commit()
    db.close()

    return jsonify({'message': 'Đã thêm món ăn mới'}), 201

@food_bp.route('/<int:mon_an_id>', methods=['PUT'])
def update_food(mon_an_id):
    data = request.json
    ten = data.get('TenMonAn')
    gia = data.get('Gia')
    loai = data.get('Loai')

    db = get_db_connection()
    cursor = db.cursor()
    query = "UPDATE monan SET TenMonAn = %s, Gia = %s, Loai = %s WHERE MonAnID = %s"
    cursor.execute(query, (ten, gia, loai, mon_an_id))
    db.commit()
    db.close()

    return jsonify({'message': 'Cập nhật thành công'})

@food_bp.route('/<int:mon_an_id>', methods=['DELETE'])
def delete_food(mon_an_id):
    db = get_db_connection()
    cursor = db.cursor()
    query = "DELETE FROM monan WHERE MonAnID = %s"
    cursor.execute(query, (mon_an_id,))
    db.commit()
    db.close()

    return jsonify({'message': 'Xoá thành công'})
