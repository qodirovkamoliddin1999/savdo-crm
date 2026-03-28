from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import DebtRecord


@receiver(post_save, sender=DebtRecord)
def update_debt_calculations(sender, instance, created, **kwargs):
    """Qarz yozuvi saqlanganda hisob-kitoblarni yangilash"""
    if not created:
        # Faqat mavjud yozuvlar uchun
        instance.calculate_amounts()
        instance.determine_status()
