-- XÓA DATABASE CŨ (nếu có)
DROP DATABASE IF EXISTS restaurant_db;

-- TẠO DATABASE MỚI
CREATE DATABASE restaurant_db;
USE restaurant_db;

-- 1. KHÁCH HÀNG
CREATE TABLE khachhang (
    KhachHangID INT AUTO_INCREMENT PRIMARY KEY,
    HoTenKhachHang VARCHAR(100),
    SoDienThoai VARCHAR(20)
);

-- 2. NHÂN VIÊN
CREATE TABLE nhanvien (
    NhanVienID INT AUTO_INCREMENT PRIMARY KEY,
    HoTenNhanVien VARCHAR(100),
    VaiTro VARCHAR(50),
    SoDienThoai VARCHAR(20)
);

-- 3. LỊCH LÀM (1-1 với nhân viên)
CREATE TABLE lichlam (
    LichLamID INT AUTO_INCREMENT PRIMARY KEY,
    NhanVienID INT UNIQUE,
    SoGioLam INT,
    Ca VARCHAR(20),
    Ngay DATE,
    FOREIGN KEY (NhanVienID) REFERENCES nhanvien(NhanVienID)
);

-- 4. KHO (1 kho do 1 nhân viên quản lý)
CREATE TABLE kho (
    KhoID INT AUTO_INCREMENT PRIMARY KEY,
    TenKho VARCHAR(100),
    ViTri VARCHAR(100),
    NhanVienID INT,
    FOREIGN KEY (NhanVienID) REFERENCES nhanvien(NhanVienID)
);

-- 5. NGUYÊN LIỆU (mỗi nguyên liệu thuộc 1 kho)
CREATE TABLE nguyenlieu (
    NguyenLieuID INT AUTO_INCREMENT PRIMARY KEY,
    TenNguyenLieu VARCHAR(100),
    DonVi VARCHAR(50),
    SoLuong INT,
    KhoID INT,
    FOREIGN KEY (KhoID) REFERENCES kho(KhoID)
);

-- 6. BÀN ĂN
CREATE TABLE banan (
    BanAnID INT AUTO_INCREMENT PRIMARY KEY,
    SoBan INT,
    TrangThai VARCHAR(50)
);

CREATE TABLE luotdatban (
    LuotDatBanID INT AUTO_INCREMENT PRIMARY KEY,
    KhachHangID INT ,
    
    BanAnID INT ,
    ThoiGianDat DATETIME,
    FOREIGN KEY (KhachHangID) REFERENCES khachhang(KhachHangID),
    FOREIGN KEY (BanAnID) REFERENCES banan(BanAnID)
);

-- 8. PHẢN HỒI (1 khách có thể gửi nhiều phản hồi)
CREATE TABLE phanhoi (
    PhanHoiID INT AUTO_INCREMENT PRIMARY KEY,
    KhachHangID INT,
    NoiDung TEXT,
    FOREIGN KEY (KhachHangID) REFERENCES khachhang(KhachHangID)
);

-- 9. MÓN ĂN
CREATE TABLE monan (
    MonAnID INT AUTO_INCREMENT PRIMARY KEY,
    TenMonAn VARCHAR(100),
    Gia DECIMAL(10, 2),
    Loai VARCHAR(50)
);

-- 10. HÓA ĐƠN (mỗi hóa đơn thuộc 1 khách và 1 nhân viên)
CREATE TABLE hoadon (
    HoaDonID INT AUTO_INCREMENT PRIMARY KEY,
    NhanVienID INT,
    KhachHangID INT,
    ThoiDiemTao DATETIME,
    TongTien DECIMAL(10, 2),
    FOREIGN KEY (NhanVienID) REFERENCES nhanvien(NhanVienID),
    FOREIGN KEY (KhachHangID) REFERENCES khachhang(KhachHangID)
);

-- 11. CHI TIẾT HÓA ĐƠN (N-N giữa món ăn và hóa đơn)
CREATE TABLE chitiet_hoadon (
    HoaDonID INT,
    MonAnID INT,
    SoLuongMonAn INT,
    Gia DECIMAL(10, 2),
    ThanhTien DECIMAL(10, 2),
    PRIMARY KEY (HoaDonID, MonAnID),
    FOREIGN KEY (HoaDonID) REFERENCES hoadon(HoaDonID) ON DELETE CASCADE,
    FOREIGN KEY (MonAnID) REFERENCES monan(MonAnID)
);

