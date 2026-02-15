# 🤖 Gofile Mirror Bot - GitHub Actions

GitHub Actions workflow untuk download file dari URL dan upload ke Gofile dengan pilihan server.

## ✨ Fitur

- ✅ Download file dari URL (termasuk SourceForge)
- ✅ Upload otomatis ke Gofile
- ✅ Pilih server Gofile sendiri atau auto (prioritas Singapore)
- ✅ Progress tracking untuk download & upload
- ✅ Auto-cleanup: File dihapus setelah upload
- ✅ Display hasil upload di GitHub Actions log

## 📋 Cara Setup

### 1. Fork atau Clone Repository

```bash
git clone https://github.com/username/repo-name.git
cd repo-name
```

### 2. Upload File ke GitHub

Pastikan struktur folder seperti ini:

```
your-repo/
├── .github/
│   └── workflows/
│       └── gofile-mirror.yml
├── gofile_bot.py
└── README.md
```

### 3. Push ke GitHub

```bash
git add .
git commit -m "Add Gofile Mirror Bot"
git push origin main
```

## 🚀 Cara Menggunakan

### Method 1: Via GitHub Web Interface

1. Buka repository Anda di GitHub
2. Klik tab **Actions**
3. Pilih workflow **Gofile Mirror Bot** di sidebar kiri
4. Klik tombol **Run workflow** (pojok kanan atas)
5. Isi form:
   - **download_url**: Masukkan URL file yang akan di-download
   - **gofile_server**: Pilih server atau biarkan "auto"
6. Klik **Run workflow**

### Method 2: Via GitHub CLI

```bash
gh workflow run gofile-mirror.yml \
  -f download_url="https://example.com/file.zip" \
  -f gofile_server="auto (Singapore priority)"
```

## 🌐 Pilihan Server

| Server | Zone | Kecepatan untuk Asia |
|--------|------|----------------------|
| **auto (Singapore priority)** | Auto-detect | ⭐⭐⭐⭐⭐ Recommended |
| store1 | Europe | ⭐⭐ |
| store2 | North America | ⭐ |
| store3 | Europe | ⭐⭐ |
| store4 | North America | ⭐ |
| store5 | Asia (kadang) | ⭐⭐⭐⭐ |
| store6 | Europe | ⭐⭐ |
| store7 | Asia (jarang) | ⭐⭐⭐⭐⭐ |

**💡 Tips:**
- Gunakan **"auto (Singapore priority)"** untuk hasil terbaik di Asia
- Bot akan otomatis mencari server Singapore/Asia yang tersedia
- Jika tidak ada server Asia, akan fallback ke server tercepat

## 📊 Contoh Output

```
🤖 Gofile Mirror Bot - GitHub Actions
============================================================

🎯 Processing URL: https://example.com/file.zip
📝 Filename: file.zip

🚀 Starting download: file.zip
📦 File size: 125.5 MB
Downloading: 100%|██████████| 125.5M/125.5M [00:45<00:00, 2.78MB/s]
✅ Download completed: file.zip

📡 Found 6 available servers
   - store1 (Zone: eu)
   - store5 (Zone: asia)
   - store6 (Zone: eu)
🇸🇬 Selected Singapore/Asia server: store5

☁️ Preparing upload to Gofile
📁 File: file.zip
🌐 Server: store5
Uploading: 100%|██████████| 125.5M/125.5M [01:23<00:00, 1.51MB/s]

🎉 Upload SUCCESS!
🔗 Download Link: https://gofile.io/d/ABC123
📄 File ID: abc123-xyz

🗑️ Local file deleted: file.zip

=== UPLOAD RESULT ===
✅ Upload Successful!
📁 File: file.zip
📦 Size: 125.5 MB
🌐 Server: store5
🔗 Link: https://gofile.io/d/ABC123
📄 File ID: abc123-xyz
```

## 🔧 Troubleshooting

### Error: "Download failed"
- ✅ Periksa URL apakah valid
- ✅ Coba akses URL di browser untuk memastikan file bisa didownload
- ✅ Beberapa website memerlukan cookies/authentication

### Error: "Upload failed"
- ✅ Coba ganti server (jangan gunakan auto)
- ✅ Cek https://api.gofile.io/servers untuk server yang aktif
- ✅ File terlalu besar (>5GB kadang bermasalah)

### Workflow tidak muncul di Actions
- ✅ Pastikan file `.github/workflows/gofile-mirror.yml` ada
- ✅ Pastikan sudah push ke branch `main` atau `master`
- ✅ Periksa syntax YAML (gunakan YAML validator)

## 📝 Catatan

- ⚠️ File akan **otomatis dihapus** setelah upload berhasil
- ⚠️ Gofile link biasanya permanen, tapi bisa dihapus jika tidak ada aktivitas
- ⚠️ GitHub Actions runner memiliki limit storage ~14GB
- ⚠️ Waktu maksimal workflow: 6 jam (untuk file besar)

## 🔒 Privacy & Security

- ✅ Tidak ada data yang disimpan di repository
- ✅ File dihapus otomatis setelah upload
- ✅ Menggunakan GitHub Actions runner (disposable environment)
- ✅ Tidak ada API key atau token yang diperlukan

## 📜 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

**Made with ❤️ for easy file mirroring**
