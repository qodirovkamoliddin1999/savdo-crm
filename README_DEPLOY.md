# CRM.Aptech.uz - Production Deployment

## 🚀 Bitta Komanda bilan Deploy Qilish

### 📋 Kerakli Fayllar:
1. `deploy_production.py` - To'liq deploy skripti
2. `quick_deploy.sh` - Tezkor deploy skripti  
3. `server_setup.sh` - Yangi server setup skripti
4. `requirements_production.txt` - Production dependencies
5. `.env.production` - Environment variables
6. `DEPLOYMENT.md` - To'liq qo'llanma

---

## 🎯 Tezkor Deploy (1 komanda)

### 1. Yangi Serverga O'rnatish:
```bash
# Serverga SSH orqali ulanish
ssh user@your-server-ip

# Fayllarni serverga yuklash
scp -r /local/path/to/CRM/* user@server:/tmp/

# Setup skriptini ishga tushirish
chmod +x /tmp/server_setup.sh
sudo /tmp/server_setup.sh
```

### 2. Mavjud Serverga Update:
```bash
# Serverga ulanish
ssh user@your-server-ip

# Fayllarni yuklash
scp -r /local/path/to/CRM/* user@server:/var/www/crm.aptech.uz/

# Deploy skriptini ishga tushirish
cd /var/www/crm.aptech.uz
chmod +x deploy_production.py
python deploy_production.py
```

### 3. Tezkor Update (faqat kodlar o'zgarganda):
```bash
# Serverga ulanish
ssh user@your-server-ip

# Quick deploy
cd /var/www/crm.aptech.uz
chmod +x quick_deploy.sh
./quick_deploy.sh
```

---

## 🔧 Avtomatik Skriptlar

### 📦 `deploy_production.py` - To'liq Deploy
- ✅ Virtual environment tekshirish
- ✅ Dependencies install qilish
- ✅ Production sozlamalari
- ✅ Database migrations
- ✅ Static files yig'ish
- ✅ Superuser yaratish
- ✅ Gunicorn install qilish
- ✅ Nginx konfiguratsiyasi
- ✅ Systemd service yaratish
- ✅ SSL/TLS sozlash (Let's Encrypt)
- ✅ Firewall sozlash
- ✅ Backup sozlash
- ✅ Monitoring sozlash
- ✅ Xizmatlarni qayta ishga tushirish

### ⚡ `quick_deploy.sh` - Tezkor Update
- ✅ Dependencies yangilash
- ✅ Database migrations
- ✅ Static files yig'ish
- ✅ Service qayta ishga tushirish
- ✅ Status tekshirish

### 🖥️ `server_setup.sh` - Yangi Server Setup
- ✅ System update
- ✅ Python va kerakli paketlar
- ✅ Nginx install qilish
- ✅ Firewall sozlash
- ✅ Papkalar yaratish
- ✅ Virtual environment
- ✅ CRM o'rnatish
- ✅ SSL/TLS sozlash
- ✅ Backup va monitoring

---

## 🌐 Domen: crm.aptech.uz

### URL lar:
- **Asosiy**: https://crm.aptech.uz
- **Admin panel**: https://crm.aptech.uz/admin/
- **Qarz daftari**: https://crm.aptech.uz/debt/
- **POS**: https://crm.aptech.uz/pos/
- **Mahsulotlar**: https://crm.aptech.uz/products/products_list/

---

## 🔐 Xavfsizlik Sozlamalari

### Production Settings:
```python
DEBUG = False
ALLOWED_HOSTS = ['crm.aptech.uz', 'www.crm.aptech.uz', 'aptech.uz', 'www.aptech.uz']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

### SSL/TLS:
- Let's Encrypt sertifikat
- HTTPS majburiy
- HSTS yoqilgan

### Firewall:
- SSH (22) - ochiq
- HTTP (80) - ochiq  
- HTTPS (443) - ochiq
- Boshqa portlar - yopiq

---

## 📊 Monitoring va Backup

### Monitoring:
- CPU, Memory, Disk usage
- Har 5 daqiqada tekshirish
- Log fayl: `/var/log/crm-monitor.log`

### Backup:
- Har kuni soat 2:00 da
- Database va media files
- 7 kun saqlanadi
- Papka: `/var/backups/crm-aptech/`

---

## 🚨 Troubleshooting

### CSS/Static Files Muammolari:
```bash
# Static files qayta yig'ish
python manage.py collectstatic --clear --noinput

# Nginx qayta yuklash
sudo systemctl reload nginx

# Browser cache tozalash (Ctrl+F5)
```

### Service Muammolari:
```bash
# Service status
sudo systemctl status crm-aptech.service

# Qayta ishga tushirish
sudo systemctl restart crm-aptech.service

# Loglarni ko'rish
sudo journalctl -u crm-aptech.service -f
```

### Database Muammolari:
```bash
# Migrations qayta yuklash
python manage.py migrate --fake-initial

# Database optimallashtirish
python manage.py dbshell
VACUUM;
```

---

## 📱 Mobile va Browser Uslubi

### ✅ Responsive Dizayn:
- Bootstrap 4
- Mobile birinchi yondashuv
- Touch-friendly interfeys
- Fast loading

### ✅ Browser Compatibility:
- Chrome (latest)
- Firefox (latest)  
- Safari (latest)
- Edge (latest)

---

## 🎯 Deploy Qilgandan Keyin

### 1. Test Qilish:
```bash
curl -I https://crm.aptech.uz
curl -I https://crm.aptech.uz/admin/
```

### 2. Admin Panelga Kirish:
- URL: `https://crm.aptech.uz/admin/`
- Username: superuser login
- Password: superuser password

### 3. Modullarni Tekshirish:
- ✅ Qarz daftari ishlashi
- ✅ POS savdo qilishi
- ✅ Mahsulotlar boshqaruvi
- ✅ Xodimlar ruxsatlari
- ✅ Barcode skanerlash

---

## 📞 Yordam

### Agar muammo yuzaga kelsa:
1. 📋 Loglarni tekshiring: `sudo journalctl -u crm-aptech.service -f`
2. 🔄 Service qayta ishga tushiring: `sudo systemctl restart crm-aptech.service`
3. 🌐 Nginx qayta yuklang: `sudo systemctl reload nginx`
4. 📁 Static files qayta yig'ing: `python manage.py collectstatic --noinput`

### Murojaat uchun:
- 📧 Email: admin@aptech.uz
- 📞 Phone: +998 XX XXX-XX-XX

---

## 🎉 Tayyor!

**CRM.Aptech.uz production serverga muvaffaqiyatli deploy qilindi!**

📍 **URL**: https://crm.aptech.uz  
👤 **Admin**: https://crm.aptech.uz/admin/  
📊 **Monitoring**: /var/log/crm-monitor.log  
💾 **Backup**: /var/backups/crm-aptech/  
🔧 **Service**: systemctl status crm-aptech.service

---

### ⚡ Tezkor Komandalar:

```bash
# Deploy qilish
python deploy_production.py

# Tezkor update
./quick_deploy.sh

# Status tekshirish
sudo systemctl status crm-aptech.service

# Loglarni ko'rish
sudo journalctl -u crm-aptech.service -f

# Backup qilish
/usr/local/bin/crm-backup.sh
```

**Barcha CSS, JavaScript, va static files ishlashi uchun barcha sozlamalar avtomatik amalga oshiriladi!** 🎉