INSERT INTO khachhang (HoTenKhachHang, SoDienThoai) VALUES
('Nguyễn Văn A', '0901000001'),
('Trần Thị B', '0901000002'),
('Lê Văn C', '0901000003'),
('Phạm Thị D', '0901000004'),
('Hoàng Văn E', '0901000005'),
('Đỗ Thị F', '0901000006'),
('Vũ Văn G', '0901000007'),
('Ngô Thị H', '0901000008'),
('Bùi Văn I', '0901000009'),
('Đặng Thị J', '0901000010');
INSERT INTO nhanvien (HoTenNhanVien, VaiTro, SoDienThoai) VALUES
('Nguyễn Nhân 1', 'Phục vụ', '0912000001'),
('Trần Nhân 2', 'Bếp trưởng', '0912000002'),
('Lê Nhân 3', 'Thu ngân', '0912000003'),
('Phạm Nhân 4', 'Phục vụ', '0912000004'),
('Hoàng Nhân 5', 'Thủ kho', '0912000005'),
('Đỗ Nhân 6', 'Phục vụ', '0912000006'),
('Vũ Nhân 7', 'Bếp phụ', '0912000007'),
('Ngô Nhân 8', 'Phục vụ', '0912000008'),
('Bùi Nhân 9', 'Thu ngân', '0912000009'),
('Đặng Nhân 10', 'Quản lý', '0912000010');
INSERT INTO lichlam (NhanVienID, SoGioLam, Ca, Ngay) VALUES
(1, 8, 'Sáng', '2025-07-01'),
(2, 6, 'Chiều', '2025-07-01'),
(3, 8, 'Tối', '2025-07-01'),
(4, 4, 'Sáng', '2025-07-01'),
(5, 8, 'Chiều', '2025-07-01'),
(6, 6, 'Tối', '2025-07-01'),
(7, 8, 'Sáng', '2025-07-01'),
(8, 4, 'Chiều', '2025-07-01'),
(9, 6, 'Tối', '2025-07-01'),
(10, 8, 'Sáng', '2025-07-01');
INSERT INTO kho (TenKho, ViTri, NhanVienID) VALUES
('Kho Bếp chính', 'Tầng 1', 1),
('Kho Chính', 'Tầng 2', 2),
('Kho Dự phòng', 'Tầng 3', 3),
('Kho Thực phẩm tươi', 'Tầng 4', 4),
('Kho Gia vị', 'Tầng 5', 5),
('Kho Bếp chính', 'Tầng 6', 6),
('Kho Pha chế', 'Tầng 7', 7),
('Kho Bảo quản', 'Tầng 8', 8),
('Kho Đồ uống', 'Tầng 9', 9),
('Kho Tráng miệng', 'Tầng 10', 10);

INSERT INTO nguyenlieu (TenNguyenLieu, DonVi, SoLuong, KhoID) VALUES
('Thịt bò', 'kg', 20, 1),
('Thịt gà', 'kg', 15, 2),
('Rau cải', 'kg', 10, 3),
('Cà rốt', 'kg', 12, 4),
('Khoai tây', 'kg', 18, 5),
('Hành tây', 'kg', 14, 6),
('Tỏi', 'kg', 8, 7),
('Ớt', 'kg', 6, 8),
('Muối', 'kg', 25, 9),
('Đường', 'kg', 30, 10);
INSERT INTO banan (SoBan, TrangThai) VALUES
(1, 'Trống'),
(2, 'Đã đặt'),
(3, 'Trống'),
(4, 'Đang sử dụng'),
(5, 'Trống'),
(6, 'Đã đặt'),
(7, 'Trống'),
(8, 'Đang sử dụng'),
(9, 'Trống'),
(10, 'Trống');
INSERT INTO luotdatban (KhachHangID, BanAnID, ThoiGianDat) VALUES
(1, 2, '2025-07-09 18:00:00'),
(2, 4, '2025-07-09 19:00:00'),
(3, 6, '2025-07-09 20:00:00'),
(4, 8, '2025-07-09 18:30:00'),
(5, 1, '2025-07-09 17:00:00'),
(6, 3, '2025-07-09 19:30:00'),
(7, 5, '2025-07-09 20:30:00'),
(8, 7, '2025-07-09 21:00:00'),
(9, 9, '2025-07-09 18:15:00'),
(10, 10, '2025-07-09 19:45:00');
INSERT INTO phanhoi (KhachHangID, NoiDung) VALUES
(1, 'Dịch vụ rất tốt!'),
(2, 'Món ăn ngon, phục vụ nhanh.'),
(3, 'Không gian đẹp, sạch sẽ.'),
(4, 'Giá hơi cao.'),
(5, 'Sẽ quay lại lần sau.'),
(6, 'Nhân viên thân thiện.'),
(7, 'Thực đơn đa dạng.'),
(8, 'Chờ món hơi lâu.'),
(9, 'Rất hài lòng.'),
(10, 'Cần cải thiện món tráng miệng.');
INSERT INTO monan (TenMonAn, Gia, Loai) VALUES
('Phở bò', 50000, 'Món chính'),
('Cơm gà', 45000, 'Món chính'),
('Bún chả', 40000, 'Món chính'),
('Gỏi cuốn', 30000, 'Khai vị'),
('Chả giò', 35000, 'Khai vị'),
('Canh chua', 40000, 'Món chính'),
('Lẩu thái', 150000, 'Món chính'),
('Trà đá', 5000, 'Đồ uống'),
('Nước cam', 20000, 'Đồ uống'),
('Kem dừa', 25000, 'Tráng miệng');
INSERT INTO hoadon (NhanVienID, KhachHangID, ThoiDiemTao, TongTien) VALUES
(1, 1, '2025-07-09 19:00:00', 100000),
(2, 2, '2025-07-09 19:30:00', 85000),
(3, 3, '2025-07-09 20:00:00', 120000),
(4, 4, '2025-07-09 20:30:00', 95000),
(5, 5, '2025-07-09 21:00:00', 110000),
(6, 6, '2025-07-09 21:30:00', 130000),
(7, 7, '2025-07-09 22:00:00', 70000),
(8, 8, '2025-07-09 22:30:00', 90000),
(9, 9, '2025-07-09 23:00:00', 105000),
(10, 10, '2025-07-09 23:30:00', 115000);
INSERT INTO chitiet_hoadon (HoaDonID, MonAnID, SoLuongMonAn, Gia, ThanhTien) VALUES
(1, 1, 2, 50000, 100000),
(2, 2, 1, 45000, 45000),
(3, 3, 3, 40000, 120000),
(4, 4, 2, 30000, 60000),
(5, 5, 2, 35000, 70000),
(6, 6, 1, 40000, 40000),
(7, 7, 1, 150000, 150000),
(8, 8, 3, 5000, 15000),
(9, 9, 2, 20000, 40000),
(10, 10, 2, 25000, 50000);
