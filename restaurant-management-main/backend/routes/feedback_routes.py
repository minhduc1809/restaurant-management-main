from flask import Blueprint, request, jsonify
from db_config import get_db_connection

feedback_bp = Blueprint('feedback_bp', __name__)

# 📩 Gửi phản hồi (bỏ điểm đánh giá)
@feedback_bp.route('/', methods=['POST'])
def send_feedback():
    data = request.json
    khach_hang_id = data.get('KhachHangID')
    noi_dung = data.get('NoiDung')

    if not khach_hang_id or noi_dung is None:
        return jsonify({'message': 'Thiếu thông tin phản hồi'}), 400

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO phanhoi (KhachHangID, NoiDung)
        VALUES (%s, %s)
    """, (khach_hang_id, noi_dung))

    db.commit()
    db.close()
    return jsonify({'message': 'Gửi phản hồi thành công'}), 201

# 📋 Lấy tất cả phản hồi (bỏ điểm đánh giá)
@feedback_bp.route('/', methods=['GET'])
def get_all_feedback():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.PhanHoiID, f.NoiDung, kh.HoTenKhachHang
        FROM phanhoi f
        JOIN khachhang kh ON f.KhachHangID = kh.KhachHangID
        ORDER BY f.PhanHoiID DESC
    """)
    feedbacks = cursor.fetchall()
    db.close()
    return jsonify(feedbacks)

# ❌ Xóa phản hồi theo ID
@feedback_bp.route('/<int:phanhoi_id>', methods=['DELETE'])
def delete_feedback(phanhoi_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM phanhoi WHERE PhanHoiID = %s", (phanhoi_id,))
    result = cursor.fetchone()

    if not result:
        db.close()
        return jsonify({'message': 'Phản hồi không tồn tại'}), 404

    cursor.execute("DELETE FROM phanhoi WHERE PhanHoiID = %s", (phanhoi_id,))
    db.commit()
    db.close()
    return jsonify({'message': f'Đã xóa phản hồi {phanhoi_id}'}), 200
