"""
═══════════════════════════════════════════════════════════════════════════
  SETUP GUIDE: DATA CSV & CONFIG STREAMLIT
  Churn Intelligence - AI Data Science Project
═══════════════════════════════════════════════════════════════════════════
"""

SETUP_GUIDE = """

╔═══════════════════════════════════════════════════════════════════════╗
║                     PART 1: SETUP DATA CSV                           ║
╚═══════════════════════════════════════════════════════════════════════╝

Anda punya 3 OPSI untuk setup data CSV:

┌─────────────────────────────────────────────────────────────────────┐
│ OPSI 1: ✅ GUNAKAN DATA SYNTHETIC YANG SUDAH ADA (RECOMMENDED)     │
└─────────────────────────────────────────────────────────────────────┘

Status:       ✅ SUDAH SIAP
File:         data/raw/customers.csv
Records:      2000 pelanggan
Type:         Synthetic (demo data)
Persiapan:    TIDAK PERLU (langsung bisa pakai)

Langkah:
  1. Tidak perlu lakukan apa-apa!
  2. Langsung jalankan app:
     
     streamlit run app/streamlit_app.py
  
  3. App akan otomatis load data dari customers.csv

Cocok untuk:
  ✓ Demo/testing
  ✓ Development
  ✓ Understanding flow tanpa data real
  ✓ Training team

Keunggulan:
  ✓ Tidak perlu persiapan
  ✓ Data sudah bersih
  ✓ Churn pattern sudah realistic
  ✓ Ready to go dalam 1 menit


┌─────────────────────────────────────────────────────────────────────┐
│ OPSI 2: GENERATE ULANG DATA SYNTHETIC DENGAN CUSTOM JUMLAH         │
└─────────────────────────────────────────────────────────────────────┘

Gunakan jika: Ingin lebih banyak/sedikit records atau fresh data

Langkah:

  # 1. Lihat data sekarang
  python generate_data.py
  
  Output:
  ⚠️  File sudah ada: data/raw/customers.csv
     Records saat ini: 2000
  
  # 2. Generate 5000 records baru (ganti existing)
  python generate_data.py 5000 --replace
  
  Output:
  ✅ Data generated successfully!
     • Lokasi: data/raw/customers.csv
     • Total records: 5000
     • Churn rate: 60.0%
     • Kolom: customer_age, account_balance, tenure_months, ...
  
  # 3. Atau generate 10000 records
  python generate_data.py 10000 --replace

Cocok untuk:
  ✓ Ingin test dengan volume data lebih besar
  ✓ Perlu test scalability
  ✓ Ingin fresh synthetic data

Keuntungan vs Opsi 1:
  ✓ Flexible jumlah records
  ✓ Data baru (fresh patterns)
  ✓ Tetap synthetic (simple)


┌─────────────────────────────────────────────────────────────────────┐
│ OPSI 3: IMPORT DATASET REAL DARI LUAR                              │
└─────────────────────────────────────────────────────────────────────┘

Gunakan jika: Punya dataset real yang ingin dianalisis

Persiapan:

  1. Siapkan file CSV atau Excel Anda dengan kolom MINIMAL:
     - customer_age (int): Umur pelanggan
     - account_balance (float): Saldo akun
     - tenure_months (int): Bulan jadi pelanggan
     - total_transactions (int): Total transaksi
     - is_premium (str): "yes" atau "no"
     - support_tickets (int): Jumlah tiket
     - avg_order_value (float): Rata-rata order
     - churn (int): 0 atau 1

  2. Jika kolom Anda berbeda, siapkan mapping:
     Contoh jika dataset Anda pakai nama berbeda:
     
     column_mapping = {
         'Age': 'customer_age',
         'Balance': 'account_balance',
         'Tenure': 'tenure_months',
         ...
     }

Langkah Import:

  # 1. Lihat contoh column mapping untuk berbagai format
  python import_real_data.py --show-examples
  
  Output:
  ╔════════════════════════════════════════════════════════════════╗
  ║           CONTOH COLUMN MAPPING UNTUK FORMAT BERBEDA          ║
  ╚════════════════════════════════════════════════════════════════╝
  
  Format 1: Kaggle Churn Dataset
  ─────────────────────────────
  column_mapping = {
      'Age': 'customer_age',
      'Balance': 'account_balance',
      'Tenure': 'tenure_months',
      ...
  }
  
  [Tampil contoh untuk berbagai format]

  # 2. Import file CSV
  python import_real_data.py data/raw/my_churn_data.csv
  
  # 3. Atau import file Excel
  python import_real_data.py data/raw/customers.xlsx
  
  # 4. Import dengan custom column mapping
  
  Edit import_real_data.py dan ubah section ini:
  
  if __name__ == "__main__":
      source = sys.argv[1] if len(sys.argv) > 1 else "data/raw/my_data.csv"
      
      column_mapping = {
          'Age': 'customer_age',
          'Balance': 'account_balance',
          'Tenure': 'tenure_months',
          'NumOfProducts': 'total_transactions',
          'IsActiveMember': 'is_premium',
          'NumTickets': 'support_tickets',
          'EstimatedSalary': 'avg_order_value',
          'Exited': 'churn'
      }
      
      import_real_data(source, column_mapping)

Cocok untuk:
  ✓ Production use dengan real data
  ✓ Analyze actual business churn
  ✓ Real insights untuk decision making

Keuntungan:
  ✓ Real data = actionable insights
  ✓ Authentic patterns
  ✓ Production-ready


╔═══════════════════════════════════════════════════════════════════════╗
║                  PART 2: SETUP CONFIG STREAMLIT                      ║
╚═══════════════════════════════════════════════════════════════════════╝

Lokasi:  .streamlit/config.toml
Status:  ✅ SUDAH OPTIMAL (tidak perlu diubah)

Current Config:
───────────────
[theme]
primaryColor = "#22d3ee"              # Cyan accent
backgroundColor = "#050816"           # Dark navy background
secondaryBackgroundColor = "#111928"  # Secondary dark
textColor = "#eef2ff"                 # Light gray text
font = "sans serif"

[browser]
gatherUsageStats = false              # Disable analytics

Perubahan CONFIG:

1. JIKA INGIN UBAH WARNA (OPTIONAL):
   
   Buka: .streamlit/config.toml
   
   Ubah theme section, contoh Blue Theme:
   
   [theme]
   primaryColor = "#0ea5e9"            # Sky blue
   backgroundColor = "#0f172a"         # Slate dark
   secondaryBackgroundColor = "#1e293b"
   textColor = "#f1f5f9"
   font = "sans serif"
   
   Simpan, aplikasi auto-reload

2. JIKA AKAN PRODUCTION DEPLOYMENT:
   
   Tambah ke config.toml:
   
   [server]
   port = 8501
   address = "0.0.0.0"        # Accessible from network
   headless = true
   enableXsrfProtection = true
   
   [client]
   maxUploadSize = 500        # 500 MB

3. JIKA INGIN DARI COMMAND LINE:
   
   streamlit run app/streamlit_app.py \\
     --server.port 8080 \\
     --server.address 0.0.0.0


╔═══════════════════════════════════════════════════════════════════════╗
║                        QUICK START CHECKLIST                         ║
╚═══════════════════════════════════════════════════════════════════════╝

Untuk mulai sekarang:

  ☐ 1. Data CSV - Pilih 1 opsi:
       ☐ Opsi 1: Gunakan data yang ada (RECOMMENDED)
         → Tidak perlu setup
       ☐ Opsi 2: Generate data baru
         → python generate_data.py 5000 --replace
       ☐ Opsi 3: Import data real
         → python import_real_data.py /path/to/your/data.csv

  ☐ 2. Config - Biarkan sebagaimana adanya
       → .streamlit/config.toml sudah optimal

  ☐ 3. Jalankan aplikasi:
       → .\.env\Scripts\Activate.ps1
       → streamlit run app/streamlit_app.py

  ☐ 4. Akses di browser:
       → http://localhost:8501


╔═══════════════════════════════════════════════════════════════════════╗
║                         TROUBLESHOOTING                              ║
╚═══════════════════════════════════════════════════════════════════════╝

Q: Data tidak ditemukan?
A: Pastikan data/raw/customers.csv ada. Jika tidak:
   python generate_data.py

Q: App tidak load dengan benar?
A: Check config.toml di .streamlit/
   Pastikan tidak ada syntax error (YAML format)

Q: Ingin upload custom data?
A: Gunakan import_real_data.py script
   python import_real_data.py /path/to/file.csv

Q: Data terlalu besar?
A: Batasi jumlah records:
   python generate_data.py 1000 --replace

Q: Warna tidak sesuai?
A: Edit .streamlit/config.toml theme section
   Restart streamlit app


═══════════════════════════════════════════════════════════════════════════
                           READY TO START!
═══════════════════════════════════════════════════════════════════════════

Pilih opsi data Anda, jalankan app, dan mulai analisis churn!

Status:
  ✅ Data CSV - ready (Opsi 1)
  ✅ Config - ready
  ✅ Semua dependencies - installed
  ✅ Scripts helper - ready (generate_data.py, import_real_data.py)

Jalankan sekarang:
  
  .\.env\Scripts\Activate.ps1
  streamlit run app/streamlit_app.py

═══════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(SETUP_GUIDE)
