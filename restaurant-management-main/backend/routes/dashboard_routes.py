from flask import Blueprint, jsonify
from db_config import get_db_connection

dashboard_bp = Blueprint('dashboard_bp', __name__)

# 📊 API: Thống kê dashboard chính
@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Tổng số nhân viên
    cursor.execute("SELECT COUNT(*) AS total FROM nhanvien")
    total_employees = cursor.fetchone()['total']

    # Tổng số bàn ăn
    cursor.execute("SELECT COUNT(*) AS total FROM banan")
    total_tables = cursor.fetchone()['total']

    # Đơn hôm nay
    cursor.execute("SELECT COUNT(*) AS total FROM hoadon WHERE DATE(ThoiDiemTao) = CURDATE()")
    today_orders = cursor.fetchone()['total']

    # Doanh thu tháng hiện tại
    cursor.execute("""
        SELECT SUM(TongTien) AS revenue
        FROM hoadon
        WHERE MONTH(ThoiDiemTao) = MONTH(CURDATE())
          AND YEAR(ThoiDiemTao) = YEAR(CURDATE())
    """)
    monthly_revenue = cursor.fetchone()['revenue'] or 0

    db.close()

    return jsonify({
        'totalEmployees': total_employees,
        'totalTables': total_tables,
        'todayOrders': today_orders,
        'monthlyRevenue': round(monthly_revenue)
    })


# 📊 API: Doanh thu theo tháng để vẽ biểu đồ
@dashboard_bp.route('/monthly-revenue', methods=['GET'])
def get_monthly_revenue():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            DATE_FORMAT(ThoiDiemTao, '%Y-%m') AS month,
            SUM(TongTien) AS total
        FROM hoadon
        GROUP BY month
        ORDER BY month
    """)
    results = cursor.fetchall()

    db.close()
    return jsonify(results)
