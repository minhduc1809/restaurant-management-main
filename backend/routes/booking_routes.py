from flask import Blueprint, request, jsonify
from db_config import get_db_connection
from datetime import datetime, timedelta
import pytz

booking_bp = Blueprint('booking_bp', __name__)

# Múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def get_vn_now():
    """Lấy thời gian hiện tại theo múi giờ Việt Nam"""
    return datetime.now(VN_TZ)

def convert_to_vn_time(dt_str):
    """Chuyển đổi string thời gian thành datetime với múi giờ Việt Nam"""
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
    return VN_TZ.localize(dt)

def format_for_db(dt):
    """Format datetime để lưu vào database (UTC)"""
    return dt.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

def parse_from_db(dt_str):
    """Parse datetime từ database và chuyển về múi giờ Việt Nam"""
    dt_utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    dt_utc = pytz.UTC.localize(dt_utc)
    return dt_utc.astimezone(VN_TZ)

# 📋 Lấy tất cả lượt đặt bàn kèm trạng thái bàn ăn
@booking_bp.route('/', methods=['GET'])
def get_all_bookings():
    search = request.args.get('search')
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT l.LuotDatBanID, k.HoTenKhachHang, l.ThoiGianDat, 
               b.SoBan, b.TrangThai
        FROM luotdatban l
        JOIN khachhang k ON l.KhachHangID = k.KhachHangID
        JOIN banan b ON l.BanAnID = b.BanAnID
    """
    if search:
        query += " WHERE k.HoTenKhachHang LIKE %s ORDER BY l.ThoiGianDat DESC"
        cursor.execute(query, (f"%{search}%",))
    else:
        query += " ORDER BY l.ThoiGianDat DESC"
        cursor.execute(query)

    bookings = cursor.fetchall()
    
    # Chuyển đổi thời gian về múi giờ Việt Nam cho frontend
    for booking in bookings:
        if booking['ThoiGianDat']:
            # Chuyển từ UTC (database) về VN time
            dt_utc = pytz.UTC.localize(booking['ThoiGianDat'])
            booking['ThoiGianDat'] = dt_utc.astimezone(VN_TZ).isoformat()
    
    db.close()
    return jsonify(bookings)

# ➕ Thêm lượt đặt bàn mới
@booking_bp.route('/', methods=['POST'])
def create_booking():
    data = request.json
    ten_khach_hang = data.get('HoTenKhachHang')
    thoi_gian_dat_str = data.get('ThoiGianDat')  # ISO format: "YYYY-MM-DDTHH:MM"
    so_ban = data.get('SoBan')

    if not ten_khach_hang or not thoi_gian_dat_str or not so_ban:
        return jsonify({'message': 'Thiếu thông tin bắt buộc'}), 400

    try:
        # Chuyển đổi thời gian từ frontend (VN time) 
        thoi_gian_dat = convert_to_vn_time(thoi_gian_dat_str)
    except ValueError:
        return jsonify({'message': 'Định dạng thời gian không hợp lệ'}), 400

    # Kiểm tra thời gian đặt phải sau thời gian hiện tại (cùng múi giờ VN)
    now_vn = get_vn_now()
    if thoi_gian_dat <= now_vn:
        return jsonify({'message': 'Thời gian đặt phải sau thời gian hiện tại'}), 400

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        # Kiểm tra khách hàng có tồn tại chưa
        cursor.execute("SELECT KhachHangID FROM khachhang WHERE HoTenKhachHang = %s", (ten_khach_hang,))
        result = cursor.fetchone()

        if result:
            khach_hang_id = result['KhachHangID']
        else:
            cursor.execute(
                "INSERT INTO khachhang (HoTenKhachHang, SoDienThoai) VALUES (%s, %s)",
                (ten_khach_hang, '')
            )
            khach_hang_id = cursor.lastrowid

        # Lấy BanAnID từ số bàn
        cursor.execute("SELECT BanAnID FROM banan WHERE SoBan = %s", (so_ban,))
        ban_result = cursor.fetchone()

        if not ban_result:
            db.rollback()
            db.close()
            return jsonify({'message': 'Không tìm thấy số bàn này'}), 400

        ban_an_id = ban_result['BanAnID']

        # Chuyển đổi thời gian để lưu vào database (UTC)
        thoi_gian_dat_utc = format_for_db(thoi_gian_dat)
        thoi_gian_ket_thuc_utc = format_for_db(thoi_gian_dat + timedelta(hours=3))
        
        # Kiểm tra bàn có bị trùng trong khung 3 giờ không
        cursor.execute("""
            SELECT LuotDatBanID, ThoiGianDat 
            FROM luotdatban 
            WHERE BanAnID = %s 
            AND (
                (%s >= ThoiGianDat AND %s < DATE_ADD(ThoiGianDat, INTERVAL 3 HOUR))
                OR
                (ThoiGianDat >= %s AND ThoiGianDat < %s)
            )
        """, (ban_an_id, thoi_gian_dat_utc, thoi_gian_dat_utc, 
              thoi_gian_dat_utc, thoi_gian_ket_thuc_utc))

        conflicting_bookings = cursor.fetchall()

        if conflicting_bookings:
            db.rollback()
            db.close()
            return jsonify({
                'message': 'Bàn này đã được đặt trong khung giờ đó. Vui lòng chọn thời gian khác (cách ít nhất 3 tiếng so với lượt đặt khác)'
            }), 400

        # Thêm lượt đặt bàn mới (lưu UTC vào database)
        cursor.execute("""
            INSERT INTO luotdatban (KhachHangID, BanAnID, ThoiGianDat)
            VALUES (%s, %s, %s)
        """, (khach_hang_id, ban_an_id, thoi_gian_dat_utc))

        db.commit()

        return jsonify({'message': 'Đặt bàn thành công'}), 201

    except Exception as e:
        db.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        db.close()

# 📊 Lấy trạng thái bàn cho thời gian cụ thể (API bổ sung)
@booking_bp.route('/table-status/<int:so_ban>', methods=['GET'])
def get_table_status(so_ban):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Lấy BanAnID từ số bàn
        cursor.execute("SELECT BanAnID FROM banan WHERE SoBan = %s", (so_ban,))
        ban_result = cursor.fetchone()
        
        if not ban_result:
            return jsonify({'message': 'Không tìm thấy bàn'}), 404
            
        ban_an_id = ban_result['BanAnID']
        current_time_vn = get_vn_now()
        
        # Lấy tất cả lượt đặt của bàn này
        cursor.execute("""
            SELECT l.LuotDatBanID, k.HoTenKhachHang, l.ThoiGianDat
            FROM luotdatban l
            JOIN khachhang k ON l.KhachHangID = k.KhachHangID
            WHERE l.BanAnID = %s
            ORDER BY l.ThoiGianDat ASC
        """, (ban_an_id,))
        
        bookings = cursor.fetchall()
        
        # Chuyển đổi thời gian và xác định trạng thái
        current_status = "Trống"
        current_booking = None
        
        for booking in bookings:
            # Chuyển từ UTC (database) về VN time
            dt_utc = pytz.UTC.localize(booking['ThoiGianDat'])
            thoi_gian_dat_vn = dt_utc.astimezone(VN_TZ)
            thoi_gian_ket_thuc_vn = thoi_gian_dat_vn + timedelta(hours=3)
            
            # Cập nhật thời gian cho response
            booking['ThoiGianDat'] = thoi_gian_dat_vn.isoformat()
            
            if current_time_vn >= thoi_gian_dat_vn and current_time_vn < thoi_gian_ket_thuc_vn:
                current_status = "Đang sử dụng"
                current_booking = booking
                break
            elif current_time_vn < thoi_gian_dat_vn:
                current_status = "Đã đặt"
                current_booking = booking
                break
        
        return jsonify({
            'so_ban': so_ban,
            'trang_thai': current_status,
            'booking_info': current_booking,
            'tat_ca_dat_ban': bookings,
            'current_time_vn': current_time_vn.isoformat()
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        db.close()

# ❌ Xóa lượt đặt bàn
@booking_bp.route('/<int:luot_dat_ban_id>', methods=['DELETE'])
def delete_booking(luot_dat_ban_id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM luotdatban WHERE LuotDatBanID = %s", (luot_dat_ban_id,))
        db.commit()
        return jsonify({'message': 'Hủy lượt đặt bàn thành công'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        db.close()