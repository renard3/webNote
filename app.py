import pyodbc
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = '9999'
server = 'DESKTOP-A7E7KLS\SQLEXPRESS01'
database = 'Webnote'
username = 'sa'
password = '123456'
connection = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')

cursor = connection.cursor()

login_manager = LoginManager()
login_manager.login_view = 'dang_nhap'
login_manager.init_app(app)

class NguoiDung(UserMixin):
    def __init__(self, MaNguoiDung, TenNguoiDung, Email, MatKhau):
        self.MaNguoiDung = MaNguoiDung
        self.TenNguoiDung = TenNguoiDung
        self.Email = Email
        self.MatKhau = MatKhau

    def get_id(self):
        return str(self.Email)

class GhiChu:
    def __init__(self, MaGhiChu, TieuDe, NoiDung, NgayTaoGhiChu, MaNguoiDung):
        self.MaGhiChu = MaGhiChu
        self.TieuDe = TieuDe
        self.NoiDung = NoiDung
        self.NgayTaoGhiChu = NgayTaoGhiChu
        self.MaNguoiDung = MaNguoiDung
        
class CongViec:
    def __init__(self, MaCongViec, TieuDe, TrangThai, MaNguoiDung):
        self.MaCongViec = MaCongViec
        self.TieuDe = TieuDe
        self.TrangThai = TrangThai
        self.MaNguoiDung = MaNguoiDung

class SuKien:
    
    def __init__(self, MaSuKien, TieuDe, ThoiGianBatDau, ThoiGianKetThuc, MaNguoiDung):
        self.MaSuKien = MaSuKien
        self.TieuDe = TieuDe
        self.ThoiGianBatDau = ThoiGianBatDau
        self.ThoiGianKetThuc = ThoiGianKetThuc
        self.MaNguoiDung = MaNguoiDung
    
    def to_dict(self):
        return {
            'MaSuKien': self.MaSuKien,
            'TieuDe': self.TieuDe,
            'ThoiGianBatDau':  self.ThoiGianBatDau,
            'ThoiGianKetThuc': self.ThoiGianKetThuc,
            'MaNguoiDung': self.MaNguoiDung
        }

def thoiGianTruoc(thoiGianTao):
    
    thoiGianHienTai = datetime.utcnow()
    thoiGianLech = thoiGianHienTai - thoiGianTao

    if thoiGianLech < timedelta(minutes=1):
        return "vài giây trước"
    elif thoiGianLech < timedelta(hours=1):
        phut = thoiGianLech.seconds // 60
        return f"{phut} phút trước"
    elif thoiGianLech < timedelta(days=1):
        gio = thoiGianLech.seconds // 3600
        return f"{gio} giờ trước"
    else:
        ngay = thoiGianLech.days
        return f"{ngay} ngày trước"

@login_manager.user_loader
def layNguoiDung(email):
    cursor.execute("SELECT * FROM NguoiDung WHERE Email = ?", (email,))
    nguoiDungDangNhap = cursor.fetchone()
    if nguoiDungDangNhap:
        nguoiDung = NguoiDung(*nguoiDungDangNhap)
        return nguoiDung
    return None

@app.route('/')
def trang_chu():
    
    if not current_user.is_authenticated:
        flash('Vui lòng đăng nhập để truy cập trang!', 'danger')
        return redirect(url_for('dang_nhap'))
    
    cursor.execute(f"SELECT * FROM GhiChu WHERE MaNguoiDung = {current_user.MaNguoiDung} ORDER BY NgayTaoGhiChu DESC")
    duLieuGhiChu = cursor.fetchall()
    ghiChuNguoiDung = [GhiChu(*ghiChu) for ghiChu in duLieuGhiChu]

    cursor.execute(f"SELECT * FROM CongViec WHERE MaNguoiDung = {current_user.MaNguoiDung}")
    duLieuCongViec = cursor.fetchall()
    congViecNguoiDung = [CongViec(*congViec) for congViec in duLieuCongViec]

    cursor.execute(f"SELECT * FROM SuKien WHERE MaNguoiDung = {current_user.MaNguoiDung}")
    duLieuSuKien = cursor.fetchall()
    suKienNguoiDung = [SuKien(*suKien) for suKien in duLieuSuKien]

    return render_template('trang_chu.html', ghiChuNguoiDung=ghiChuNguoiDung,  thoiGianTruoc=thoiGianTruoc, congViecNguoiDung=congViecNguoiDung, suKienNguoiDung=suKienNguoiDung)

