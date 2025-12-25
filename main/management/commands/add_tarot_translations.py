"""
Management command to add basic translations for Tarot card names.
This adds English and Persian translations as a starting point.
Run with: python manage.py add_tarot_translations
"""
from django.core.management.base import BaseCommand
from main.models import TarotCard


class Command(BaseCommand):
    help = 'Add basic translations for Tarot card names'

    def handle(self, *args, **options):
        # Basic translations for Major Arcana (Persian and Arabic)
        translations = {
            'The Fool': {'fa': 'احمق', 'ar': 'الأحمق'},
            'The Magician': {'fa': 'جادوگر', 'ar': 'الساحر'},
            'The High Priestess': {'fa': 'کاهنه اعظم', 'ar': 'الكاهنة العليا'},
            'The Empress': {'fa': 'ملکه', 'ar': 'الإمبراطورة'},
            'The Emperor': {'fa': 'امپراتور', 'ar': 'الإمبراطور'},
            'The Hierophant': {'fa': 'راهب اعظم', 'ar': 'الكاهن الأعظم'},
            'The Lovers': {'fa': 'عشاق', 'ar': 'العشاق'},
            'The Chariot': {'fa': 'ارابه', 'ar': 'العربة'},
            'Strength': {'fa': 'قدرت', 'ar': 'القوة'},
            'The Hermit': {'fa': 'راهب', 'ar': 'الناسك'},
            'Wheel of Fortune': {'fa': 'چرخ تقدیر', 'ar': 'عجلة الحظ'},
            'Justice': {'fa': 'عدالت', 'ar': 'العدالة'},
            'The Hanged Man': {'fa': 'معلق', 'ar': 'المعلق'},
            'Death': {'fa': 'مرگ', 'ar': 'الموت'},
            'Temperance': {'fa': 'اعتدال', 'ar': 'الاعتدال'},
            'The Devil': {'fa': 'شیطان', 'ar': 'الشيطان'},
            'The Tower': {'fa': 'برج', 'ar': 'البرج'},
            'The Star': {'fa': 'ستاره', 'ar': 'النجمة'},
            'The Moon': {'fa': 'ماه', 'ar': 'القمر'},
            'The Sun': {'fa': 'خورشید', 'ar': 'الشمس'},
            'Judgment': {'fa': 'داوری', 'ar': 'الدينونة'},
            'The World': {'fa': 'جهان', 'ar': 'العالم'},
        }
        
        # Add translations for Minor Arcana
        minor_arcana_translations = {
            'Wands': {'fa': 'عصا', 'ar': 'العصي'},
            'Cups': {'fa': 'جام', 'ar': 'الكؤوس'},
            'Swords': {'fa': 'شمشیر', 'ar': 'السيوف'},
            'Pentacles': {'fa': 'سکه', 'ar': 'العملات'},
            'Ace': {'fa': 'آس', 'ar': 'الآس'},
            'Two': {'fa': 'دو', 'ar': 'اثنان'},
            'Three': {'fa': 'سه', 'ar': 'ثلاثة'},
            'Four': {'fa': 'چهار', 'ar': 'أربعة'},
            'Five': {'fa': 'پنج', 'ar': 'خمسة'},
            'Six': {'fa': 'شش', 'ar': 'ستة'},
            'Seven': {'fa': 'هفت', 'ar': 'سبعة'},
            'Eight': {'fa': 'هشت', 'ar': 'ثمانية'},
            'Nine': {'fa': 'نه', 'ar': 'تسعة'},
            'Ten': {'fa': 'ده', 'ar': 'عشرة'},
            'Page': {'fa': 'پیشکار', 'ar': 'الخادم'},
            'Knight': {'fa': 'شوالیه', 'ar': 'الفارس'},
            'Queen': {'fa': 'ملکه', 'ar': 'الملكة'},
            'King': {'fa': 'شاه', 'ar': 'الملك'},
            'of': {'fa': '', 'ar': ''},
        }
        
        updated_count = 0
        
        for card in TarotCard.objects.all():
            # Initialize names_translations if empty
            if not card.names_translations:
                card.names_translations = {}
            
            # Add English name if not present
            if 'en' not in card.names_translations:
                card.names_translations['en'] = card.name_en or card.name
            
            # Check if we have a direct translation for this card
            if card.name in translations:
                for lang, trans in translations[card.name].items():
                    if lang not in card.names_translations or not card.names_translations[lang]:
                        card.names_translations[lang] = trans
                        updated_count += 1
            
            # For Minor Arcana, build translation from parts
            elif card.suit in ['wands', 'cups', 'swords', 'pentacles']:
                card_name_parts = card.name.split()
                if len(card_name_parts) >= 3:  # e.g., "Ace of Wands"
                    number_part = card_name_parts[0]
                    suit_part = card_name_parts[2]
                    
                    # Build Persian translation
                    if 'fa' not in card.names_translations or not card.names_translations.get('fa'):
                        fa_number = minor_arcana_translations.get(number_part, {}).get('fa', number_part)
                        fa_suit = minor_arcana_translations.get(suit_part, {}).get('fa', suit_part)
                        if fa_number and fa_suit:
                            card.names_translations['fa'] = f'{fa_number} {fa_suit}'
                            updated_count += 1
                    
                    # Build Arabic translation
                    if 'ar' not in card.names_translations or not card.names_translations.get('ar'):
                        ar_number = minor_arcana_translations.get(number_part, {}).get('ar', number_part)
                        ar_suit = minor_arcana_translations.get(suit_part, {}).get('ar', suit_part)
                        if ar_number and ar_suit:
                            card.names_translations['ar'] = f'{ar_number} {ar_suit}'
                            updated_count += 1
            
            card.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated translations for: {card.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nSummary:\n'
                f'  Updated translations for {TarotCard.objects.count()} cards\n'
                f'  Total translation entries added/updated: {updated_count}'
            )
        )

