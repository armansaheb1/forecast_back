#!/usr/bin/env python3
"""
اسکریپت برای کراپ کردن و حذف پیکسل‌های شفاف (ترنسپرنت) و سفید از دور تصاویر کارت‌های تاروت
این اسکریپت تمام PNG های موجود در پوشه tarotcards را پردازش می‌کند
"""

import os
from PIL import Image
import sys

def is_empty_pixel(r, g, b, a, white_threshold=250):
    """
    بررسی اینکه آیا پیکسل خالی است (شفاف یا سفید)
    white_threshold: حد آستانه برای تشخیص سفید (پیش‌فرض 250)
    """
    # پیکسل شفاف
    if a == 0:
        return True
    
    # پیکسل سفید یا تقریباً سفید
    if r >= white_threshold and g >= white_threshold and b >= white_threshold:
        return True
    
    return False

def get_bbox_with_content(img, white_threshold=250):
    """
    پیدا کردن محدوده (bounding box) محتوای غیرخالی در تصویر
    پیکسل‌های شفاف و سفید به عنوان خالی در نظر گرفته می‌شوند
    """
    # تبدیل به RGBA اگر نیست
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # گرفتن داده‌های پیکسل
    pixels = img.load()
    width, height = img.size
    
    # پیدا کردن حداقل و حداکثر مختصات پیکسل‌های غیرخالی
    min_x = width
    min_y = height
    max_x = 0
    max_y = 0
    
    found_content = False
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # اگر پیکسل خالی نباشد (نه شفاف و نه سفید)
            if not is_empty_pixel(r, g, b, a, white_threshold):
                found_content = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    if not found_content:
        return None
    
    return (min_x, min_y, max_x + 1, max_y + 1)

def crop_transparent_edges(image_path, output_path=None, white_threshold=250):
    """
    کراپ کردن حاشیه‌های شفاف و سفید از یک تصویر PNG
    white_threshold: حد آستانه برای تشخیص سفید (0-255)
    """
    try:
        # باز کردن تصویر
        img = Image.open(image_path)
        original_mode = img.mode
        
        # تبدیل به RGBA برای پردازش
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # پیدا کردن محدوده محتوا (بدون پیکسل‌های شفاف و سفید)
        bbox = get_bbox_with_content(img, white_threshold)
        
        if bbox is None:
            print(f"⚠️  {os.path.basename(image_path)}: هیچ محتوای غیرخالی پیدا نشد")
            return False
        
        # بررسی اینکه آیا نیاز به کراپ هست
        original_size = img.size
        cropped_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
        
        if original_size == cropped_size:
            print(f"✓ {os.path.basename(image_path)}: نیاز به کراپ ندارد")
            return False
        
        # کراپ کردن تصویر
        cropped_img = img.crop(bbox)
        
        # اگر تصویر اصلی شفافیت نداشت، به RGB تبدیل می‌کنیم
        if original_mode in ('RGB', 'L') and cropped_img.mode == 'RGBA':
            # ایجاد یک بک‌گراند سفید برای تصاویر بدون شفافیت
            background = Image.new('RGB', cropped_img.size, (255, 255, 255))
            background.paste(cropped_img, mask=cropped_img.split()[-1] if cropped_img.mode == 'RGBA' else None)
            cropped_img = background
        
        # ذخیره تصویر کراپ شده
        if output_path is None:
            output_path = image_path
        
        # حفظ فرمت PNG
        if cropped_img.mode == 'RGBA':
            cropped_img.save(output_path, 'PNG', optimize=True)
        else:
            cropped_img.save(output_path, 'PNG', optimize=True)
        
        print(f"✓ {os.path.basename(image_path)}: کراپ شد از {original_size} به {cropped_size}")
        return True
        
    except Exception as e:
        print(f"❌ خطا در پردازش {os.path.basename(image_path)}: {str(e)}")
        return False

def main():
    # مسیر پوشه tarotcards
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tarot_dir = os.path.join(script_dir, 'media', 'tarotcards')
    
    if not os.path.exists(tarot_dir):
        print(f"❌ پوشه {tarot_dir} پیدا نشد!")
        sys.exit(1)
    
    print(f"📁 پردازش تصاویر در: {tarot_dir}\n")
    
    # پیدا کردن تمام فایل‌های PNG
    png_files = [f for f in os.listdir(tarot_dir) if f.lower().endswith('.png')]
    
    if not png_files:
        print("⚠️  هیچ فایل PNG پیدا نشد!")
        sys.exit(0)
    
    print(f"📊 تعداد فایل‌های PNG پیدا شده: {len(png_files)}\n")
    
    # پردازش هر فایل
    processed = 0
    cropped = 0
    
    for filename in sorted(png_files):
        file_path = os.path.join(tarot_dir, filename)
        if crop_transparent_edges(file_path):
            cropped += 1
        processed += 1
    
    print(f"\n{'='*60}")
    print(f"✅ پردازش کامل شد!")
    print(f"📊 آمار:")
    print(f"   - کل فایل‌ها: {processed}")
    print(f"   - فایل‌های کراپ شده: {cropped}")
    print(f"   - فایل‌های بدون تغییر: {processed - cropped}")

if __name__ == '__main__':
    main()

