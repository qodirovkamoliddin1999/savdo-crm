#!/usr/bin/env python
"""
Production uchun kerak bo'lmagan fayllarni o'chirish
"""
import os
import shutil
from pathlib import Path

def cleanup_production():
    """O'chirilishi kerak bo'lgan fayllar va papkalar"""
    
    base_dir = Path(__file__).resolve().parent
    
    # O'chirilishi kerak papkalar
    folders_to_remove = [
        '__pycache__',
        '.pytest_cache',
        '.mypy_cache',
        'htmlcov',
        '.coverage',
    ]
    
    # O'chirilishi kerak fayl turlari
    file_patterns = [
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db',
        '*.swp',
        '*.swo',
        '*~',
        '*.log',
    ]
    
    removed_count = 0
    freed_space = 0
    
    print("🧹 Production uchun tozalash boshlandi...\n")
    
    # Papkalarni o'chirish
    for root, dirs, files in os.walk(base_dir):
        for folder in folders_to_remove:
            if folder in dirs:
                folder_path = os.path.join(root, folder)
                try:
                    # Papka hajmini hisoblash
                    folder_size = sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(folder_path)
                        for filename in filenames
                    )
                    
                    shutil.rmtree(folder_path)
                    removed_count += 1
                    freed_space += folder_size
                    print(f"✓ O'chirildi: {folder_path} ({folder_size / 1024:.1f} KB)")
                except Exception as e:
                    print(f"✗ Xatolik: {folder_path} - {e}")
    
    # Fayllarni o'chirish
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            for pattern in file_patterns:
                if file.endswith(pattern.replace('*', '')):
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        removed_count += 1
                        freed_space += file_size
                        print(f"✓ O'chirildi: {file_path} ({file_size / 1024:.1f} KB)")
                    except Exception as e:
                        print(f"✗ Xatolik: {file_path} - {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Tozalash tugadi!")
    print(f"📦 O'chirilgan fayllar: {removed_count} ta")
    print(f"💾 Bo'shatilgan joy: {freed_space / (1024*1024):.2f} MB")
    print(f"{'='*60}\n")
    
    # Qolgan kerak bo'lmagan fayllar haqida ogohlantirish
    print("⚠️  Qo'lda tekshiring:")
    print("   - venv/ papkasini hostingga yuklamang")
    print("   - .git/ papkasini hostingga yuklamang (FTP ishlatayotgan bo'lsangiz)")
    print("   - db.sqlite3 file backup qiling (production DB uchun)")
    print("   - .env faylini xavfsiz saqlang\n")

if __name__ == '__main__':
    cleanup_production()
