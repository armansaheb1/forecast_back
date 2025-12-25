"""
Management command to add placeholder image information for Tarot cards.
This creates a note about image requirements but doesn't set actual images.
Images should be uploaded through Django admin panel.
Run with: python manage.py add_tarot_image_placeholders
"""
from django.core.management.base import BaseCommand
from main.models import TarotCard


class Command(BaseCommand):
    help = 'Add placeholder image information for Tarot cards'

    def handle(self, *args, **options):
        total_cards = TarotCard.objects.count()
        cards_with_images = TarotCard.objects.exclude(image__isnull=True).exclude(image="").count()
        cards_needing_images = total_cards - cards_with_images
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Tarot Cards Image Status:\n'
                f'  Total cards: {total_cards}\n'
                f'  Cards with images: {cards_with_images}\n'
                f'  Cards needing images: {cards_needing_images}\n'
                f'\n'
                f'📝 To upload images:\n'
                f'  1. Go to Django admin panel: /admin/main/tarotcard/\n'
                f'  2. Click on each card\n'
                f'  3. Upload image in "عکس کارت" (Card Image) field\n'
                f'  4. Recommended specifications:\n'
                f'     - Format: JPG or PNG\n'
                f'     - Size: 300x500 pixels (or similar aspect ratio)\n'
                f'     - File size: Under 500KB per image\n'
                f'     - Background: Transparent or themed background\n'
                f'\n'
                f'💡 Tip: You can bulk upload images by:\n'
                f'  - Preparing all images with consistent naming (e.g., "the_fool.jpg")\n'
                f'  - Uploading them one by one through admin panel\n'
                f'  - Or using Django admin bulk actions if available\n'
            )
        )
        
        # List cards without images
        if cards_needing_images > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'\n📋 Cards needing images ({cards_needing_images}):\n'
                )
            )
            for card in TarotCard.objects.filter(image__isnull=True) | TarotCard.objects.filter(image=""):
                self.stdout.write(f'  - {card.name} ({card.get_suit_display()})')

