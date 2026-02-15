# ⚡ Quick Start - 5 Menit Setup

Panduan singkat untuk mulai menggunakan Gofile Mirror Bot dalam 5 menit.

## 🎯 Langkah Cepat

### 1️⃣ Buat Repository GitHub (1 menit)

1. Buka https://github.com/new
2. Repository name: `gofile-mirror`
3. Public/Private: **Pilih sesuai kebutuhan**
4. Klik **"Create repository"**

### 2️⃣ Upload File (2 menit)

1. Klik **"uploading an existing file"**
2. **Drag & drop** semua file dari folder `gofile-github-actions`
3. **Penting**: Pastikan folder `.github` ikut terupload
4. Klik **"Commit changes"**

### 3️⃣ Jalankan Workflow (1 menit)

1. Klik tab **"Actions"**
2. Klik **"Gofile Mirror Bot"** di sidebar
3. Klik **"Run workflow"** (tombol hijau)
4. Isi:
   - URL: `https://speed.hetzner.de/100MB.bin` (untuk test)
   - Server: `auto (Singapore priority)`
5. Klik **"Run workflow"**

### 4️⃣ Dapatkan Link (1 menit)

1. Tunggu workflow selesai (loading akan berubah jadi ✅)
2. Klik pada workflow run yang baru
3. Klik **"📊 Display Results"**
4. Copy link Gofile: `🔗 Link: https://gofile.io/d/...`

## ✅ Done! Siap Digunakan!

---

## 📱 Penggunaan Sehari-hari

### Upload File ke Gofile

```
1. Actions → Run workflow
2. Paste URL file
3. Tunggu → Dapatkan link!
```

### Pilih Server

| Server | Kecepatan Asia |
|--------|----------------|
| `auto (Singapore priority)` | ⭐⭐⭐⭐⭐ |
| `store5` | ⭐⭐⭐⭐ |
| `store1` | ⭐⭐ |

### Contoh URL yang Bisa Digunakan

✅ Direct links: `https://example.com/file.zip`
✅ SourceForge: `https://sourceforge.net/projects/.../files/...`
✅ HTTP servers: `http://speedtest.tele2.net/100MB.zip`

---

## 🆘 Masalah?

| Masalah | Solusi |
|---------|--------|
| Workflow tidak muncul | Pastikan folder `.github/workflows/` terupload |
| Download gagal | Cek URL di browser dulu |
| Upload gagal | Ganti server atau coba lagi |

---

## 📖 Dokumentasi Lengkap

- **SETUP.md** - Panduan setup detail
- **README.md** - Dokumentasi lengkap fitur

---

**🎉 Selamat! Anda sudah bisa mirror file ke Gofile dengan GitHub Actions!**

**💡 Tips:** Bookmark repository Actions page untuk akses cepat!
