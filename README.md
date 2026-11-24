# Beijing Air Quality Data Analysis & Dashboard 🌫️

Proyek akhir **Belajar Analisis Data dengan Python** menggunakan **Air Quality Dataset (Beijing Multi-Site 2013–2017)** yang mencakup 12 stasiun pemantauan.

## Struktur Direktori
```
submission/
├── dashboard/
│   ├── main_data.csv       # Data bersih agregasi harian per stasiun
│   └── dashboard.py        # Aplikasi dashboard interaktif Streamlit
├── data/                   # 12 berkas CSV dataset mentah PRSA_Data
├── notebook.ipynb          # Notebook analisis data lengkap (sudah dijalankan)
├── README.md               # Panduan proyek dan cara menjalankan dashboard
├── requirements.txt        # Daftar dependensi Python
└── url.txt                 # Tautan deployment Streamlit Community Cloud
```

## Setup Environment

### Menggunakan Anaconda
```bash
conda create --name main-ds python=3.10
conda activate main-ds
pip install -r requirements.txt
```

### Menggunakan Shell / Terminal (venv)
```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## Menjalankan Dashboard Streamlit
Pastikan berada di direktori root proyek (`submission/`), lalu jalankan perintah berikut:
```bash
streamlit run dashboard/dashboard.py
```
Dashboard akan otomatis terbuka di browser pada alamat lokal `http://localhost:8501`.
