# 📊 Proyek Analisis Penjualan ✨

Dashboard interaktif ini dibuat untuk menganalisis data penjualan e-commerce. Dirancang agar mudah dijalankan di **Visual Studio Code** dengan **Python** dan **Streamlit**.

---

## 🔧 Setup Environment (VS Code)

Ikuti langkah-langkah berikut untuk menyiapkan dan menjalankan proyek ini secara lokal di VS Code.

### 1. Kloning Repositori

Buka terminal pada PC atau Laptop (Windows Win + R, ketik "cmd" dan tekan Enter) (MacOS tekan Command + Space, ketik "Terminal", dan tekan Enter) lalu jalankan:

```bash
git clone https://github.com/08samudra/analisis_data_penjualan_e-commerce.git
```

Setelah proses cloning selesai, buka folder proyek secara otomatis di VS Code dengan perintah berikut:

```bash
code analisis_data_penjualan_e-commerce
```

Setelah itu tekan CTRL+` untuk membuka terminal pada folder proyek di dalam VS Code.
---

### 2. Buat dan Aktifkan Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

Jika muncul masalah terkait *Execution Policy*, jalankan PowerShell sebagai Administrator lalu ketik:

```powershell
Set-ExecutionPolicy RemoteSigned
```

Lalu tekan `Y`, dan coba aktivasi ulang.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> Setelah aktivasi berhasil, terminal Anda akan menampilkan `(.venv)` di awal baris.

---

### 3. Install Library yang Dibutuhkan

Pastikan virtual environment sudah aktif. Kemudian install seluruh library yang dibutuhkan melalui berkas `requirements.txt`:

```bash
pip install -r requirements.txt
```
Dan tunggu hingga proses selesai.

---

## 🚀 Jalankan Aplikasi Streamlit

Masuk ke folder `dashboard/`:

```bash
cd dashboard
```

Lalu jalankan aplikasi Streamlit:

```bash
streamlit run main.py
```

Aplikasi akan terbuka otomatis di browser pada alamat: [http://localhost:8501](http://localhost:8501)

---