from flask import Blueprint, request, jsonify
from db_config import get_db_connection

employee_bp = Blueprint('employee_bp', __name__)

@employee_bp.route('/', methods=['GET'])
def get_all_employees():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM nhanvien")
    employees = cursor.fetchall()
    db.close()
    return jsonify(employees)

@employee_bp.route('/', methods=['POST'])
def add_employee():
    data = request.json
    hoten = data.get('HoTenNhanVien')
    vaitro = data.get('VaiTro')
    sdt = data.get('SoDienThoai')
    username = data.get('TenDangNhap')
    password = data.get('MatKhau')

    db = get_db_connection()
    cursor = db.cursor()
    query = """
        INSERT INTO nhanvien (HoTenNhanVien, VaiTro, SoDienThoai, TenDangNhap, MatKhau)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (hoten, vaitro, sdt, username, password))
    db.commit()
    db.close()

    return jsonify({'message': 'Thêm nhân viên thành công'}), 201

@employee_bp.route('/<int:nhanvien_id>', methods=['PUT'])
def update_employee(nhanvien_id):
    data = request.json
    hoten = data.get('HoTenNhanVien')
    vaitro = data.get('VaiTro')
    sdt = data.get('SoDienThoai')

    db = get_db_connection()
    cursor = db.cursor()
    query = """
        UPDATE nhanvien SET HoTenNhanVien = %s, VaiTro = %s, SoDienThoai = %s
        WHERE NhanVienID = %s
    """
    cursor.execute(query, (hoten, vaitro, sdt, nhanvien_id))
    db.commit()
    db.close()

    return jsonify({'message': 'Cập nhật nhân viên thành công'})

@employee_bp.route('/<int:nhanvien_id>', methods=['DELETE'])
def delete_employee(nhanvien_id):
    db = get_db_connection()
    cursor = db.cursor()
    query = "DELETE FROM nhanvien WHERE NhanVienID = %s"
    cursor.execute(query, (nhanvien_id,))
    db.commit()
    db.close()

    return jsonify({'message': 'Xoá nhân viên thành công'})
