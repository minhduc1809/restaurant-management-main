from flask import Blueprint, request, jsonify
from db_config import get_db_connection

ingredient_bp = Blueprint('ingredient_bp', __name__)

# 📋 Lấy danh sách tất cả kho và nguyên liệu
@ingredient_bp.route('/tatca', methods=['GET'])
def get_kho_with_ingredients():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            k.KhoID, k.TenKho, k.ViTri,
            nl.NguyenLieuID, nl.TenNguyenLieu, nl.DonVi, nl.SoLuong
        FROM kho k
        LEFT JOIN nguyenlieu nl ON k.KhoID = nl.KhoID
        ORDER BY k.KhoID, nl.NguyenLieuID
    """)
    rows = cursor.fetchall()
    db.close()

    kho_map = {}
    for row in rows:
        kho_id = row['KhoID']
        if kho_id not in kho_map:
            kho_map[kho_id] = {
                'KhoID': kho_id,
                'TenKho': row['TenKho'],
                'ViTri': row['ViTri'],
                'NguyenLieu': []
            }
        if row['NguyenLieuID']:
            kho_map[kho_id]['NguyenLieu'].append({
                'NguyenLieuID': row['NguyenLieuID'],
                'TenNguyenLieu': row['TenNguyenLieu'],
                'DonVi': row['DonVi'],
                'SoLuong': row['SoLuong']
            })

    return jsonify(list(kho_map.values()))

# ➕ Thêm nguyên liệu vào kho
@ingredient_bp.route('/', methods=['POST'])
def add_ingredient():
    data = request.json
    ten = data.get('TenNguyenLieu')
    don_vi = data.get('DonVi', 'kg')
    so_luong = data.get('SoLuong', 0)
    kho_id = data.get('KhoID')

    if not ten or not kho_id:
        return jsonify({'message': 'Thiếu tên nguyên liệu hoặc KhoID'}), 400

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO nguyenlieu (TenNguyenLieu, DonVi, SoLuong, KhoID)
        VALUES (%s, %s, %s, %s)
    """, (ten, don_vi, so_luong, kho_id))
    db.commit()
    db.close()
    return jsonify({'message': 'Thêm nguyên liệu thành công'}), 201

# ✏️ Sửa nguyên liệu
@ingredient_bp.route('/<int:id>', methods=['PUT'])
def update_ingredient(id):
    data = request.json
    ten = data.get('TenNguyenLieu')
    don_vi = data.get('DonVi')
    so_luong = data.get('SoLuong')
    kho_id = data.get('KhoID')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE nguyenlieu
        SET TenNguyenLieu=%s, DonVi=%s, SoLuong=%s, KhoID=%s
        WHERE NguyenLieuID=%s
    """, (ten, don_vi, so_luong, kho_id, id))
    db.commit()
    db.close()
    return jsonify({'message': 'Cập nhật nguyên liệu thành công'})

# ❌ Xóa nguyên liệu
@ingredient_bp.route('/<int:id>', methods=['DELETE'])
def delete_ingredient(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM nguyenlieu WHERE NguyenLieuID=%s", (id,))
    db.commit()
    db.close()
    return jsonify({'message': 'Xóa nguyên liệu thành công'})
# 🔍 Tìm kiếm nguyên liệu theo tên
@ingredient_bp.route('/timkiem', methods=['GET'])
def search_ingredients():
    keyword = request.args.get('keyword', '').strip()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT 
            nl.NguyenLieuID, nl.TenNguyenLieu, nl.DonVi, nl.SoLuong,
            k.KhoID, k.TenKho, k.ViTri
        FROM nguyenlieu nl
        JOIN kho k ON nl.KhoID = k.KhoID
        WHERE nl.TenNguyenLieu LIKE %s
    """
    cursor.execute(query, ('%' + keyword + '%',))
    results = cursor.fetchall()
    db.close()

    return jsonify(results)
