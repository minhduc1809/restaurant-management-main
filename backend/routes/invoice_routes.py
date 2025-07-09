from flask import Blueprint, request, jsonify
from db_config import get_db_connection
from datetime import datetime, timedelta

invoice_bp = Blueprint('invoice_bp', __name__)

# 📋 Lấy tất cả hóa đơn
@invoice_bp.route('/', methods=['GET'])
def get_all_invoices():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT hd.*, kh.HoTenKhachHang, nv.HoTenNhanVien
        FROM hoadon hd
        JOIN khachhang kh ON hd.KhachHangID = kh.KhachHangID
        JOIN nhanvien nv ON hd.NhanVienID = nv.NhanVienID
        ORDER BY ThoiDiemTao DESC
    """)
    invoices = cursor.fetchall()

    db.close()
    return jsonify(invoices)

# ➕ Tạo hóa đơn mới
@invoice_bp.route('/', methods=['POST'])
def create_invoice():
    data = request.json
    ho_ten_khach = data.get('HoTenKhachHang')
    chi_tiet = data.get('ChiTiet')  # [{"MonAnID": 1, "SoLuong": 2}, ...]
    nhan_vien_id = data.get('NhanVienID', 1)

    if not ho_ten_khach or not chi_tiet:
        return jsonify({'message': 'Thiếu thông tin hóa đơn'}), 400

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Kiểm tra nhân viên tồn tại
    cursor.execute("SELECT * FROM nhanvien WHERE NhanVienID = %s", (nhan_vien_id,))
    if not cursor.fetchone():
        db.close()
        return jsonify({'message': 'Nhân viên không tồn tại'}), 400

    # Tìm hoặc thêm khách hàng
    cursor.execute("SELECT KhachHangID FROM khachhang WHERE HoTenKhachHang = %s", (ho_ten_khach,))
    khach = cursor.fetchone()
    if khach:
        khach_hang_id = khach['KhachHangID']
    else:
        cursor.execute("INSERT INTO khachhang (HoTenKhachHang) VALUES (%s)", (ho_ten_khach,))
        khach_hang_id = cursor.lastrowid

    tong_tien = 0
    hoa_don_chi_tiet = []

    for item in chi_tiet:
        mon_id = item['MonAnID']
        so_luong = item['SoLuong']

        cursor.execute("SELECT Gia FROM monan WHERE MonAnID = %s", (mon_id,))
        mon = cursor.fetchone()
        if not mon:
            db.close()
            return jsonify({'message': f'Món ăn ID {mon_id} không tồn tại'}), 400

        gia = float(mon['Gia'])
        thanh_tien = gia * so_luong
        tong_tien += thanh_tien
        hoa_don_chi_tiet.append((mon_id, so_luong, gia, thanh_tien))

    thoi_diem = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Thêm hóa đơn
    cursor.execute("""
        INSERT INTO hoadon (NhanVienID, KhachHangID, ThoiDiemTao, TongTien)
        VALUES (%s, %s, %s, %s)
    """, (nhan_vien_id, khach_hang_id, thoi_diem, tong_tien))
    hoa_don_id = cursor.lastrowid

    # Thêm chi tiết hóa đơn
    for mon_id, so_luong, gia, thanh_tien in hoa_don_chi_tiet:
        cursor.execute("""
            INSERT INTO chitiet_hoadon (HoaDonID, MonAnID, SoLuongMonAn, Gia, ThanhTien)
            VALUES (%s, %s, %s, %s, %s)
        """, (hoa_don_id, mon_id, so_luong, gia, thanh_tien))

    db.commit()
    db.close()

    return jsonify({'message': 'Lưu hóa đơn thành công', 'HoaDonID': hoa_don_id}), 201

# 🔍 Tìm kiếm hóa đơn
@invoice_bp.route('/search', methods=['GET'])
def search_invoices():
    ten_khach = request.args.get('ten', '')
    tu_ngay = request.args.get('from', '')
    den_ngay = request.args.get('to', '')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT hd.*, kh.HoTenKhachHang, nv.HoTenNhanVien
        FROM hoadon hd
        JOIN khachhang kh ON hd.KhachHangID = kh.KhachHangID
        JOIN nhanvien nv ON hd.NhanVienID = nv.NhanVienID
        WHERE 1=1
    """
    params = []

    if ten_khach:
        query += " AND kh.HoTenKhachHang LIKE %s"
        params.append(f"%{ten_khach}%")
    if tu_ngay:
        query += " AND DATE(hd.ThoiDiemTao) >= %s"
        params.append(tu_ngay)
    if den_ngay:
        query += " AND DATE(hd.ThoiDiemTao) <= %s"
        params.append(den_ngay)

    query += " ORDER BY hd.ThoiDiemTao DESC"
    cursor.execute(query, params)
    results = cursor.fetchall()

    db.close()
    return jsonify(results)

