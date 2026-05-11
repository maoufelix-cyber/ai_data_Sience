# Arsitektur Proyek

## 1. Overview
Proyek ini dibangun sebagai pipeline end-to-end:
- Pengumpulan data
- Praproses dan pembersihan
- Eksplorasi data
- Rekayasa fitur
- Pelatihan model
- Evaluasi model
- Deployment aplikasi interaktif

## 2. Struktur Komponen
- `data/raw/`: lokasi dataset asli.
- `data/processed/`: dataset yang sudah dibersihkan dan siap model.
- `notebooks/`: laporan interaktif Jupyter Notebook.
- `src/`: modul Python untuk pipeline, fitur, dan model.
- `app/`: aplikasi deployment Streamlit.
- `models/`: model tersimpan.
- `reports/`: laporan dan grafik tambahan.

## 3. Alur Data
1. `src/data_pipeline.py` memuat dan membagi data.
2. `src/feature_engineering.py` membangun fitur turunan.
3. `src/model_pipeline.py` membuat pipeline scikit-learn dan mengevaluasi model.
4. `notebooks/01_project_end_to_end.ipynb` menjalankan analisis secara interaktif.
5. `app/streamlit_app.py` menggunakan model terlatih untuk prediksi realtime.

## 4. Deployment
- Gunakan Streamlit untuk antarmuka.
- Simpan model dengan `joblib` di `models/customer_churn_model.joblib`.
- Jalankan dengan:
  ```bash
  streamlit run app/streamlit_app.py
  ```
