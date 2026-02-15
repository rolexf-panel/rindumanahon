# 🚀 Setup Guide - Gofile Mirror Bot GitHub Actions

Panduan lengkap untuk setup workflow Gofile Mirror Bot di GitHub.

## 📦 Struktur File

Setelah extract, struktur folder harus seperti ini:

```
gofile-github-actions/
├── .github/
│   └── workflows/
│       └── gofile-mirror.yml    # Workflow definition
├── .gitignore                    # Git ignore rules
├── gofile_bot.py                 # Main Python script
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation
└── SETUP.md                      # This file
```

## 🔧 Langkah-langkah Setup

### Step 1: Buat Repository Baru di GitHub

1. Login ke GitHub: https://github.com
2. Klik tombol **"+"** di pojok kanan atas
3. Pilih **"New repository"**
4. Isi form:
   - **Repository name**: `gofile-mirror-bot` (atau nama lain)
   - **Description**: `Automated file mirror to Gofile using GitHub Actions`
   - **Public** atau **Private** (pilih sesuai kebutuhan)
   - ✅ Check **"Add a README file"** (opsional)
5. Klik **"Create repository"**

### Step 2: Upload File ke Repository

#### Method A: Via Web Interface (Paling Mudah)

1. Di halaman repository, klik **"Add file"** → **"Upload files"**
2. Drag & drop semua file/folder dari `gofile-github-actions/` ke area upload
3. Pastikan struktur folder tetap terjaga (`.github/workflows/` harus ada)
4. Scroll ke bawah, isi commit message: `Initial commit - Add Gofile Mirror Bot`
5. Klik **"Commit changes"**

#### Method B: Via Git Command Line

```bash
# Clone repository yang baru dibuat
git clone https://github.com/username/gofile-mirror-bot.git
cd gofile-mirror-bot

# Copy semua file dari gofile-github-actions ke repo
cp -r /path/to/gofile-github-actions/* .

# Atau jika di Windows
# xcopy /E /I C:\path\to\gofile-github-actions\* .

# Add, commit, push
git add .
git commit -m "Initial commit - Add Gofile Mirror Bot"
git push origin main
```

### Step 3: Verifikasi Setup

1. Buka repository di GitHub
2. Klik tab **"Actions"**
3. Anda harus melihat workflow **"Gofile Mirror Bot"** di sidebar kiri

**✅ Jika muncul**: Setup berhasil!
**❌ Jika tidak muncul**: Periksa apakah file `.github/workflows/gofile-mirror.yml` ada

### Step 4: Test Run Pertama

1. Di tab **Actions**, klik workflow **"Gofile Mirror Bot"**
2. Klik tombol **"Run workflow"** (pojok kanan atas, warna hijau)
3. Isi form test:
   ```
   download_url: https://speed.hetzner.de/100MB.bin
   gofile_server: auto (Singapore priority)
   ```
4. Klik **"Run workflow"**
5. Tunggu beberapa detik, refresh halaman
6. Klik pada workflow run yang baru muncul
7. Lihat progress download & upload secara real-time

### Step 5: Lihat Hasil

Setelah workflow selesai:
1. Expand section **"📥 Download and Upload to Gofile"**
2. Lihat log lengkap proses download & upload
3. Expand section **"📊 Display Results"**
4. Dapatkan link download Gofile: `🔗 Link: https://gofile.io/d/...`

## 🎯 Cara Menggunakan

### Quick Start

1. **Buka GitHub Repository** → Tab **Actions**
2. **Klik** workflow "Gofile Mirror Bot"
3. **Klik** "Run workflow"
4. **Masukkan URL** file yang ingin di-mirror
5. **Pilih server** (atau biarkan auto)
6. **Klik** "Run workflow"
7. **Tunggu** dan dapatkan link Gofile!

### Contoh URL yang Didukung

```
✅ Direct download links
https://example.com/file.zip

✅ SourceForge
https://sourceforge.net/projects/project-name/files/file.zip

✅ File hosting
https://transfer.sh/xxxxx/file.zip

✅ HTTP/HTTPS servers
http://speedtest.tele2.net/100MB.zip
```

### Contoh Pilihan Server

| Input | Hasil |
|-------|-------|
| `auto (Singapore priority)` | Bot cari server Asia/SG otomatis |
| `store1` | Paksa gunakan store1 (Europe) |
| `store5` | Paksa gunakan store5 (biasanya Asia) |

## ⚡ Tips & Tricks

### 1. **Gunakan Private Repository** (Opsional)
   - Jika ingin workflow tidak terlihat publik
   - Settings → Change visibility → Make private

### 2. **Notifikasi Email**
   - GitHub akan email Anda jika workflow gagal
   - Settings → Notifications → Actions

### 3. **Workflow History**
   - Semua run history tersimpan di tab Actions
   - Bisa re-run workflow yang gagal

### 4. **Multiple Files**
   - Untuk mirror multiple files, jalankan workflow berkali-kali
   - Atau edit script untuk support multiple URLs

### 5. **Check Server Status**
   - Buka: https://api.gofile.io/servers
   - Lihat server mana yang online

## 🔍 Troubleshooting

### Problem: "Workflow not found"

**Solusi:**
```bash
# Periksa struktur folder
ls -la .github/workflows/

# Harus ada: gofile-mirror.yml
# Jika tidak ada, re-upload file
```

### Problem: "Python module not found"

**Solusi:**
- Workflow sudah include `pip install requests tqdm`
- Tidak perlu install manual

### Problem: "Download timeout"

**Solusi:**
1. Coba lagi (kadang server source bermasalah)
2. Cek URL di browser dulu
3. GitHub Actions timeout: 6 jam (cukup untuk file <50GB)

### Problem: "Upload failed to Gofile"

**Solusi:**
1. Coba server lain (jangan auto)
2. Tunggu beberapa menit, Gofile kadang maintenance
3. Check https://gofile.io untuk status

### Problem: "Permission denied"

**Solusi:**
- Tab Actions → Settings
- Scroll ke "Workflow permissions"
- Pilih "Read and write permissions"
- Save

## 📊 Limits & Restrictions

| Item | Limit |
|------|-------|
| Workflow runtime | 6 hours max |
| Storage | ~14GB available |
| File size | Unlimited (asal < storage) |
| Concurrent runs | 20 workflows |
| Monthly minutes | 2,000 min (Free), Unlimited (Pro) |

## 🆘 Support

### GitHub Actions Documentation
https://docs.github.com/en/actions

### Gofile API Documentation
https://gofile.io/api

### Issues
Jika ada masalah, buat issue di repository ini.

## 🎓 Advanced Usage

### Custom Modifications

Edit `gofile_bot.py` untuk:
- Support more file hosts
- Add password protection
- Custom filename
- Upload to folder

### Schedule Automatic Runs

Edit `.github/workflows/gofile-mirror.yml`, tambahkan:
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Run daily at midnight
  workflow_dispatch:
    # ... existing inputs
```

### Notifications to Telegram/Discord

Tambahkan step di workflow untuk send notification setelah upload.

---

**🎉 Selamat! Setup selesai!**

Sekarang Anda bisa mirror file ke Gofile dengan mudah menggunakan GitHub Actions.
