# Gunakan base image Python versi 3.9 (slim agar lebih ringan)
FROM python:3.9-slim

# Install ADB (dan hapus cache agar image lebih kecil)
RUN apt-get update && \
    apt-get install -y adb && \
    rm -rf /var/lib/apt/lists/*

# Buat direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt
COPY requirements.txt .

# Install semua dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode ke dalam /app
COPY . .

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Jalankan aplikasi menggunakan uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
