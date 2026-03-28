#!/usr/bin/env python
"""
CRM.Aptech.uz - Production Deployment Script
Bu skript production serverga CRM sistemani deploy qilish uchun yaratilgan.
Domen: crm.aptech.uz
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

# Django sozlamalari
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_pos.settings')

def run_command(command, description):
    """Komandalarni bajarish va natijalarni chiqarish"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Muvaffaqiyatli!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - Xatolik!")
            if result.stderr:
                print(f"Xatolik: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Istisno: {e}")
        return False
    
    return True

def main():
    """Asosiy deployment funksiyasi"""
    print("🚀 CRM.Aptech.uz Production Deployment")
    print("📍 Domen: crm.aptech.uz")
    print("⚡ Production serverga deploy qilish boshlanmoqda...")
    
    # 1. Django sozlamalarini tekshirish
    print("\n🔍 Django sozlamalari tekshirilmoqda...")
    try:
        django.setup()
        from django.conf import settings
        print(f"✅ Django versiya: {django.get_version()}")
        print(f"✅ DEBUG mode: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    except Exception as e:
        print(f"❌ Django sozlamalari xatosi: {e}")
        return
    
    # 2. Virtual environment tekshirish
    print("\n🐍 Virtual environment tekshirilmoqda...")
    venv_path = os.path.join(os.getcwd(), 'venv')
    if os.path.exists(venv_path):
        print("✅ Virtual environment mavjud")
    else:
        print("⚠️  Virtual environment topilmadi. Yangi yaratilmoqda...")
        run_command("python -m venv venv", "Virtual environment yaratish")
    
    # 3. Dependencies install qilish
    print("\n📦 Dependencies larni install qilish...")
    requirements_path = os.path.join(os.getcwd(), 'requirements.txt')
    if os.path.exists(requirements_path):
        run_command(f"pip install -r {requirements_path}", "Dependencies install qilish")
    else:
        print("⚠️  requirements.txt topilmadi")
    
    # 4. Production sozlamalari
    print("\n⚙️  Production sozlamalari...")
    
    # Settings.py faylini production uchun sozlash
    settings_file = 'django_pos/settings.py'
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # DEBUG ni False ga o'zgartirish
        if 'DEBUG = True' in content:
            content = content.replace('DEBUG = True', 'DEBUG = False')
            with open(settings_file, 'w') as f:
                f.write(content)
            print("✅ DEBUG mode False ga o'zgartirildi")
        
        # ALLOWED_HOSTS ga domen qo'shish
        if 'crm.aptech.uz' not in content:
            content = content.replace(
                "ALLOWED_HOSTS = ['aptech.uz', 'www.aptech.uz', 'localhost', '127.0.0.1']",
                "ALLOWED_HOSTS = ['crm.aptech.uz', 'www.crm.aptech.uz', 'aptech.uz', 'www.aptech.uz', 'localhost', '127.0.0.1']"
            )
            with open(settings_file, 'w') as f:
                f.write(content)
            print("✅ ALLOWED_HOSTS ga crm.aptech.uz qo'shildi")
    
    # 5. Database migrations
    print("\n🗄️  Database migrations...")
    run_command("python manage.py makemigrations", "Migrations yaratish")
    run_command("python manage.py migrate", "Migrations qo'llash")
    
    # 6. Static files yig'ish
    print("\n📁 Static files yig'ish...")
    run_command("python manage.py collectstatic --noinput", "Static files yig'ish")
    
    # 7. Superuser yaratish (agar yo'q bo'lsa)
    print("\n👤 Superuser tekshirish...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("⚠️  Superuser topilmadi. Yangi yaratish kerak:")
            run_command("python manage.py createsuperuser", "Superuser yaratish")
        else:
            print("✅ Superuser mavjud")
    except Exception as e:
        print(f"❌ Superuser tekshirishda xatolik: {e}")
    
    # 8. Gunicorn install qilish
    print("\n🦊 Gunicorn install qilish...")
    run_command("pip install gunicorn", "Gunicorn install qilish")
    
    # 9. Nginx konfiguratsiyasi yaratish
    print("\n🌐 Nginx konfiguratsiyasi...")
    nginx_config = f"""
server {{
    listen 80;
    server_name crm.aptech.uz www.crm.aptech.uz;
    
    location /static/ {{
        alias {os.getcwd()}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
    
    location /media/ {{
        alias {os.getcwd()}/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
    
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    
    nginx_file = '/etc/nginx/sites-available/crm.aptech.uz'
    try:
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)
        print(f"✅ Nginx konfiguratsiyasi yaratildi: {nginx_file}")
        run_command("ln -sf /etc/nginx/sites-available/crm.aptech.uz /etc/nginx/sites-enabled/", "Nginx site enable qilish")
        run_command("nginx -t", "Nginx konfiguratsiyasi tekshirish")
        run_command("systemctl reload nginx", "Nginx qayta yuklash")
    except Exception as e:
        print(f"⚠️  Nginx konfiguratsiyasi xatosi: {e}")
    
    # 10. Systemd service yaratish
    print("\n🔧 Systemd service yaratish...")
    service_config = f"""
[Unit]
Description=CRM Aptech Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory={os.getcwd()}
Environment=DJANGO_SETTINGS_MODULE=django_pos.settings
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 django_pos.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    service_file = '/etc/systemd/system/crm-aptech.service'
    try:
        with open(service_file, 'w') as f:
            f.write(service_config)
        print(f"✅ Systemd service yaratildi: {service_file}")
        run_command("systemctl daemon-reload", "Systemd daemon reload")
        run_command("systemctl enable crm-aptech.service", "Service enable qilish")
        run_command("systemctl start crm-aptech.service", "Service ishga tushirish")
        run_command("systemctl status crm-aptech.service", "Service holatini tekshirish")
    except Exception as e:
        print(f"⚠️  Systemd service xatosi: {e}")
    
    # 11. SSL/TLS sozlamalari (Let's Encrypt)
    print("\n🔒 SSL/TLS sozlamalari...")
    run_command("apt update && apt install -y certbot python3-certbot-nginx", "Certbot install qilish")
    run_command("certbot --nginx -d crm.aptech.uz -d www.crm.aptech.uz --non-interactive --agree-tos --email admin@aptech.uz", "SSL sertifikat olish")
    
    # 12. Firewall sozlamalari
    print("\n🔥 Firewall sozlamalari...")
    run_command("ufw allow 22", "SSH portini ochish")
    run_command("ufw allow 80", "HTTP portini ochish")
    run_command("ufw allow 443", "HTTPS portini ochish")
    run_command("ufw --force enable", "Firewall enable qilish")
    
    # 13. Backup sozlamalari
    print("\n💾 Backup sozlamalari...")
    backup_script = f"""
#!/bin/bash
# CRM Aptech Backup Script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/crm-aptech"
DB_FILE="{os.getcwd()}/db.sqlite3"

# Backup papkasini yaratish
mkdir -p $BACKUP_DIR

# Database backup
cp $DB_FILE $BACKUP_DIR/db_$DATE.sqlite3

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz {os.getcwd()}/media/

# 7 kundan eski backuplarni o'chirish
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup muvaffaqiyatli yakunlandi: $DATE"
"""
    
    backup_file = '/usr/local/bin/crm-backup.sh'
    try:
        with open(backup_file, 'w') as f:
            f.write(backup_script)
        os.chmod(backup_file, 0o755)
        print(f"✅ Backup skripti yaratildi: {backup_file}")
        
        # Cron job qo'shish (har kuni soat 2:00 da backup)
        run_command("crontab -l | {{ cat; echo '0 2 * * * /usr/local/bin/crm-backup.sh'; }} | crontab -", "Cron job qo'shish")
    except Exception as e:
        print(f"⚠️  Backup sozlamalari xatosi: {e}")
    
    # 14. Monitoring sozlamalari
    print("\n📊 Monitoring sozlamalari...")
    run_command("pip install psutil", "psutil install qilish")
    
    monitoring_script = f"""
#!/usr/bin/env python3
import psutil
import time
import subprocess
import os

def check_system_health():
    """System health monitoring"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"CPU: {{cpu_percent}}%")
    print(f"Memory: {{memory.percent}}%")
    print(f"Disk: {{disk.percent}}%")
    
    # Agar resurslar yuqori bo'lsa, log yozish
    if cpu_percent > 80:
        with open('/var/log/crm-monitor.log', 'a') as f:
            f.write(f"{{time.ctime()}} - CPU yuqori: {{cpu_percent}}%\\n")
    
    if memory.percent > 80:
        with open('/var/log/crm-monitor.log', 'a') as f:
            f.write(f"{{time.ctime()}} - Memory yuqori: {{memory.percent}}%\\n")
    
    if disk.percent > 80:
        with open('/var/log/crm-monitor.log', 'a') as f:
            f.write(f"{{time.ctime()}} - Disk yuqori: {{disk.percent}}%\\n")

if __name__ == "__main__":
    check_system_health()
"""
    
    monitor_file = '/usr/local/bin/crm-monitor.py'
    try:
        with open(monitor_file, 'w') as f:
            f.write(monitor_script)
        os.chmod(monitor_file, 0o755)
        print(f"✅ Monitoring skripti yaratildi: {monitor_file}")
        
        # Har 5 daqiqada monitoring
        run_command("crontab -l | {{ cat; echo '*/5 * * * * /usr/local/bin/crm-monitor.py'; }} | crontab -", "Monitoring cron job qo'shish")
    except Exception as e:
        print(f"⚠️  Monitoring sozlamalari xatosi: {e}")
    
    # 15. Xizmatlarni qayta ishga tushirish
    print("\n🔄 Xizmatlarni qayta ishga tushirish...")
    run_command("systemctl restart crm-aptech.service", "CRM service qayta ishga tushirish")
    run_command("systemctl restart nginx", "Nginx qayta ishga tushirish")
    
    # 16. Final tekshirish
    print("\n🔍 Final tekshirish...")
    run_command("curl -I http://crm.aptech.uz", "HTTP tekshirish")
    run_command("curl -I https://crm.aptech.uz", "HTTPS tekshirish")
    
    print("\n" + "="*60)
    print("🎉 CRM.Aptech.uz muvaffaqiyatli deploy qilindi!")
    print("📍 URL: https://crm.aptech.uz")
    print("👤 Admin panel: https://crm.aptech.uz/admin/")
    print("📊 Monitoring: /var/log/crm-monitor.log")
    print("💾 Backup: /var/backups/crm-aptech/")
    print("🔧 Service: systemctl status crm-aptech.service")
    print("="*60)

if __name__ == "__main__":
    main()
