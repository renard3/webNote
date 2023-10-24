CREATE DATABASE MaiNhatThanhTam;
GO

USE MaiNhatThanhTam;
GO

CREATE TABLE NguoiDung(
    MaNguoiDung INT PRIMARY KEY IDENTITY,
    TenNguoiDung NVARCHAR(50) NOT NULL,
    Email VARCHAR(50) NOT NULL UNIQUE,
    MatKhau VARCHAR(100) NOT NULL
);
GO

CREATE TABLE GhiChu(
    MaGhiChu INT PRIMARY KEY IDENTITY,
    TieuDe NVARCHAR(255) NOT NULL,
    NoiDung NTEXT NULL,
    NgayTaoGhiChu DATETIME DEFAULT GETDATE(),
    MaNguoiDung INT,
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung)
);
GO

CREATE TABLE Congviec(
    MaCongViec INT PRIMARY KEY IDENTITY,
    TieuDe NVARCHAR(255) NOT NULL,
    TrangThai NVARCHAR(20) CHECK (TrangThai IN (N'Hoàn thành', N'Đang thực hiện')),
    MaNguoiDung INT,
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung)
); 
GO

CREATE TABLE SuKien(
    MaSuKien INT PRIMARY KEY IDENTITY,
    TieuDe NVARCHAR(255) NOT NULL,
    ThoiGianBatDau DATETIME,
    ThoiGianKetThuc DATETIME,
    MaNguoiDung INT,
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung)
);
GO