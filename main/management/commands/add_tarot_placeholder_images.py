"""
Management command to add placeholder image URLs for Tarot cards.
This sets a default placeholder image URL that can be replaced later.
Run with: python manage.py add_tarot_placeholder_images
"""
from django.core.management.base import BaseCommand
from main.models import TarotCard
import os


class Command(BaseCommand):
    help = 'Add placeholder image URLs for Tarot cards'

    def handle(self, *args, **options):
        # Placeholder image URL - you can replace this with your actual image hosting service
        # For now, using a placeholder service that generates card images
        # You can also use local paths like '/static/tarot_cards/{card_name}.jpg'
        
        placeholder_base_url = 'https://via.placeholder.com/300x500/2A1A4E/D4AF37?text='
        
        updated_count = 0
        
        for card in TarotCard.objects.all().order_by('order'):
            # Only set placeholder if no image is already set
            if not card.image:
                # Create a safe filename-friendly version of card name
                safe_name = card.name.replace(' ', '_').replace("'", '').lower()
                
                # For now, we'll just note that images need to be uploaded
                # The actual image upload should be done through admin panel
                self.stdout.write(
                    self.style.NOTICE(f'○ Card "{card.name}" needs image upload in admin panel')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Card "{card.name}" already has an image')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nSummary:\n'
                f'  Total cards: {TarotCard.objects.count()}\n'
                f'  Cards with images: {TarotCard.objects.exclude(image__isnull=True).exclude(image="").count()}\n'
                f'  Cards needing images: {TarotCard.objects.filter(image__isnull=True).count() + TarotCard.objects.filter(image="").count()}\n'
                f'\n'
                f'  To upload images:\n'
                f'  1. Go to Django admin panel\n'
                f'  2. Navigate to "کارت‌های تاروت" (Tarot Cards)\n'
                f'  3. Click on each card and upload its image\n'
                f'  4. Recommended image size: 300x500 pixels or similar aspect ratio\n'
            )
        )

