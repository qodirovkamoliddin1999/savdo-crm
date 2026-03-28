#!/bin/bash

# CRM.Aptech.uz - Server Setup Script
# Yangi Ubuntu serverga CRM sistemani o'rnatish

echo "🚀 CRM.Aptech.uz Server Setup"
echo "📍 Domen: savdo.aptech.uz"
echo "⚡ Yangi serverga o'rnatish boshlanmoqda..."

# 1. System update
echo "📦 System update..."
sudo apt update && sudo apt upgrade -y

# 2. Python va kerakli paketlar
echo "🐍 Python va kerakli paketlar..."
sudo apt install python3 python3-pip python3-venv python3-dev -y
sudo apt install build-essential libpq-dev -y

# 3. Nginx
echo "🌐 Nginx install qilish..."
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx

# 4. Firewall
echo "🔥 Firewall sozlash..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# 5. Papkalar yaratish
echo "📁 Papkalar yaratish..."
sudo mkdir -p /var/www/crm.aptech.uz
sudo mkdir -p /var/backups/crm-aptech
sudo mkdir -p /var/log/crm

# 6. User permissions
echo "👤 User permissions..."
sudo chown -R $USER:$USER /var/www/crm.aptech.uz
sudo chmod -R 755 /var/www/crm.aptech.uz

# 7. CRM papkasiga o'tish
cd /var/www/crm.aptech.uz

# 8. Virtual environment yaratish
echo "🐍 Virtual environment yaratish..."
python3 -m venv venv
source venv/bin/activate

# 9. Git (agar kerak bo'lsa)
echo "📥 Git install qilish..."
sudo apt install git -y

# 10. CRM kodlarini yuklash (git orqali)
echo "💻 CRM kodlarini yuklash..."
# git clone <your-repo-url> .
# yoki FTP/SCP orqali yuklang

# 11. Dependencies install qilish
echo "📦 Dependencies install qilish..."
pip install -r requirements_production.txt

# 12. Environment variables
echo "⚙️  Environment variables..."
cp .env.production .env

# 13. Django sozlamalari
echo "🔧 Django sozlamalari..."
export DJANGO_SETTINGS_MODULE=django_pos.settings

# 14. Database migrations
echo "🗄️  Database migrations..."
python manage.py makemigrations
python manage.py migrate

# 15. Static files yig'ish
echo "📁 Static files yig'ish..."
python manage.py collectstatic --noinput

# 16. Superuser yaratish
echo "👤 Superuser yaratish..."
echo "Superuser yaratish uchun ma'lumotlarni kiriting:"
python manage.py createsuperuser

# 17. Systemd service yaratish
echo "🔧 Systemd service yaratish..."
sudo tee /etc/systemd/system/crm-aptech.service > /dev/null <<EOF
[Unit]
Description=CRM Aptech Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/crm.aptech.uz
Environment=DJANGO_SETTINGS_MODULE=django_pos.settings
ExecStart=/var/www/crm.aptech.uz/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 django_pos.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 18. Service enable qilish
echo "🔄 Service enable qilish..."
sudo systemctl daemon-reload
sudo systemctl enable crm-aptech.service
sudo systemctl start crm-aptech.service

# 19. Nginx konfiguratsiyasi
echo "🌐 Nginx konfiguratsiyasi..."
sudo tee /etc/nginx/sites-available/savdo.aptech.uz > /dev/null <<EOF
server {
    listen 80;
    server_name savdo.aptech.uz www.savdo.aptech.uz;
    
    location /static/ {
        alias /var/www/crm.aptech.uz/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/savdo.aptech.uz/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 20. Nginx site enable qilish
echo "🌐 Nginx site enable qilish..."
sudo ln -sf /etc/nginx/sites-available/crm.aptech.uz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 21. SSL/TLS sozlash
echo "🔒 SSL/TLS sozlash..."
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d crm.aptech.uz -d www.crm.aptech.uz --non-interactive --agree-tos --email admin@aptech.uz

# 22. Backup skripti
echo "💾 Backup skripti yaratish..."
sudo tee /usr/local/bin/crm-backup.sh > /dev/null <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/crm-aptech"
DB_FILE="/var/www/crm.aptech.uz/db.sqlite3"

# Backup papkasini yaratish
mkdir -p $BACKUP_DIR

# Database backup
cp $DB_FILE $BACKUP_DIR/db_$DATE.sqlite3

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/crm.aptech.uz/media/

# 7 kundan eski backuplarni o'chirish
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup muvaffaqiyatli yakunlandi: $DATE"
EOF

sudo chmod +x /usr/local/bin/crm-backup.sh

# 23. Cron job qo'shish
echo "⏰ Cron job qo'shish..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/crm-backup.sh") | crontab -

# 24. Monitoring skripti
echo "📊 Monitoring skripti yaratish..."
sudo tee /usr/local/bin/crm-monitor.py > /dev/null <<'EOF'
#!/usr/bin/env python3
import psutil
import time
import subprocess
import os

def check_system_health():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"CPU: {cpu_percent}%")
    print(f"Memory: {memory.percent}%")
    print(f"Disk: {disk.percent}%")
    
    if cpu_percent > 80:
        with open('/var/log/crm-monitor.log', 'a') as f:
            f.write(f"{time.ctime()} - CPU yuqori: {cpu_percent}%\n")
    
    if memory.percent > 80:
        with open('/var/log/crm-monitor.log', 'a') as f:
            f.write(f"{time.ctime()} - Memory yuqori: {memory.percent}%\n")
    
    if disk.percent > 80:
        with open('/var/log/crm-monitor.log', 'a') as f:
            f.write(f"{time.ctime()} - Disk yuqori: {disk.percent}%\n")

if __name__ == "__main__":
    check_system_health()
EOF

sudo chmod +x /usr/local/bin/crm-monitor.py
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/crm-monitor.py") | crontab -

# 25. Final tekshirish
echo "🔍 Final tekshirish..."
sudo systemctl status crm-aptech.service --no-pager
sudo systemctl status nginx --no-pager

# 26. Test qilish
echo "🌐 Test qilish..."
curl -I http://localhost:8000
curl -I http://savdo.aptech.uz
curl -I https://savdo.aptech.uz

echo ""
echo "🎉 Server setup muvaffaqiyatli yakunlandi!"
echo "📍 URL: https://savdo.aptech.uz"
echo "👤 Admin: https://savdo.aptech.uz/admin/"
echo "📊 Monitoring: /var/log/crm-monitor.log"
echo "💾 Backup: /var/backups/crm-aptech/"
echo "🔧 Service: systemctl status crm-aptech.service"
echo ""
echo "⚠️  Eslatma: .env.production fayliga SECRET_KEY ni o'rnating!"
