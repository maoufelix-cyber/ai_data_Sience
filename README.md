# Proyek Data Science End-to-End

Tema Proyek: Prediksi Churn Pelanggan E-Commerce
Tujuan: Meningkatkan retensi pelanggan dengan memprediksi pelanggan yang berisiko berhenti berlangganan.

## 1. Problem Statement
Pelanggan yang berhenti membeli produk menyebabkan penurunan pendapatan. Proyek ini bertujuan untuk membangun model prediksi churn sehingga tim bisnis dapat melakukan intervensi yang tepat.

## 2. Business Understanding
- **Sasaran bisnis:** Identifikasi pelanggan yang cenderung churn.
- **Manfaat:** Mengurangi biaya perolehan pelanggan baru, meningkatkan nilai umur pelanggan (LTV), dan membuat program loyalitas yang lebih baik.
- **Pengguna akhir:** Tim pemasaran, manajemen produk, dan tim retensi.

## 3. Data Collection
- Dataset dapat diunggah ke folder `data/raw/`.
- Data yang ideal terdiri dari: demografi pelanggan, riwayat transaksi, frekuensi pembelian, interaksi layanan pelanggan, dan status churn.
- Jika belum tersedia, implementasi ini menggunakan data sintetis untuk demonstrasi.

## 4. Data Preprocessing
- Membersihkan nilai hilang.
- Menangani outlier.
- Encoding variabel kategorikal.
- Standardisasi fitur numerik.

## 5. Exploratory Data Analysis
- Analisis distribusi fitur utama.
- Korelasi antar fitur.
- Visualisasi churn terhadap fitur penting.

## 6. Feature Engineering
- Membuat fitur turunan dari frekuensi pembelian, total transaksi, durasi keanggotaan, dan rasio engagement.
- Memilih fitur paling berpengaruh menggunakan teknik domain knowledge dan korelasi.

## 7. Model Building
- Model baseline: Logistic Regression.
- Model lanjutan: Random Forest.
- Pipeline scikit-learn untuk preprocessing + modeling.

## 8. Model Evaluation
- Metode evaluasi: Confusion matrix, ROC AUC, precision, recall, f1-score.
- Cross-validation untuk validasi model.
- Analisis business metric untuk menentukan threshold.

## 9. Deployment
- Aplikasi deployment menggunakan Streamlit.
- Model disimpan dengan `joblib` di folder `models/`.
- Streamlit membaca model dan menampilkan prediksi interaktif.

## 10. Dashboard
- Dashboard visualisasi performa model.
- Dashboard prediksi pelanggan churn.
- Tampilan summary metrik performa.

## 11. Dokumentasi GitHub
- `README.md` sebagai dokumentasi utama.
- `docs/architecture.md` menjelaskan arsitektur proyek.
- `notebooks/01_project_end_to_end.ipynb` sebagai laporan eksplorasi dan modeling.

## 12. Struktur Folder Proyek
```
Ai_data sience/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── 01_project_end_to_end.ipynb
├── src/
│   ├── data_pipeline.py
│   ├── feature_engineering.py
│   └── model_pipeline.py
├── app/
│   └── streamlit_app.py
├── models/
│   └── customer_churn_model.joblib
├── reports/
└── docs/
    └── architecture.md
```

## Quick Start
1. Buat environment Python baru.
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan notebook di `notebooks/01_project_end_to_end.ipynb`.
4. Untuk deployment lokal:
   ```bash
   streamlit run app/streamlit_app.py
   ```

## Best Practice Industri
- Gunakan source control (Git) dan branch terpisah untuk eksperimen.
- Simpan dataset asli di `data/raw/` dan hasil bersih di `data/processed/`.
- Pisahkan preprocessing, feature engineering, dan modeling dalam modul berbeda.
- Dokumentasikan asumsi data, batasan, dan langkah validasi.
- Gunakan `requirements.txt` untuk dependensi eksplisit.
