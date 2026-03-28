# 📋 Production Deploy Checklist

## ✅ Tayyor (Allaqachon Qilingan)

### Django Settings
- ✅ `DEBUG = False` 
- ✅ `ALLOWED_HOSTS` sozlangan
- ✅ `STATIC_ROOT` va `MEDIA_ROOT` sozlangan
- ✅ `WhiteNoise` middleware qo'shilgan
- ✅ Session timeout: 5 daqiqa
- ✅ Time zone: Asia/Tashkent

### Xavfsizlik
- ✅ CSRF protection yoqilgan
- ✅ XSS protection yoqilgan
- ✅ Clickjacking protection yoqilgan

### Barcode Tizimi
- ✅ Avtomatik generatsiya
- ✅ PDF export
- ✅ Scanner qo'llab-quvvatlash
- ✅ Horizontal sticker format

---

## ⚠️ Hostingga Yuklashdan Oldin

### 1. Ortiqcha Fayllarni O'chirish
```bash
python cleanup_for_production.py
```

Bu o'chiradi:
- `__pycache__/` papkalar
- `*.pyc`, `*.pyo` fayllar
- `*.log` fayllar
- `.DS_Store`, `Thumbs.db`

### 2. Hostingga YUKLAMASLIK Kerak

**❌ Bu papkalarni yuklamang:**
```
venv/                    # Virtual environment (185 MB+)
.git/                    # Git repository (agar FTP ishlatayotgan bo'lsangiz)
__pycache__/             # Compiled Python files
.vscode/                 # IDE settings
.idea/                   # IDE settings
node_modules/            # Agar bor bo'lsa
staticfiles/             # Bu serverda yaratiladi
```

**❌ Bu fayllarni yuklamang:**
```
*.pyc
*.pyo
*.log
.env                     # Maxfiy ma'lumotlar (serverda alohida yarating)
db.sqlite3               # Local database (serverda yangi yaratiladi)
.DS_Store
Thumbs.db
```

### 3. Database

**Production DB uchun ikkita variant:**

**A) SQLite (oddiy proyektlar uchun):**
- Hosting serverda yangi `db.sqlite3` yarating
- `python manage.py migrate` ishga tushiring
- `python manage.py createsuperuser` admin yarating

**B) PostgreSQL (tavsiya etiladi katta proyektlar uchun):**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_db',
        'USER': 'crm_user',
        'PASSWORD': 'xavfsiz_parol',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. SECRET_KEY

**❗️ Muhim:** Production'da yangi SECRET_KEY yarating

```python
# Python shell'da:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Bu kalitni `.env` faylga qo'ying va serverga yuklang.

---

## 🚀 Deploy Qadamlari

### Variant 1: Shared Hosting (cPanel)

1. **Fayllarni yuklash:**
   - ZIP qiling (venv/ va .git/ dan tashqari)
   - cPanel File Manager orqali yuklang
   - `/home/username/crm.aptech.uz/` ga extract qiling

2. **Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Database:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Passenger WSGI:**
   - `passenger_wsgi.py` fayl allaqachon mavjud ✅
   - cPanel'da Python App sozlang

### Variant 2: VPS (Ubuntu)

1. **Server tayyorlash:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3-pip python3-venv nginx -y
   ```

2. **Proyektni yuklash:**
   ```bash
   cd /var/www/
   git clone <repo-url> crm.aptech.uz
   # yoki
   scp -r crm/ user@server:/var/www/crm.aptech.uz/
   ```

3. **Dependencies:**
   ```bash
   cd /var/www/crm.aptech.uz/
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Static va Media:**
   ```bash
   python manage.py collectstatic --noinput
   mkdir -p media
   ```

5. **Gunicorn service:**
   ```bash
   sudo cp /path/to/crm-aptech.service /etc/systemd/system/
   sudo systemctl enable crm-aptech.service
   sudo systemctl start crm-aptech.service
   ```

6. **Nginx:**
   ```bash
   sudo cp /path/to/nginx.conf /etc/nginx/sites-available/crm.aptech.uz
   sudo ln -s /etc/nginx/sites-available/crm.aptech.uz /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **SSL:**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d crm.aptech.uz
   ```

---

## 📦 Fayl Hajmlari

```
To'liq proyekt (venv bilan):    ~250 MB
Production (venv siz):            ~15 MB
Database (SQLite):                ~5 MB
Media files:                      O'zgaruvchan
```

**Maslahat:** `venv/` ni hostingga yuklamang, serverda yarating!

---

## 🔍 Deploy Keyin Tekshirish

### 1. Sayt ochilishi
```bash
curl -I https://crm.aptech.uz
```
Javob: `200 OK` ✅

### 2. Static files
- CSS yuklanyaptimi?
- JS ishlayaptimi?
- Rasmlar ko'rinaptimi?

### 3. Admin panel
- `/admin/` ochiladi?
- Login qilish mumkin?

### 4. Barcode
- Yangi mahsulot qo'shganda barcode yaratiladi?
- PDF yuklash ishlaydi?
- Scanner qidiruvi ishlaydi?

### 5. Savdo
- Mahsulot qo'shish?
- Mijoz tanlash?
- Savdo yaratish?

---

## 🛠️ Texnik Tavsiyalar

### Performance
- ✅ WhiteNoise static files uchun
- ⏳ Redis caching (kelajakda)
- ⏳ Database connection pooling

### Backup
```bash
# Har kuni soat 2:00 da
0 2 * * * /path/to/backup.sh
```

### Monitoring
```bash
# Har 5 daqiqada
*/5 * * * * /path/to/monitor.py
```

---

## 📊 Hosting Talablari

### Minimal:
- Python 3.8+
- 512 MB RAM
- 5 GB disk space
- WSGI support (Passenger, Gunicorn)

### Tavsiya etiladi:
- Python 3.10+
- 2 GB RAM
- 20 GB disk space
- PostgreSQL
- Redis
- SSL certificate

---

## ✅ Deploy Tayyor!

**Yuklash kerak:**
- ✓ Python code files (`.py`)
- ✓ Templates (`.html`)
- ✓ Static files (`css/`, `js/`, `img/`)
- ✓ `requirements.txt`
- ✓ `passenger_wsgi.py` (shared hosting)
- ✓ `.env` (maxfiy ma'lumotlar bilan)

**Yuklamaslik kerak:**
- ✗ `venv/` (serverda yaratiladi)
- ✗ `__pycache__/` (avtomatik yaratiladi)
- ✗ `.git/` (agar kerak bo'lmasa)
- ✗ `db.sqlite3` (serverda yaratiladi)
- ✗ `*.pyc`, `*.log`

**Hosting serverda qilish:**
```bash
# 1. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Database
python manage.py migrate
python manage.py createsuperuser

# 4. Static files
python manage.py collectstatic --noinput

# 5. Service start (VPS)
sudo systemctl start crm-aptech.service
```

**🎉 Tayyor! Saytingiz ishlaydi: https://crm.aptech.uz**
