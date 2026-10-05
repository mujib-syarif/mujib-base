# mujib-base

Website katalog **Mujib, S.Coc. — ART BASE CREATOR** (Custom Base Nama Clash of Clans).
Static site (HTML + CSS + vanilla JS) di-deploy ke Cloudflare Workers static assets.

## Struktur

| Path | Isi |
| --- | --- |
| `originals/` | Master/original gambar. **Tidak pernah diubah** oleh workflow. |
| `originals/free/` | Master gambar Free Base. |
| `originals/testimoni/` | (opsional) Master screenshot testimoni. |
| `site/` | Folder yang di-deploy (`wrangler.toml` → `[assets] directory = "./site"`). |
| `site/gallery/` | **Generated.** Thumbnail WebP (maks 1100px, q86) + `large/` (maks 2400px, q90) + `manifest.json`. |
| `site/free/`, `site/testimoni/` | Generated dengan pola yang sama. |
| `tools/optimize_images.py` | Pembuat WebP + manifest. |
| `tools/catalog-names.json` | Alias: nama file master → nama tampilan katalog. |
| `tools/validate_site.py` | Cek path gambar, teks wajib, referensi lama. |
| `.github/workflows/optimize-images.yml` | Menjalankan optimizer saat `originals/` berubah. |

## Menambah base baru

1. Upload gambar ke `originals/` dengan nama `Nama TH 17.jpg` (bagian `TH <angka>` dipakai untuk filter & harga).
   - Nama file lain (mis. `Screenshot_...jpg`) **tidak** tampil di katalog kecuali ditambahkan ke `tools/catalog-names.json`, contoh: `"Screenshot_20260901-120000.jpg": "Nama TH 17"`.
2. Push ke `main`. GitHub Actions membuat `site/gallery/*.webp` + `manifest.json` dan commit otomatis, lalu Cloudflare men-deploy.
3. Urutan "Base Terbaru" mengikuti tanggal pertama file muncul (`added` di manifest).

Free Base: taruh master di `originals/free/` (link CoC tetap di `FREE_BASES` dalam `site/index.html`).
Testimoni: taruh di `originals/testimoni/` (otomatis dikompres) atau langsung di `site/testimoni/` (sudah terkompres).

## Jalankan lokal

```bash
pip install -r tools/requirements.txt
python tools/optimize_images.py      # buat WebP + manifest
python tools/validate_site.py        # validasi
npx wrangler dev                     # preview di http://localhost:8787
```

## Deploy

```bash
npx wrangler deploy
```

Atau biarkan Cloudflare Workers Builds yang deploy setiap push ke `main`.
