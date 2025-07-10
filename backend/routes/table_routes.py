from flask import Blueprint, request, jsonify
from db_config import get_db_connection
from datetime import datetime, timedelta
import pytz

table_bp = Blueprint('table_bp', __name__)

# Thiết lập múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def get_vn_now():
    return datetime.now(VN_TZ)

def tinh_trang_thai_ban(thoi_gian_dat_vn):
    now = get_vn_now()
    thoi_gian_ket_thuc = thoi_gian_dat_vn + timedelta(hours=3)

    if now < thoi_gian_dat_vn:
        return 'Đã đặt'
    elif thoi_gian_dat_vn <= now < thoi_gian_ket_thuc:
        con_lai = (thoi_gian_ket_thuc - now).total_seconds() / 60
        if con_lai <= 30:
            return 'Sắp trống'
        return 'Đang sử dụng'
    else:
        return 'Trống'

def cap_nhat_trang_thai_ban():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Lấy tất cả bàn
    cursor.execute("SELECT BanAnID FROM banan")
    ds_ban = cursor.fetchall()

    for ban in ds_ban:
        ban_id = ban['BanAnID']

        # Tìm lượt đặt mới nhất gần thời gian hiện tại
        cursor.execute("""
            SELECT ThoiGianDat FROM luotdatban 
            WHERE BanAnID = %s 
            ORDER BY ThoiGianDat DESC LIMIT 1
        """, (ban_id,))
        ket_qua = cursor.fetchone()

        if not ket_qua:
            trang_thai = 'Trống'
        else:
            thoi_gian_utc = pytz.UTC.localize(ket_qua['ThoiGianDat'])
            thoi_gian_vn = thoi_gian_utc.astimezone(VN_TZ)
            trang_thai = tinh_trang_thai_ban(thoi_gian_vn)

        # Cập nhật lại trạng thái bàn
        cursor.execute("UPDATE banan SET TrangThai = %s WHERE BanAnID = %s", (trang_thai, ban_id))

    db.commit()
    db.close()

# 📋 Lấy danh sách tất cả bàn ăn và cập nhật trạng thái trước khi trả
@table_bp.route('/', methods=['GET'])
def get_all_tables():
    cap_nhat_trang_thai_ban()  # cập nhật trước khi trả dữ liệu
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
    trang_thai = data.get('TrangThai', 'Trống')  # mặc định là Trống nếu không có

    if so_ban is None:
        return jsonify({'message': 'Thiếu số bàn'}), 400

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO banan (SoBan, TrangThai)
        VALUES (%s, %s)
    """, (so_ban, trang_thai))

    db.commit()
    db.close()
    return jsonify({'message': 'Thêm bàn thành công'}), 201

# ✏️ Cập nhật trạng thái bàn ăn thủ công
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

# 🔄 API cập nhật trạng thái tất cả bàn (nếu muốn gọi tay)
@table_bp.route('/cap-nhat-trang-thai', methods=['POST'])
def trigger_cap_nhat_trang_thai():
    cap_nhat_trang_thai_ban()
    return jsonify({'message': 'Cập nhật trạng thái bàn ăn thành công'})
