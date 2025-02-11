# **Aplikasi FastAPI untuk Ekstraksi Data Perangkat Android**

Aplikasi ini menggunakan FastAPI untuk menyediakan antarmuka API yang memungkinkan pengguna mengekstrak data dari perangkat Android yang terhubung melalui ADB (Android Debug Bridge). Data yang diekstraksi termasuk informasi perangkat, riwayat browser, SMS, kontak, dan log panggilan.

## **Prasyarat**

1. **Python 3.8 atau lebih tinggi**: Pastikan Python sudah terinstal di sistem Anda.
2. **ADB (Android Debug Bridge)**: Pastikan ADB sudah terinstal dan dapat diakses di sistem Anda.
3. **Perangkat Android Terhubung**: Pastikan perangkat Android sudah terhubung ke komputer dengan mode debugging USB diaktifkan.
4. **SQLite**: Aplikasi ini menggunakan SQLite untuk menyimpan data ekstraksi.

## **Langkah Instalasi**


### 1. Buat Lingkungan Virtual (`venv`)
Untuk mengisolasi dependensi, buat lingkungan virtual Python:
```bash
python -m venv venv
```

### 2. Aktifkan Lingkungan Virtual
Aktifkan lingkungan virtual sesuai dengan sistem operasi Anda:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Instal Dependensi
Instal semua dependensi yang diperlukan menggunakan `pip`:
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi ADB
Pastikan jalur ADB sudah benar dalam kode. Jika tidak, ubah variabel `ADB_PATH` di file Python sesuai dengan lokasi ADB di sistem Anda:
```python
ADB_PATH = r"C:\\Path\\To\\adb.exe"
```

### 5. Jalankan Aplikasi
Gunakan `uvicorn` untuk menjalankan aplikasi FastAPI:
```bash
uvicorn main:app --reload
```

Aplikasi akan berjalan di `http://127.0.0.1:8000`.

---

## **Endpoints API**

Berikut adalah beberapa endpoint utama yang tersedia:

1. **`GET /`**: Halaman dashboard (HTML).
2. **`GET /pull-all`**: Ekstrak semua data (informasi perangkat, kontak, SMS, log panggilan, dll.) dan simpan ke database SQLite.
3. **`GET /browser-history`**: Dapatkan riwayat browser dari database.
4. **`GET /contacts`**: Dapatkan daftar kontak dari database.
5. **`GET /sms`**: Dapatkan daftar SMS dari database.
6. **`GET /device-info`**: Dapatkan informasi perangkat dari database.
7. **`GET /call-logs`**: Dapatkan log panggilan dari database.
8. **`GET /most-contacted`**: Dapatkan daftar pengirim SMS/penerima panggilan terbanyak.
