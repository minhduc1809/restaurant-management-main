from flask import Blueprint, request, jsonify
from db_config import get_db_connection
from datetime import datetime

invoice_bp = Blueprint('invoice_bp', __name__)

@invoice_bp.route('/', methods=['POST'])
def create_invoice():
    data = request.json

    ho_ten_khach = data.get('HoTenKhachHang')
    nhan_vien_id = data.get('NhanVienID')
    chi_tiet = data.get('ChiTiet')  # Danh sách món ăn: [{MonAnID, SoLuong, Gia}]

    db = get_db_connection()
    cursor = db.cursor()

    # Tính tổng tiền
    tong_tien = sum(item['SoLuong'] * item['Gia'] for item in chi_tiet)
    thoi_diem = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Tạo hóa đơn
    cursor.execute("""
        INSERT INTO hoadon (ThoiDiemTao, HoTenKhachHang, TongTien, NhanVienID)
        VALUES (%s, %s, %s, %s)
    """, (thoi_diem, ho_ten_khach, tong_tien, nhan_vien_id))
    hoa_don_id = cursor.lastrowid

    # Thêm chi tiết hóa đơn
    for item in chi_tiet:
        mon_an_id = item['MonAnID']
        so_luong = item['SoLuong']
        gia = item['Gia']
        thanh_tien = so_luong * gia

        cursor.execute("""
            INSERT INTO chitiet_hoadon (HoaDonID, MonAnID, SoLuongMonAn, Gia, ThanhTien)
            VALUES (%s, %s, %s, %s, %s)
        """, (hoa_don_id, mon_an_id, so_luong, gia, thanh_tien))

    db.commit()
    db.close()

    return jsonify({'message': 'Lập hóa đơn thành công', 'HoaDonID': hoa_don_id}), 201

@invoice_bp.route('/<int:hoa_don_id>', methods=['GET'])
def get_invoice_detail(hoa_don_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Lấy thông tin hóa đơn
    cursor.execute("SELECT * FROM hoadon WHERE HoaDonID = %s", (hoa_don_id,))
    hoadon = cursor.fetchone()

    # Lấy chi tiết hóa đơn
    cursor.execute("""
        SELECT c.MonAnID, m.TenMonAn, c.SoLuongMonAn, c.Gia, c.ThanhTien
        FROM chitiet_hoadon c
        JOIN monan m ON c.MonAnID = m.MonAnID
        WHERE c.HoaDonID = %s
    """, (hoa_don_id,))
    chitiet = cursor.fetchall()

    db.close()
    return jsonify({'HoaDon': hoadon, 'ChiTiet': chitiet})
