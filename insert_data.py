"""
Bulk CSV Inserter ke MySQL - kyc_data database
Insert ~6 juta baris dari data.csv secara efisien menggunakan batch insert.
"""

import csv
import time
import mysql.connector
from mysql.connector import Error

# ─────────────────────────────────────────────
# KONFIGURASI — sesuaikan jika perlu
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",        # ganti jika bukan root
    "password": "",            # ganti jika ada password
    "database": "kyc_data",
    "allow_local_infile": True,
}

CSV_FILE   = r"c:\Kuliah\Semester 5\BIG DATA\INSERT_SQL\data.csv"
TABLE_NAME = "taxi_trips"
BATCH_SIZE = 10_000          # jumlah baris per commit (bisa dinaikkan jika RAM cukup)

# ─────────────────────────────────────────────
# DDL — buat tabel jika belum ada
# ─────────────────────────────────────────────
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
    `id`                     BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `VendorID`               TINYINT,
    `tpep_pickup_datetime`   DATETIME,
    `tpep_dropoff_datetime`  DATETIME,
    `passenger_count`        TINYINT,
    `trip_distance`          FLOAT,
    `RatecodeID`             TINYINT,
    `store_and_fwd_flag`     CHAR(1),
    `PULocationID`           SMALLINT,
    `DOLocationID`           SMALLINT,
    `payment_type`           TINYINT,
    `fare_amount`            FLOAT,
    `extra`                  FLOAT,
    `mta_tax`                FLOAT,
    `tip_amount`             FLOAT,
    `tolls_amount`           FLOAT,
    `improvement_surcharge`  FLOAT,
    `total_amount`           FLOAT,
    `congestion_surcharge`   FLOAT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

# ─────────────────────────────────────────────
# INSERT SQL (placeholder per baris)
# ─────────────────────────────────────────────
COLUMNS = [
    "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
    "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag",
    "PULocationID", "DOLocationID", "payment_type", "fare_amount",
    "extra", "mta_tax", "tip_amount", "tolls_amount",
    "improvement_surcharge", "total_amount", "congestion_surcharge",
]

col_list   = ", ".join(f"`{c}`" for c in COLUMNS)
placeholder = ", ".join(["%s"] * len(COLUMNS))
INSERT_SQL  = f"INSERT INTO `{TABLE_NAME}` ({col_list}) VALUES ({placeholder})"


def sanitize(value: str):
    """Ubah string kosong jadi None agar tersimpan sebagai NULL."""
    v = value.strip()
    return None if v == "" else v


def main():
    print("=" * 60)
    print(f"  Bulk Insert: {CSV_FILE}")
    print(f"  Target     : {DB_CONFIG['database']}.{TABLE_NAME}")
    print(f"  Batch size : {BATCH_SIZE:,} rows")
    print("=" * 60)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("[OK] Koneksi ke MySQL berhasil.\n")
    except Error as e:
        print(f"[ERROR] Gagal konek ke MySQL: {e}")
        return

    # Nonaktifkan cek FK & autocommit untuk performa
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("SET UNIQUE_CHECKS = 0;")
    cursor.execute("SET sql_log_bin = 0;")
    conn.autocommit = False

    # Buat tabel jika belum ada
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    print(f"[OK] Tabel `{TABLE_NAME}` siap.\n")

    start_time  = time.time()
    total_rows  = 0
    batch       = []
    error_count = 0

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                record = tuple(sanitize(row[col]) for col in COLUMNS)
                batch.append(record)
            except KeyError as ke:
                print(f"[WARN] Kolom tidak ditemukan: {ke} — baris dilewati.")
                error_count += 1
                continue

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(INSERT_SQL, batch)
                conn.commit()
                total_rows += len(batch)
                batch = []

                elapsed = time.time() - start_time
                rate    = total_rows / elapsed if elapsed > 0 else 0
                print(f"  >> {total_rows:>10,} baris  |  {rate:,.0f} rows/s  |  {elapsed:.1f}s", end="\r")

        # Sisa batch terakhir
        if batch:
            cursor.executemany(INSERT_SQL, batch)
            conn.commit()
            total_rows += len(batch)

    elapsed = time.time() - start_time
    rate    = total_rows / elapsed if elapsed > 0 else 0

    print(f"\n\n{'=' * 60}")
    print(f"  SELESAI!")
    print(f"  Total baris inserted : {total_rows:,}")
    print(f"  Error/skip           : {error_count:,}")
    print(f"  Waktu total          : {elapsed:.1f} detik ({elapsed/60:.1f} menit)")
    print(f"  Rata-rata kecepatan  : {rate:,.0f} rows/detik")
    print("=" * 60)

    # Kembalikan setting MySQL
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    cursor.execute("SET UNIQUE_CHECKS = 1;")
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