@app.route('/dang_ky', methods=['GET', 'POST'])
def dang_ky():
    
    if request.method == 'POST':
        
        tenNguoiDung = request.form['ten_nguoi_dung']
        email = request.form['email']
        matKhau = request.form['mat_khau']

        cursor.execute(f"SELECT * FROM NguoiDung WHERE Email = '{email}'")
        nguoiDungTonTai = cursor.fetchone()
        
        if nguoiDungTonTai:
            flash('Email đã tồn tại!', 'danger')
            return redirect(url_for('dang_ky'))

        matKhauBam = generate_password_hash(matKhau, method='sha256')
        cursor.execute(f"INSERT INTO NguoiDung (TenNguoiDung, Email, MatKhau) VALUES (?, ?, ?)", (tenNguoiDung, email, matKhauBam))
        connection.commit()

        flash('Tạo tài khoản thành công!', 'success')
        return redirect(url_for('dang_nhap'))

    return render_template('dang_ky.html')

@app.route('/dang_nhap', methods=['GET', 'POST'])
def dang_nhap():
    
    if request.method == 'POST':
        
        email = request.form['email']
        matKhau = request.form['mat_khau']

        cursor.execute(f"SELECT * FROM NguoiDung WHERE Email = '{email}'")
        duLieuNguoiDung = cursor.fetchone()
        
        if duLieuNguoiDung and check_password_hash(duLieuNguoiDung.MatKhau, matKhau):
            nguoiDung = NguoiDung(*duLieuNguoiDung)
           
            login_user(nguoiDung)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('trang_chu'))
        else:
            flash('Đăng nhập thất bại!', 'danger')

    return render_template('dang_nhap.html')

@app.route('/dang_xuat')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dang_nhap'))

@app.route('/ghi_chu', methods=['GET', 'POST'])
@login_required
def ghi_chu():
    
    if request.method == 'POST':
        
        action = request.form.get('action')
        ma_ghi_chu = request.form.get('ma_ghi_chu')  # Lấy giá trị ma_ghi_chu từ trường input ẩn
        tieu_de = request.form.get('tieu_de')
        noi_dung = request.form.get('noi_dung')

        if action == 'add':
            
            # Thêm ghi chú mới
            if tieu_de and noi_dung:
                cursor.execute("INSERT INTO GhiChu (TieuDe, NoiDung, NgayTaoGhiChu, MaNguoiDung) VALUES (?, ?, ?, ?)",
                               (tieu_de, noi_dung, datetime.utcnow(), current_user.MaNguoiDung))
                connection.commit()
                flash('Thêm ghi chú thành công!', 'success')
            else:
                flash('Tiêu đề và nội dung không được để trống!', 'danger')
        
        elif action == 'save':
            
            # Lưu ghi chú đã chỉnh sửa
            if ma_ghi_chu and tieu_de and noi_dung:
                cursor.execute("UPDATE GhiChu SET TieuDe = ?, NoiDung = ? WHERE MaGhiChu = ? AND MaNguoiDung = ?",
                               (tieu_de, noi_dung, ma_ghi_chu, current_user.MaNguoiDung))
                connection.commit()
                flash('Chỉnh sửa ghi chú thành công!', 'success')
            else:
                flash('Tiêu đề và nội dung không được để trống!', 'danger')
        
        elif action == 'delete':
            
            # Xóa ghi chú
            if ma_ghi_chu:
                cursor.execute("DELETE FROM GhiChu WHERE MaGhiChu = ? AND MaNguoiDung = ?",
                               (ma_ghi_chu, current_user.MaNguoiDung))
                connection.commit()
                flash('Đã xóa ghi chú thành công!', 'success')

    cursor.execute(f"SELECT * FROM GhiChu WHERE MaNguoiDung = {current_user.MaNguoiDung} ORDER BY NgayTaoGhiChu DESC")
    du_lieu_ghi_chu = cursor.fetchall()
    ghi_chu_nguoi_dung = [GhiChu(*ghi_chu) for ghi_chu in du_lieu_ghi_chu]

    return render_template('ghi_chu.html', ghiChuNguoiDung=ghi_chu_nguoi_dung, thoiGianTruoc=thoiGianTruoc)

