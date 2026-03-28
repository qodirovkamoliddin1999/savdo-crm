# CRM.Aptech.uz - Production Deployment Guide

## 🚀 Tezkor Deploy Qilish

### 1. Production Serverga Fayllarni Yuklash
```bash
# Serverga SSH orqali ulanish
ssh user@your-server-ip

# CRM papkasini yaratish
mkdir -p /var/www/crm.aptech.uz
cd /var/www/crm.aptech.uz

# Git orqali kodlarni yuklash (yoki FTP/SCP)
git clone <your-repo-url> .
# yoki
# scp -r /local/path/to/CRM user@server:/var/www/crm.aptech.uz/
```

### 2. Deploy Skriptini Ishga Tushirish
```bash
# Skriptni ishga tushirish
python deploy_production.py

# Yoki qo'lda bajarish:
chmod +x deploy_production.py
./deploy_production.py
```

## 📋 Production Sozlamalari

### Django Settings (django_pos/settings.py)
```python
# Production uchun sozlangan qiymatlar
DEBUG = False
ALLOWED_HOSTS = ['crm.aptech.uz', 'www.crm.aptech.uz', 'aptech.uz', 'www.aptech.uz']

# Static files
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = os.path.join(CORE_DIR, 'media')
MEDIA_URL = '/media/'

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Nginx Konfiguratsiyasi
```nginx
server {
    listen 80;
    server_name crm.aptech.uz www.crm.aptech.uz;
    
    location /static/ {
        alias /var/www/crm.aptech.uz/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/crm.aptech.uz/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service
```ini
[Unit]
Description=CRM Aptech Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/crm.aptech.uz
Environment=DJANGO_SETTINGS_MODULE=django_pos.settings
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 django_pos.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔧 Server Sozlamalari

### 1. System Update
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Python va Dependencies
```bash
sudo apt install python3 python3-pip python3-venv -y
pip install -r requirements.txt
```

### 3. Database
```bash
# SQLite (o'rniga PostgreSQL ham ishlatish mumkin)
python manage.py migrate
```

### 4. Static Files
```bash
python manage.py collectstatic --noinput
```

### 5. Superuser
```bash
python manage.py createsuperuser
```

## 🌐 SSL/TLS Sozlash

### Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d crm.aptech.uz -d www.crm.aptech.uz
```

## 🔥 Firewall Sozlash

### UFW
```bash
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS
sudo ufw --force enable
```

## 💾 Backup Sozlash

### Cron Job
```bash
# Har kuni soat 2:00 da backup
0 2 * * * /usr/local/bin/crm-backup.sh
```

## 📊 Monitoring

### System Monitoring
```bash
# Har 5 daqiqada monitoring
*/5 * * * * /usr/local/bin/crm-monitor.py
```

## 🔍 Xizmatlarni Boshqarish

### Service Commands
```bash
# CRM service
sudo systemctl status crm-aptech.service
sudo systemctl start crm-aptech.service
sudo systemctl stop crm-aptech.service
sudo systemctl restart crm-aptech.service

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
```

### Log Files
```bash
# CRM loglari
sudo journalctl -u crm-aptech.service -f

# Nginx loglari
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Monitoring loglari
sudo tail -f /var/log/crm-monitor.log
```

## 🚨 Troubleshooting

### Umumiy Muammolar
1. **Static files ishlamayapti**: `python manage.py collectstatic --noinput`
2. **Database xatolik**: `python manage.py migrate`
3. **Permission xatolik**: `sudo chown -R www-data:www-data /var/www/crm.aptech.uz`
4. **Service ishlamayapti**: `sudo systemctl restart crm-aptech.service`

### CSS/Static Files Muammolari
```bash
# Static files qayta yig'ish
python manage.py collectstatic --clear --noinput

# Nginx qayta yuklash
sudo systemctl reload nginx

# Browser cache tozalash (Ctrl+F5)
```

### Database Muammolari
```bash
# Migrations qayta yuklash
python manage.py migrate --fake-initial

# Database optimallashtirish
python manage.py dbshell
VACUUM;
```

## 📱 Mobile va Browser Uslubi

### Responsive Dizayn
- Bootstrap 4 dan foydalanilgan
- Mobile birinchi yondashuv
- Touch-friendly interfeys

### Browser Compatibility
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🔐 Security

### Xavfsizlik Sozlamalari
- CSRF protection yoqilgan
- XSS protection yoqilgan
- HTTPS majburiy
- Admin panel himoyalangan

### Password Policy
- Minimum 8 ta belgi
- Har xil turdagi belgilar
- Password hash qilingan

## 📈 Performance

### Optimallashtirish
- Static files caching
- Database indekslar
- Gunicorn workers
- Nginx caching

### Monitoring Metrikalar
- CPU usage
- Memory usage
- Disk space
- Response time

## 🎯 Deploy Qilgandan Keyin

### 1. Test Qilish
```bash
curl -I https://crm.aptech.uz
curl -I https://crm.aptech.uz/admin/
```

### 2. Admin Panelga Kirish
- URL: `https://crm.aptech.uz/admin/`
- Username: superuser login
- Password: superuser password

### 3. Modullarni Tekshirish
- Qarz daftari: `/debt/`
- POS: `/pos/`
- Mahsulotlar: `/products/products_list/`
- Xodimlar: `/organizations/employees_list/`

## 📞 Yordam

### Agar muammo yuzaga kelsa:
1. Loglarni tekshiring: `sudo journalctl -u crm-aptech.service -f`
2. Service qayta ishga tushiring: `sudo systemctl restart crm-aptech.service`
3. Nginx qayta yuklang: `sudo systemctl reload nginx`
4. Static files qayta yig'ing: `python manage.py collectstatic --noinput`

### Murojaat uchun:
- Email: admin@aptech.uz
- Phone: +998 XX XXX-XX-XX

---

## 🎉 Tayyor!

CRM.Aptech.uz production serverga muvaffaqiyatli deploy qilindi!

📍 **URL**: https://crm.aptech.uz  
👤 **Admin**: https://crm.aptech.uz/admin/  
📊 **Monitoring**: /var/log/crm-monitor.log  
💾 **Backup**: /var/backups/crm-aptech/
