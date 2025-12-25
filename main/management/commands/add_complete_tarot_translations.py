"""
Management command to add complete translations for all 78 Tarot cards in 10 main languages.
Languages: en, fa, ar, es, fr, de, it, ru, hi, zh
Run with: python manage.py add_complete_tarot_translations
"""
from django.core.management.base import BaseCommand
from main.models import TarotCard


class Command(BaseCommand):
    help = 'Add complete translations for all Tarot cards in 10 main languages'

    def handle(self, *args, **options):
        # Complete translations for all 78 cards in 10 languages
        translations = {
            # Major Arcana
            'The Fool': {
                'en': 'The Fool', 'fa': 'احمق', 'ar': 'الأحمق', 'es': 'El Loco', 
                'fr': 'Le Mat', 'de': 'Der Narr', 'it': 'Il Matto', 
                'ru': 'Дурак', 'hi': 'मूर्ख', 'zh': '愚者'
            },
            'The Magician': {
                'en': 'The Magician', 'fa': 'جادوگر', 'ar': 'الساحر', 'es': 'El Mago', 
                'fr': 'Le Bateleur', 'de': 'Der Magier', 'it': 'Il Mago', 
                'ru': 'Маг', 'hi': 'जादूगर', 'zh': '魔术师'
            },
            'The High Priestess': {
                'en': 'The High Priestess', 'fa': 'کاهنه اعظم', 'ar': 'الكاهنة العليا', 
                'es': 'La Sacerdotisa', 'fr': 'La Papesse', 'de': 'Die Hohepriesterin', 
                'it': 'La Papessa', 'ru': 'Верховная Жрица', 'hi': 'उच्च पुजारिन', 'zh': '女祭司'
            },
            'The Empress': {
                'en': 'The Empress', 'fa': 'ملکه', 'ar': 'الإمبراطورة', 
                'es': 'La Emperatriz', 'fr': "L'Impératrice", 'de': 'Die Kaiserin', 
                'it': "L'Imperatrice", 'ru': 'Императрица', 'hi': 'महारानी', 'zh': '皇后'
            },
            'The Emperor': {
                'en': 'The Emperor', 'fa': 'امپراتور', 'ar': 'الإمبراطور', 
                'es': 'El Emperador', 'fr': "L'Empereur", 'de': 'Der Kaiser', 
                'it': "L'Imperatore", 'ru': 'Император', 'hi': 'सम्राट', 'zh': '皇帝'
            },
            'The Hierophant': {
                'en': 'The Hierophant', 'fa': 'راهب اعظم', 'ar': 'الكاهن الأعظم', 
                'es': 'El Hierofante', 'fr': 'Le Pape', 'de': 'Der Hierophant', 
                'it': 'Il Papa', 'ru': 'Иерофант', 'hi': 'महायाजक', 'zh': '教皇'
            },
            'The Lovers': {
                'en': 'The Lovers', 'fa': 'عشاق', 'ar': 'العشاق', 
                'es': 'Los Enamorados', 'fr': 'L\'Amoureux', 'de': 'Die Liebenden', 
                'it': 'Gli Amanti', 'ru': 'Влюбленные', 'hi': 'प्रेमी', 'zh': '恋人'
            },
            'The Chariot': {
                'en': 'The Chariot', 'fa': 'ارابه', 'ar': 'العربة', 
                'es': 'El Carro', 'fr': 'Le Chariot', 'de': 'Der Wagen', 
                'it': 'Il Carro', 'ru': 'Колесница', 'hi': 'रथ', 'zh': '战车'
            },
            'Strength': {
                'en': 'Strength', 'fa': 'قدرت', 'ar': 'القوة', 
                'es': 'La Fuerza', 'fr': 'La Force', 'de': 'Die Kraft', 
                'it': 'La Forza', 'ru': 'Сила', 'hi': 'शक्ति', 'zh': '力量'
            },
            'The Hermit': {
                'en': 'The Hermit', 'fa': 'راهب', 'ar': 'الناسك', 
                'es': 'El Ermitaño', 'fr': 'L\'Ermite', 'de': 'Der Eremit', 
                'it': 'L\'Eremita', 'ru': 'Отшельник', 'hi': 'सन्यासी', 'zh': '隐者'
            },
            'Wheel of Fortune': {
                'en': 'Wheel of Fortune', 'fa': 'چرخ تقدیر', 'ar': 'عجلة الحظ', 
                'es': 'La Rueda de la Fortuna', 'fr': 'La Roue de Fortune', 
                'de': 'Das Rad des Schicksals', 'it': 'La Ruota della Fortuna', 
                'ru': 'Колесо Фортуны', 'hi': 'भाग्य चक्र', 'zh': '命运之轮'
            },
            'Justice': {
                'en': 'Justice', 'fa': 'عدالت', 'ar': 'العدالة', 
                'es': 'La Justicia', 'fr': 'La Justice', 'de': 'Die Gerechtigkeit', 
                'it': 'La Giustizia', 'ru': 'Справедливость', 'hi': 'न्याय', 'zh': '正义'
            },
            'The Hanged Man': {
                'en': 'The Hanged Man', 'fa': 'معلق', 'ar': 'المعلق', 
                'es': 'El Colgado', 'fr': 'Le Pendu', 'de': 'Der Gehängte', 
                'it': 'L\'Appeso', 'ru': 'Повешенный', 'hi': 'लटका हुआ आदमी', 'zh': '倒吊人'
            },
            'Death': {
                'en': 'Death', 'fa': 'مرگ', 'ar': 'الموت', 
                'es': 'La Muerte', 'fr': 'La Mort', 'de': 'Der Tod', 
                'it': 'La Morte', 'ru': 'Смерть', 'hi': 'मृत्यु', 'zh': '死神'
            },
            'Temperance': {
                'en': 'Temperance', 'fa': 'اعتدال', 'ar': 'الاعتدال', 
                'es': 'La Templanza', 'fr': 'Tempérance', 'de': 'Die Mäßigung', 
                'it': 'La Temperanza', 'ru': 'Умеренность', 'hi': 'संयम', 'zh': '节制'
            },
            'The Devil': {
                'en': 'The Devil', 'fa': 'شیطان', 'ar': 'الشيطان', 
                'es': 'El Diablo', 'fr': 'Le Diable', 'de': 'Der Teufel', 
                'it': 'Il Diavolo', 'ru': 'Дьявол', 'hi': 'शैतान', 'zh': '恶魔'
            },
            'The Tower': {
                'en': 'The Tower', 'fa': 'برج', 'ar': 'البرج', 
                'es': 'La Torre', 'fr': 'La Maison Dieu', 'de': 'Der Turm', 
                'it': 'La Torre', 'ru': 'Башня', 'hi': 'मीनार', 'zh': '塔'
            },
            'The Star': {
                'en': 'The Star', 'fa': 'ستاره', 'ar': 'النجمة', 
                'es': 'La Estrella', 'fr': 'L\'Étoile', 'de': 'Der Stern', 
                'it': 'La Stella', 'ru': 'Звезда', 'hi': 'तारा', 'zh': '星星'
            },
            'The Moon': {
                'en': 'The Moon', 'fa': 'ماه', 'ar': 'القمر', 
                'es': 'La Luna', 'fr': 'La Lune', 'de': 'Der Mond', 
                'it': 'La Luna', 'ru': 'Луна', 'hi': 'चंद्रमा', 'zh': '月亮'
            },
            'The Sun': {
                'en': 'The Sun', 'fa': 'خورشید', 'ar': 'الشمس', 
                'es': 'El Sol', 'fr': 'Le Soleil', 'de': 'Die Sonne', 
                'it': 'Il Sole', 'ru': 'Солнце', 'hi': 'सूर्य', 'zh': '太阳'
            },
            'Judgment': {
                'en': 'Judgment', 'fa': 'داوری', 'ar': 'الدينونة', 
                'es': 'El Juicio', 'fr': 'Le Jugement', 'de': 'Das Gericht', 
                'it': 'Il Giudizio', 'ru': 'Суд', 'hi': 'न्याय', 'zh': '审判'
            },
            'The World': {
                'en': 'The World', 'fa': 'جهان', 'ar': 'العالم', 
                'es': 'El Mundo', 'fr': 'Le Monde', 'de': 'Die Welt', 
                'it': 'Il Mondo', 'ru': 'Мир', 'hi': 'संसार', 'zh': '世界'
            },
        }
        
        # Translations for Minor Arcana suits
        suit_translations = {
            'Wands': {
                'en': 'Wands', 'fa': 'عصا', 'ar': 'العصي', 'es': 'Bastos', 
                'fr': 'Bâtons', 'de': 'Stäbe', 'it': 'Bastoni', 
                'ru': 'Жезлы', 'hi': 'छड़ी', 'zh': '权杖'
            },
            'Cups': {
                'en': 'Cups', 'fa': 'جام', 'ar': 'الكؤوس', 'es': 'Copas', 
                'fr': 'Coupes', 'de': 'Kelche', 'it': 'Coppe', 
                'ru': 'Кубки', 'hi': 'कप', 'zh': '圣杯'
            },
            'Swords': {
                'en': 'Swords', 'fa': 'شمشیر', 'ar': 'السيوف', 'es': 'Espadas', 
                'fr': 'Épées', 'de': 'Schwerter', 'it': 'Spade', 
                'ru': 'Мечи', 'hi': 'तलवार', 'zh': '宝剑'
            },
            'Pentacles': {
                'en': 'Pentacles', 'fa': 'سکه', 'ar': 'العملات', 'es': 'Oros', 
                'fr': 'Deniers', 'de': 'Münzen', 'it': 'Denari', 
                'ru': 'Пентакли', 'hi': 'सिक्के', 'zh': '星币'
            },
        }
        
        # Number translations
        number_translations = {
            'Ace': {
                'en': 'Ace', 'fa': 'آس', 'ar': 'الآس', 'es': 'As', 
                'fr': 'As', 'de': 'Ass', 'it': 'Asso', 
                'ru': 'Туз', 'hi': 'एस', 'zh': '王牌'
            },
            'Two': {
                'en': 'Two', 'fa': 'دو', 'ar': 'اثنان', 'es': 'Dos', 
                'fr': 'Deux', 'de': 'Zwei', 'it': 'Due', 
                'ru': 'Двойка', 'hi': 'दो', 'zh': '二'
            },
            'Three': {
                'en': 'Three', 'fa': 'سه', 'ar': 'ثلاثة', 'es': 'Tres', 
                'fr': 'Trois', 'de': 'Drei', 'it': 'Tre', 
                'ru': 'Тройка', 'hi': 'तीन', 'zh': '三'
            },
            'Four': {
                'en': 'Four', 'fa': 'چهار', 'ar': 'أربعة', 'es': 'Cuatro', 
                'fr': 'Quatre', 'de': 'Vier', 'it': 'Quattro', 
                'ru': 'Четверка', 'hi': 'चार', 'zh': '四'
            },
            'Five': {
                'en': 'Five', 'fa': 'پنج', 'ar': 'خمسة', 'es': 'Cinco', 
                'fr': 'Cinq', 'de': 'Fünf', 'it': 'Cinque', 
                'ru': 'Пятерка', 'hi': 'पांच', 'zh': '五'
            },
            'Six': {
                'en': 'Six', 'fa': 'شش', 'ar': 'ستة', 'es': 'Seis', 
                'fr': 'Six', 'de': 'Sechs', 'it': 'Sei', 
                'ru': 'Шестерка', 'hi': 'छह', 'zh': '六'
            },
            'Seven': {
                'en': 'Seven', 'fa': 'هفت', 'ar': 'سبعة', 'es': 'Siete', 
                'fr': 'Sept', 'de': 'Sieben', 'it': 'Sette', 
                'ru': 'Семерка', 'hi': 'सात', 'zh': '七'
            },
            'Eight': {
                'en': 'Eight', 'fa': 'هشت', 'ar': 'ثمانية', 'es': 'Ocho', 
                'fr': 'Huit', 'de': 'Acht', 'it': 'Otto', 
                'ru': 'Восьмерка', 'hi': 'आठ', 'zh': '八'
            },
            'Nine': {
                'en': 'Nine', 'fa': 'نه', 'ar': 'تسعة', 'es': 'Nueve', 
                'fr': 'Neuf', 'de': 'Neun', 'it': 'Nove', 
                'ru': 'Девятка', 'hi': 'नौ', 'zh': '九'
            },
            'Ten': {
                'en': 'Ten', 'fa': 'ده', 'ar': 'عشرة', 'es': 'Diez', 
                'fr': 'Dix', 'de': 'Zehn', 'it': 'Dieci', 
                'ru': 'Десятка', 'hi': 'दस', 'zh': '十'
            },
            'Page': {
                'en': 'Page', 'fa': 'پیشکار', 'ar': 'الخادم', 'es': 'Paje', 
                'fr': 'Valet', 'de': 'Bube', 'it': 'Fante', 
                'ru': 'Паж', 'hi': 'पेज', 'zh': '侍从'
            },
            'Knight': {
                'en': 'Knight', 'fa': 'شوالیه', 'ar': 'الفارس', 'es': 'Caballero', 
                'fr': 'Cavalier', 'de': 'Ritter', 'it': 'Cavaliere', 
                'ru': 'Рыцарь', 'hi': 'घुड़सवार', 'zh': '骑士'
            },
            'Queen': {
                'en': 'Queen', 'fa': 'ملکه', 'ar': 'الملكة', 'es': 'Reina', 
                'fr': 'Reine', 'de': 'Königin', 'it': 'Regina', 
                'ru': 'Королева', 'hi': 'रानी', 'zh': '皇后'
            },
            'King': {
                'en': 'King', 'fa': 'شاه', 'ar': 'الملك', 'es': 'Rey', 
                'fr': 'Roi', 'de': 'König', 'it': 'Re', 
                'ru': 'Король', 'hi': 'राजा', 'zh': '国王'
            },
        }
        
        updated_count = 0
        
        for card in TarotCard.objects.all().order_by('order'):
            # Initialize names_translations if empty
            if not card.names_translations:
                card.names_translations = {}
            
            # Check if we have a direct translation for this card (Major Arcana)
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
                    
                    # Get suit translation
                    suit_key = suit_part if suit_part in suit_translations else None
                    if not suit_key:
                        # Try to find matching suit
                        for key in suit_translations.keys():
                            if key.lower() == card.suit:
                                suit_key = key
                                break
                    
                    # Get number translation
                    number_key = number_part if number_part in number_translations else None
                    
                    # Build translations for all languages (always update to ensure correct format)
                    for lang in ['en', 'fa', 'ar', 'es', 'fr', 'de', 'it', 'ru', 'hi', 'zh']:
                        # Always update Minor Arcana translations to ensure correct format
                        if lang not in card.names_translations or card.suit in ['wands', 'cups', 'swords', 'pentacles']:
                            if number_key and suit_key:
                                num_trans = number_translations[number_key].get(lang, number_part)
                                suit_trans = suit_translations[suit_key].get(lang, suit_part)
                                
                                # Build translation based on language structure
                                if lang == 'fa':
                                    card.names_translations[lang] = f'{num_trans} {suit_trans}'
                                elif lang == 'ar':
                                    card.names_translations[lang] = f'{num_trans} {suit_trans}'
                                elif lang == 'hi':
                                    card.names_translations[lang] = f'{num_trans} {suit_trans}'
                                elif lang == 'zh':
                                    card.names_translations[lang] = f'{num_trans}{suit_trans}'
                                elif lang == 'es':
                                    # Spanish: "As de Bastos"
                                    card.names_translations[lang] = f'{num_trans} de {suit_trans}'
                                elif lang == 'fr':
                                    # French: "As de Bâtons"
                                    card.names_translations[lang] = f'{num_trans} de {suit_trans}'
                                elif lang == 'it':
                                    # Italian: "Asso di Bastoni"
                                    card.names_translations[lang] = f'{num_trans} di {suit_trans}'
                                elif lang == 'ru':
                                    # Russian: "Туз Жезлов" (genitive case, no preposition)
                                    card.names_translations[lang] = f'{num_trans} {suit_trans}'
                                elif lang == 'de':
                                    # German: "Ass der Stäbe" (genitive)
                                    # For simplicity, using "Stäbe-Ass" format or just "Ass Stäbe"
                                    card.names_translations[lang] = f'{num_trans} {suit_trans}'
                                else:  # en
                                    card.names_translations[lang] = f'{num_trans} of {suit_trans}'
                                updated_count += 1
            
            card.save()
            if updated_count % 10 == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated: {card.name} ({updated_count} translations so far)')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nSummary:\n'
                f'  Total cards processed: {TarotCard.objects.count()}\n'
                f'  Total translation entries added/updated: {updated_count}\n'
                f'  Languages: en, fa, ar, es, fr, de, it, ru, hi, zh'
            )
        )

