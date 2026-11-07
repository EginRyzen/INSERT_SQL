# 📚 Panduan Lengkap SQL VIEW - Database `kyc_data`

Dokumen ini berisi kumpulan perintah SQL untuk **Membuat (CREATE)**, **Melihat / Menjalankan (SELECT)**, dan **Mengelola (DROP / ALTER)** VIEW table pada dataset taksi (`taxi_trips`).

---

## 📑 Daftar Isi
1. [Apa itu VIEW?](#-apa-itu-view)
2. [1. View Kesibukan Siang vs Malam](#1-view-kesibukan-siang-vs-malam)
3. [2. View Rekap Harian](#2-view-rekap-harian)
4. [3. View Performa Vendor](#3-view-performa-vendor)
5. [4. View Metode Pembayaran](#4-view-metode-pembayaran)
6. [5. View Kategori Jarak Perjalanan](#5-view-kategori-jarak-perjalanan)
7. [Perintah Tambahan (Mengubah & Menghapus View)](#-perintah-tambahan-mengubah--menghapus-view)
8. [Cara Menjalankan di phpMyAdmin](#-cara-menjalankan-di-phpmyadmin)

---

## 🔍 Apa itu VIEW?
**VIEW** adalah tabel virtual berbasis query `SELECT`. VIEW tidak menyimpan data secara fisik, melainkan menyimpan kueri SQL yang akan otomatis dieksekusi setiap kali VIEW dipanggil.

---

## 1. View Kesibukan Siang vs Malam

Membandingkan aktivitas taksi pada jam **Siang (06:00 - 18:00)** dan **Malam (18:00 - 06:00)**.

### 🛠️ Perintah Membuat (CREATE VIEW)
```sql
CREATE OR REPLACE VIEW view_kesibukan_siang_malam AS
SELECT 
    CASE 
        WHEN HOUR(tpep_pickup_datetime) >= 6 AND HOUR(tpep_pickup_datetime) < 18 THEN 'Siang (06:00 - 18:00)'
        ELSE 'Malam (18:00 - 06:00)'
    END AS waktu_operasional,
    COUNT(*) AS total_trip,
    SUM(passenger_count) AS total_penumpang,
    ROUND(AVG(passenger_count), 2) AS rata_rata_penumpang,
    ROUND(AVG(trip_distance), 2) AS rata_rata_jarak,
    ROUND(AVG(fare_amount), 2) AS rata_rata_tarif,
    ROUND(SUM(total_amount), 2) AS total_pendapatan
FROM taxi_trips
GROUP BY waktu_operasional;
```

### 👁️ Perintah Melihat (SELECT VIEW)
```sql
-- Menampilkan seluruh hasil siang vs malam
SELECT * FROM view_kesibukan_siang_malam;

-- Hanya melihat data siang hari
SELECT * FROM view_kesibukan_siang_malam 
WHERE waktu_operasional LIKE 'Siang%';

-- Hanya melihat data malam hari
SELECT * FROM view_kesibukan_siang_malam 
WHERE waktu_operasional LIKE 'Malam%';
```

---

## 2. View Rekap Harian

Merekapitulasi total trip, penumpang, tip, dan omset per tanggal.

### 🛠️ Perintah Membuat (CREATE VIEW)
```sql
CREATE OR REPLACE VIEW view_rekap_harian AS
SELECT 
    DATE(tpep_pickup_datetime) AS tanggal,
    COUNT(*) AS total_trip,
    SUM(passenger_count) AS total_penumpang,
    ROUND(AVG(trip_distance), 2) AS rata_rata_jarak,
    ROUND(SUM(tip_amount), 2) AS total_tip,
    ROUND(SUM(total_amount), 2) AS total_pendapatan
FROM taxi_trips
GROUP BY DATE(tpep_pickup_datetime)
ORDER BY tanggal ASC;
```

### 👁️ Perintah Melihat (SELECT VIEW)
```sql
-- Menampilkan 10 hari pertama
SELECT * FROM view_rekap_harian 
LIMIT 10;

-- Menampilkan rekap pada rentang tanggal tertentu (contoh: 1-7 Januari 2020)
SELECT * FROM view_rekap_harian 
WHERE tanggal BETWEEN '2020-01-01' AND '2020-01-07';

-- Menampilkan 5 hari dengan pendapatan tertinggi
SELECT * FROM view_rekap_harian 
ORDER BY total_pendapatan DESC 
LIMIT 5;
```

---

## 3. View Performa Vendor

Membandingkan performa antara Vendor 1 (Creative Mobile Technologies) dan Vendor 2 (VeriFone Inc.).

### 🛠️ Perintah Membuat (CREATE VIEW)
```sql
CREATE OR REPLACE VIEW view_performa_vendor AS
SELECT 
    CASE 
        WHEN VendorID = 1 THEN 'Vendor 1 (Creative Mobile Technologies)'
        WHEN VendorID = 2 THEN 'Vendor 2 (VeriFone Inc.)'
        ELSE CONCAT('Vendor ', IFNULL(VendorID, 'Unknown'))
    END AS nama_vendor,
    COUNT(*) AS total_trip,
    SUM(passenger_count) AS total_penumpang,
    ROUND(AVG(trip_distance), 2) AS rata_rata_jarak,
    ROUND(AVG(fare_amount), 2) AS rata_rata_tarif,
    ROUND(SUM(total_amount), 2) AS total_pendapatan
FROM taxi_trips
GROUP BY VendorID;
```

### 👁️ Perintah Melihat (SELECT VIEW)
```sql
-- Menampilkan performa seluruh vendor
SELECT * FROM view_performa_vendor;

-- Mengurutkan berdasarkan total pendapatan terbanyak
SELECT * FROM view_performa_vendor 
ORDER BY total_pendapatan DESC;
```

---

## 4. View Metode Pembayaran

Menganalisis penggunaan metode pembayaran (Kartu Kredit, Cash, Dispute, dll) serta total tip yang diperoleh.

### 🛠️ Perintah Membuat (CREATE VIEW)
```sql
CREATE OR REPLACE VIEW view_metode_pembayaran AS
SELECT 
    CASE 
        WHEN payment_type = 1 THEN 'Credit Card'
        WHEN payment_type = 2 THEN 'Cash'
        WHEN payment_type = 3 THEN 'No Charge'
        WHEN payment_type = 4 THEN 'Dispute'
        WHEN payment_type = 5 THEN 'Unknown'
        WHEN payment_type = 6 THEN 'Voided Trip'
        ELSE CONCAT('Lainnya (', IFNULL(payment_type, 'Null'), ')')
    END AS metode_pembayaran,
    COUNT(*) AS total_transaksi,
    ROUND(SUM(tip_amount), 2) AS total_tip,
    ROUND(AVG(tip_amount), 2) AS rata_rata_tip,
    ROUND(SUM(total_amount), 2) AS total_pendapatan
FROM taxi_trips
GROUP BY payment_type;
```

### 👁️ Perintah Melihat (SELECT VIEW)
```sql
-- Menampilkan semua metode pembayaran diurutkan dari transaksi terbanyak
SELECT * FROM view_metode_pembayaran 
ORDER BY total_transaksi DESC;

-- Melihat metode pembayaran yang memberikan tip
SELECT metode_pembayaran, total_tip, rata_rata_tip 
FROM view_metode_pembayaran 
WHERE total_tip > 0 
ORDER BY total_tip DESC;
```

---

## 5. View Kategori Jarak Perjalanan

Mengelompokkan perjalanan menjadi kategori **Dekat** (< 3 mil), **Sedang** (3 - 10 mil), dan **Jauh** (> 10 mil).

### 🛠️ Perintah Membuat (CREATE VIEW)
```sql
CREATE OR REPLACE VIEW view_kategori_jarak_trip AS
SELECT 
    CASE 
        WHEN trip_distance < 3 THEN 'Dekat (< 3 mil)'
        WHEN trip_distance BETWEEN 3 AND 10 THEN 'Sedang (3 - 10 mil)'
        ELSE 'Jauh (> 10 mil)'
    END AS kategori_jarak,
    COUNT(*) AS total_trip,
    ROUND(AVG(trip_distance), 2) AS rata_rata_jarak,
    ROUND(AVG(fare_amount), 2) AS rata_rata_tarif,
    ROUND(SUM(total_amount), 2) AS total_pendapatan
FROM taxi_trips
GROUP BY kategori_jarak;
```

### 👁️ Perintah Melihat (SELECT VIEW)
```sql
-- Menampilkan ringkasan kategori jarak
SELECT * FROM view_kategori_jarak_trip;

-- Urutkan berdasarkan kategori perjalanan terbanyak
SELECT * FROM view_kategori_jarak_trip 
ORDER BY total_trip DESC;
```

---

## ⚙️ Perintah Tambahan (Mengubah & Menghapus View)

### Menghapus VIEW jika sudah tidak dibutuhkan:
```sql
DROP VIEW IF EXISTS view_kesibukan_siang_malam;
DROP VIEW IF EXISTS view_rekap_harian;
DROP VIEW IF EXISTS view_performa_vendor;
DROP VIEW IF EXISTS view_metode_pembayaran;
DROP VIEW IF EXISTS view_kategori_jarak_trip;
```

### Memperbarui Definisi VIEW:
Gunakan klausa `CREATE OR REPLACE VIEW nama_view AS ...` seperti contoh di atas untuk memperbarui view yang sudah ada tanpa harus menghapusnya terlebih dahulu.

---

## 💻 Cara Menjalankan di phpMyAdmin
1. Buka browser dan akses **[phpMyAdmin kyc_data](http://localhost/phpmyadmin/index.php?route=/database/structure&db=kyc_data)**.
2. Pastikan database **`kyc_data`** terpilih.
3. Klik tab **SQL** di menu bagian atas.
4. Salin (copy) salah satu query **CREATE VIEW** atau **SELECT VIEW** di atas, lalu tempel (paste) ke dalam editor SQL.
5. Klik tombol **Kirim / Go** di pojok kanan bawah.
6. Hasil view akan langsung muncul di layar dan nama view akan tercantum di daftar tabel/view di menu navigasi sebelah kiri.

