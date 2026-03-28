"""
Mahsulotlar uchun signal handlers
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Product
from .barcode_utils import get_next_barcode_for_product


@receiver(pre_save, sender=Product)
def auto_generate_barcode(sender, instance, **kwargs):
    """
    Mahsulot saqlanishidan oldin avtomatik barcode yaratish
    """
    print(f"\n{'='*60}")
    print(f"🔧 SIGNAL: pre_save ishga tushdi")
    print(f"📦 Mahsulot: {instance.name}")
    print(f"🏷️ Mavjud barcode: {instance.barcode}")
    
    # Agar barcode bo'sh bo'lsa, avtomatik yaratish
    if not instance.barcode:
        print(f"⚠️ Barcode yo'q, yangi yaratilmoqda...")
        try:
            new_barcode = get_next_barcode_for_product(instance)
            instance.barcode = new_barcode
            print(f"✅ YANGI BARCODE YARATILDI: {instance.barcode}")
            print(f"📏 Uzunlik: {len(instance.barcode)}")
            print(f"🔢 Turi: {type(instance.barcode)}")
        except Exception as e:
            print(f"❌ XATOLIK barcode yaratishda: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️ Barcode allaqachon mavjud: {instance.barcode}")
    
    print(f"{'='*60}\n")


@receiver(post_save, sender=Product)
def log_product_barcode(sender, instance, created, **kwargs):
    """
    Yangi mahsulot yaratilganda log yozish
    """
    print(f"\n{'='*60}")
    print(f"💾 SIGNAL: post_save ishga tushdi")
    print(f"📦 Mahsulot: {instance.name}")
    print(f"🆕 Yangi yaratildi: {created}")
    
    if created:
        if instance.barcode:
            print(f"✅ Database'ga saqlandi!")
            print(f"🏷️ Barcode: {instance.barcode}")
            print(f"🔍 Tekshirish...")
            
            # Database'dan o'qib ko'rish
            from products.models import Product
            saved_product = Product.objects.get(id=instance.id)
            print(f"📊 Database'dan o'qildi: {saved_product.barcode}")
            print(f"✓ Barcode database'da: {saved_product.barcode == instance.barcode}")
        else:
            print(f"⚠️ MUAMMO: Yangi mahsulot barcode'siz saqlandi!")
    else:
        print(f"ℹ️ Mahsulot yangilandi (barcode: {instance.barcode})")
    
    print(f"{'='*60}\n")
