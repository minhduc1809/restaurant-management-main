from flask import Blueprint, request, jsonify
from db_config import get_db_connection

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM nhanvien WHERE TenDangNhap = %s AND MatKhau = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            'message': 'Đăng nhập thành công',
            'NhanVienID': user['NhanVienID'],
            'HoTenNhanVien': user['HoTenNhanVien'],
            'VaiTro': user['VaiTro']
        }), 200
    else:
        return jsonify({'message': 'Sai tài khoản hoặc mật khẩu'}), 401