# 📄 Lấy chi tiết hóa đơn
@invoice_bp.route('/<int:hoa_don_id>', methods=['GET'])
def get_invoice_detail(hoa_don_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT hd.*, kh.HoTenKhachHang, nv.HoTenNhanVien
        FROM hoadon hd
        JOIN khachhang kh ON hd.KhachHangID = kh.KhachHangID
        JOIN nhanvien nv ON hd.NhanVienID = nv.NhanVienID
        WHERE HoaDonID = %s
    """, (hoa_don_id,))
    hoa_don = cursor.fetchone()
    if not hoa_don:
        db.close()
        return jsonify({'message': 'Không tìm thấy hóa đơn'}), 404

    cursor.execute("""
        SELECT ct.MonAnID, ma.TenMonAn, ct.SoLuongMonAn, ct.Gia, ct.ThanhTien
        FROM chitiet_hoadon ct
        JOIN monan ma ON ct.MonAnID = ma.MonAnID
        WHERE ct.HoaDonID = %s
    """, (hoa_don_id,))
    chi_tiet = cursor.fetchall()
    db.close()

    return jsonify({'HoaDon': hoa_don, 'ChiTiet': chi_tiet})

# ✏️ Cập nhật hóa đơn trong 15 phút
@invoice_bp.route('/<int:hoa_don_id>', methods=['PUT'])
def update_invoice(hoa_don_id):
    data = request.json
    chi_tiet_moi = data.get('ChiTiet')

    if not chi_tiet_moi:
        return jsonify({'message': 'Thiếu thông tin món ăn'}), 400

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT ThoiDiemTao FROM hoadon WHERE HoaDonID = %s", (hoa_don_id,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return jsonify({'message': 'Hóa đơn không tồn tại'}), 404

    thoi_diem_tao = result['ThoiDiemTao']
    if datetime.now() - thoi_diem_tao > timedelta(minutes=15):
        db.close()
        return jsonify({'message': 'Chỉ được sửa trong 15 phút'}), 403

    cursor.execute("DELETE FROM chitiet_hoadon WHERE HoaDonID = %s", (hoa_don_id,))

    tong_tien_moi = 0
    for item in chi_tiet_moi:
        thanh_tien = item['SoLuong'] * item['Gia']
        tong_tien_moi += thanh_tien
        cursor.execute("""
            INSERT INTO chitiet_hoadon (HoaDonID, MonAnID, SoLuongMonAn, Gia, ThanhTien)
            VALUES (%s, %s, %s, %s, %s)
        """, (hoa_don_id, item['MonAnID'], item['SoLuong'], item['Gia'], thanh_tien))

    cursor.execute("UPDATE hoadon SET TongTien = %s WHERE HoaDonID = %s", (tong_tien_moi, hoa_don_id))

    db.commit()
    db.close()

    return jsonify({'message': 'Cập nhật hóa đơn thành công'})

# 📋 API lấy danh sách món ăn (cho form thêm hóa đơn)
@invoice_bp.route('/monan', methods=['GET'])
def get_all_monan():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT MonAnID, TenMonAn, Gia FROM monan")
    monan = cursor.fetchall()
    db.close()
    return jsonify(monan)
# 📋 API lấy danh sách nhân viên (cho form thêm hóa đơn)
@invoice_bp.route('/nhanvien', methods=['GET'])
def get_all_nhanvien():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT NhanVienID, HoTenNhanVien FROM nhanvien")
    nhanvien = cursor.fetchall()
    db.close()
    return jsonify(nhanvien)
