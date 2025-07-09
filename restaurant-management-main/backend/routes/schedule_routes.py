from flask import Blueprint, request, jsonify
from db_config import get_db_connection

schedule_bp = Blueprint('schedule_bp', __name__)

# 📋 Lấy toàn bộ lịch làm (kèm tên nhân viên)
@schedule_bp.route('/', methods=['GET'])
def get_all_schedules():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.LichLamID, l.NhanVienID, n.HoTenNhanVien, l.SoGioLam, l.Ca, l.Ngay
        FROM lichlam l
        JOIN nhanvien n ON l.NhanVienID = n.NhanVienID
        ORDER BY l.Ngay DESC
    """)
    schedules = cursor.fetchall()
    db.close()
    return jsonify(schedules)

# 📝 Tạo lịch làm mới
# 📝 Tạo lịch làm mới
@schedule_bp.route('/', methods=['POST'])
def create_schedule():
    data = request.json
    nhan_vien_id = data.get('NhanVienID')
    so_gio_lam = data.get('SoGioLam')
    ca = data.get('Ca')
    ngay = data.get('Ngay')  # Format: 'YYYY-MM-DD'

    if not all([nhan_vien_id, so_gio_lam, ca, ngay]):
        return jsonify({'message': 'Thiếu thông tin'}), 400

    db = get_db_connection()
    cursor = db.cursor()

    # ❗ Kiểm tra nhân viên đã có lịch vào ngày đó và ca đó chưa
    cursor.execute("""
        SELECT * FROM lichlam 
        WHERE NhanVienID = %s AND Ngay = %s AND Ca = %s
    """, (nhan_vien_id, ngay, ca))
    exists = cursor.fetchone()
    if exists:
        db.close()
        return jsonify({'message': 'Nhân viên đã có lịch làm trong ca này ngày này!'}), 409

    # ✅ Tạo lịch mới
    cursor.execute("""
        INSERT INTO lichlam (NhanVienID, SoGioLam, Ca, Ngay)
        VALUES (%s, %s, %s, %s)
    """, (nhan_vien_id, so_gio_lam, ca, ngay))
    db.commit()
    db.close()
    return jsonify({'message': 'Tạo lịch làm thành công'}), 201

# 🔍 Lấy lịch làm theo NhanVienID
@schedule_bp.route('/nhanvien/<int:nhan_vien_id>', methods=['GET'])
def get_schedule_by_employee_id(nhan_vien_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.LichLamID, l.NhanVienID, n.HoTenNhanVien, l.SoGioLam, l.Ca, l.Ngay
        FROM lichlam l
        JOIN nhanvien n ON l.NhanVienID = n.NhanVienID
        WHERE l.NhanVienID = %s
        ORDER BY l.Ngay DESC
    """, (nhan_vien_id,))
    schedules = cursor.fetchall()
    db.close()
    return jsonify(schedules)

# ❌ Xoá lịch làm theo ID
@schedule_bp.route('/<int:lich_lam_id>', methods=['DELETE'])
def delete_schedule(lich_lam_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM lichlam WHERE LichLamID = %s", (lich_lam_id,))
    db.commit()
    db.close()
    return jsonify({'message': 'Xoá lịch làm thành công'})

# 🔎 Tìm kiếm nâng cao theo tên nhân viên, ca, ngày
@schedule_bp.route('/search', methods=['GET'])
def search_schedule():
    ten = request.args.get('ten', '')
    ca = request.args.get('ca', '')
    ngay = request.args.get('ngay', '')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT l.LichLamID, l.NhanVienID, n.HoTenNhanVien, l.SoGioLam, l.Ca, l.Ngay
        FROM lichlam l
        JOIN nhanvien n ON l.NhanVienID = n.NhanVienID
        WHERE 1=1
    """
    params = []

    if ten:
        query += " AND n.HoTenNhanVien LIKE %s"
        params.append(f"%{ten}%")
    if ca:
        query += " AND l.Ca = %s"
        params.append(ca)
    if ngay:
        query += " AND l.Ngay = %s"
        params.append(ngay)

    query += " ORDER BY l.Ngay DESC"
    cursor.execute(query, params)
    results = cursor.fetchall()
    db.close()
    return jsonify(results)
