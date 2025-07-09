from flask import Flask, request, redirect, send_from_directory, session, url_for
from flask_cors import CORS
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Cần để dùng session
CORS(app)

# Import & Đăng ký các route
from routes.food_routes import food_bp
app.register_blueprint(food_bp, url_prefix='/api/foods')

from routes.employee_routes import employee_bp
app.register_blueprint(employee_bp, url_prefix='/api/employees')

from routes.invoice_routes import invoice_bp
app.register_blueprint(invoice_bp, url_prefix='/api/hoadon')

from routes.auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')

from routes.schedule_routes import schedule_bp
app.register_blueprint(schedule_bp, url_prefix='/api/lichlam')

from routes.table_routes import table_bp
app.register_blueprint(table_bp, url_prefix='/api/banan')

from routes.ingredient_routes import ingredient_bp
app.register_blueprint(ingredient_bp, url_prefix='/api/kho')

from routes.search_routes import search_bp
app.register_blueprint(search_bp, url_prefix='/api/search')
from routes.feedback_routes import feedback_bp
app.register_blueprint(feedback_bp, url_prefix='/api/feedbacks')
from routes.booking_routes import booking_bp
app.register_blueprint(booking_bp, url_prefix='/api/bookings')
from routes.dashboard_routes import dashboard_bp
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    return send_from_directory('../frontend', path)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM taikhoan WHERE TenDangNhap=%s AND MatKhau=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        session['username'] = user['TenDangNhap']
        session['role'] = user['VaiTro']
        if user['VaiTro'] == 'admin':
            return redirect('/admin.html')
        else:
            return "Bạn không có quyền truy cập trang này", 403
    else:
        return "Đăng nhập thất bại", 401

if __name__ == '__main__':
    app.run(debug=True)
