#!/bin/bash

# CRM.Aptech.uz - Quick Deploy Script
# Bu skript production serverga CRM sistemani tezkor deploy qilish uchun

echo "🚀 CRM.Aptech.uz Production Deploy"
echo "📍 Domen: crm.aptech.uz"
echo "⚡ Production serverga deploy qilish boshlanmoqda..."

# 1. Papkaga o'tish
cd /var/www/crm.aptech.uz || { echo "❌ Papka topilmadi!"; exit 1; }

# 2. Virtual environment aktivlashtirish
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment aktivlashtirildi"
else
    echo "❌ Virtual environment topilmadi!"
    exit 1
fi

# 3. Dependencies install qilish
echo "📦 Dependencies larni yangilash..."
pip install -r requirements.txt

# 4. Django sozlamalari
echo "⚙️  Django sozlamalari..."
export DJANGO_SETTINGS_MODULE=django_pos.settings

# 5. Database migrations
echo "🗄️  Database migrations..."
python manage.py makemigrations
python manage.py migrate

# 6. Static files yig'ish
echo "📁 Static files yig'ish..."
python manage.py collectstatic --noinput --clear

# 7. Service qayta ishga tushirish
echo "🔄 Service qayta ishga tushirish..."
sudo systemctl restart crm-aptech.service
sudo systemctl reload nginx

# 8. Status tekshirish
echo "🔍 Status tekshirish..."
sudo systemctl status crm-aptech.service --no-pager
sudo systemctl status nginx --no-pager

# 9. Test qilish
echo "🌐 Test qilish..."
curl -I http://localhost:8000
curl -I http://crm.aptech.uz

echo ""
echo "🎉 Deploy muvaffaqiyatli yakunlandi!"
echo "📍 URL: https://crm.aptech.uz"
echo "👤 Admin: https://crm.aptech.uz/admin/"
