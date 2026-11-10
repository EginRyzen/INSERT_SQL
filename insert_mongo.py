"""
Bulk CSV Inserter ke MongoDB - kyc_data database
Insert ~6,4 juta baris dari data.csv ke koleksi 'taxi_trips' di MongoDB Lokal.
"""

import csv
import time
from pymongo import MongoClient

# ─────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────
MONGO_URI       = "mongodb://localhost:27017/"
DB_NAME         = "kyc_data"
COLLECTION_NAME = "taxi_trips"
CSV_FILE        = r"c:\Kuliah\Semester 5\BIG DATA\INSERT_SQL\data.csv"
BATCH_SIZE      = 20_000   # batch dokumen per insert_many


def parse_val(col, val):
    val = val.strip()
    if val == "":
        return None
    
    # Konversi tipe data agar tidak semua string
    if col in ("VendorID", "passenger_count", "RatecodeID", "PULocationID", "DOLocationID", "payment_type"):
        try:
            return int(val)
        except ValueError:
            return val
    elif col in ("trip_distance", "fare_amount", "extra", "mta_tax", "tip_amount", 
                 "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge"):
        try:
            return float(val)
        except ValueError:
            return val
    return val


def main():
    print("=" * 60)
    print("  Bulk Insert MongoDB: data.csv")
    print(f"  Target Database   : {DB_NAME}")
    print(f"  Target Collection : {COLLECTION_NAME}")
    print(f"  Batch Size        : {BATCH_SIZE:,} dokumen")
    print("=" * 60)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print("[OK] Terhubung ke MongoDB Server (localhost:27017).")
    print("Memulai proses pembacaan CSV dan insert...\n")

    start_time = time.time()
    total_inserted = 0
    batch = []

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = {col: parse_val(col, val) for col, val in row.items()}
            batch.append(doc)

            if len(batch) >= BATCH_SIZE:
                collection.insert_many(batch, ordered=False)
                total_inserted += len(batch)
                batch = []

                elapsed = time.time() - start_time
                rate = total_inserted / elapsed if elapsed > 0 else 0
                print(f"  >> {total_inserted:>10,} dokumen  |  {rate:,.0f} docs/s  |  {elapsed:.1f}s", end="\r")

        # Insert sisa batch terakhir
        if batch:
            collection.insert_many(batch, ordered=False)
            total_inserted += len(batch)

    elapsed = time.time() - start_time
    rate = total_inserted / elapsed if elapsed > 0 else 0

    print(f"\n\n{'=' * 60}")
    print("  SELESAI INSERT KE MONGODB!")
    print(f"  Total dokumen masuk : {total_inserted:,}")
    print(f"  Waktu total         : {elapsed:.1f} detik ({elapsed/60:.1f} menit)")
    print(f"  Kecepatan rata-rata : {rate:,.0f} docs/detik")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()