@app.route('/xoa_ghi_chu/<int:ma_ghi_chu>', methods=['POST'])
@login_required
def xoa_ghi_chu(ma_ghi_chu):
    cursor.execute("DELETE FROM GhiChu WHERE MaGhiChu = ?", (ma_ghi_chu,))
    connection.commit()
    flash('Đã xóa ghi chú thành công!', 'success')
    return redirect(url_for('ghi_chu'))

@app.route('/cong_viec', methods=['GET', 'POST'])
@login_required
def cong_viec():
    
    if request.method == 'POST':
        
        action = request.form.get('action')
        ma_cong_viec = request.form.get('ma_cong_viec')  
        tieu_de = request.form.get('tieu_de')
        trang_thai = request.form.get('trang_thai')
        
        if action == 'add':
            
            # Thêm công việc mới
            if tieu_de:
                cursor.execute("INSERT INTO CongViec (TieuDe, TrangThai, MaNguoiDung) VALUES (?, ?, ?)",
                               (tieu_de, 'Đang thực hiện', current_user.MaNguoiDung))
                connection.commit()
                flash('Thêm công việc thành công!', 'success')
            else:
                flash('Tiêu đề không được để trống!', 'danger')
        
        elif action == 'save':
            
            # Lưu công việc đã chỉnh sửa
            if ma_cong_viec and tieu_de:
                cursor.execute("UPDATE CongViec SET TieuDe = ?, TrangThai = ? WHERE MaCongViec = ? AND MaNguoiDung = ?",
                               (tieu_de, trang_thai, ma_cong_viec, current_user.MaNguoiDung))
                connection.commit()
                flash('Chỉnh sửa công việc thành công!', 'success')
            else:
                flash('Tiêu đề không được để trống!', 'danger')

    cursor.execute(f"SELECT * FROM CongViec WHERE MaNguoiDung = {current_user.MaNguoiDung}")
    duLieuCongViec = cursor.fetchall()
    congViecNguoiDung = [CongViec(*congViec) for congViec in duLieuCongViec]

    return render_template('cong_viec.html', congViecNguoiDung=congViecNguoiDung)

@app.route('/xoa_cong_viec/<int:ma_cong_viec>', methods=['POST'])
@login_required
def xoa_cong_viec(ma_cong_viec):
    
    cursor.execute("DELETE FROM CongViec WHERE MaCongViec = ?", (ma_cong_viec,))
    connection.commit()
    flash('Đã xóa công việc thành công!', 'success')
    return redirect(url_for('cong_viec'))

@app.route('/su_kien', methods=['GET', 'POST'])
@login_required
def su_kien():
    
    if request.method == 'POST':
        
        tieuDe = request.form.get('tieu_de')
        thoiGianBatDau = request.form.get('thoi_gian_bat_dau')
        thoiGianKetThuc = request.form.get('thoi_gian_ket_thuc')
        
        if tieuDe and thoiGianBatDau and thoiGianKetThuc:
            cursor.execute("INSERT INTO SuKien (TieuDe, ThoiGianBatDau, ThoiGianKetThuc, MaNguoiDung) VALUES (?, ?, ?, ?)",
                           (tieuDe, thoiGianBatDau, thoiGianKetThuc, current_user.MaNguoiDung))
            connection.commit()
            flash('Thêm sự kiện thành công!', 'success')
        
        else:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
    
    cursor.execute(f"SELECT * FROM SuKien WHERE MaNguoiDung = {current_user.MaNguoiDung}")
    duLieuSuKien = cursor.fetchall()
    suKienNguoiDung = [SuKien(*suKien) for suKien in duLieuSuKien]
    
    suKien_dict_list = [suKien.to_dict() for suKien in suKienNguoiDung]

    return render_template('su_kien.html', suKienNguoiDung=suKien_dict_list)  

@app.route('/xoa_su_kien/<int:ma_su_kien>', methods=['POST'])
@login_required  
def xoa_su_kien(ma_su_kien):

    cursor.execute("DELETE FROM SuKien WHERE MaSuKien = ? AND MaNguoiDung = ?", (ma_su_kien, current_user.MaNguoiDung))
    connection.commit()

    flash('Đã xóa sự kiện thành công!', 'success')

    return redirect(url_for('su_kien'))

if __name__ == '__main__':
    app.run(debug=True)
