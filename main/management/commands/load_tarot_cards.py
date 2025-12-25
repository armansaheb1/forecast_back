"""
Management command to load all 78 Tarot cards into the database.
Run with: python manage.py load_tarot_cards
"""
from django.core.management.base import BaseCommand
from main.models import TarotCard


class Command(BaseCommand):
    help = 'Load all 78 Tarot cards into the database'

    def handle(self, *args, **options):
        # Mapping from Flutter suit names to Django suit choices
        suit_mapping = {
            'Major Arcana': 'major',
            'Wands': 'wands',
            'Cups': 'cups',
            'Swords': 'swords',
            'Pentacles': 'pentacles',
        }

        # All 78 Tarot cards data
        cards_data = [
            # Major Arcana (22 cards)
            {'name': 'The Fool', 'name_en': 'The Fool', 'suit': 'Major Arcana', 'number': 0, 'emoji': '🃏',
             'meaning': 'New beginnings, innocence, spontaneity, a free spirit',
             'reversed_meaning': 'Recklessness, risk-taking, poor judgment, naivety', 'order': 0},
            {'name': 'The Magician', 'name_en': 'The Magician', 'suit': 'Major Arcana', 'number': 1, 'emoji': '✨',
             'meaning': 'Manifestation, resourcefulness, power, inspired action',
             'reversed_meaning': 'Manipulation, poor planning, untapped talents', 'order': 1},
            {'name': 'The High Priestess', 'name_en': 'The High Priestess', 'suit': 'Major Arcana', 'number': 2, 'emoji': '🌙',
             'meaning': 'Intuition, sacred knowledge, divine feminine, the subconscious mind',
             'reversed_meaning': 'Secrets, disconnected from intuition, withdrawal and silence', 'order': 2},
            {'name': 'The Empress', 'name_en': 'The Empress', 'suit': 'Major Arcana', 'number': 3, 'emoji': '👑',
             'meaning': 'Femininity, beauty, nature, nurturing, abundance',
             'reversed_meaning': 'Creative block, dependence on others', 'order': 3},
            {'name': 'The Emperor', 'name_en': 'The Emperor', 'suit': 'Major Arcana', 'number': 4, 'emoji': '⚔️',
             'meaning': 'Authority, establishment, structure, a father figure',
             'reversed_meaning': 'Domination, excessive control, lack of discipline, inflexibility', 'order': 4},
            {'name': 'The Hierophant', 'name_en': 'The Hierophant', 'suit': 'Major Arcana', 'number': 5, 'emoji': '📿',
             'meaning': 'Spiritual wisdom, religious beliefs, conformity, tradition, conformity',
             'reversed_meaning': 'Personal beliefs, freedom, challenging the status quo', 'order': 5},
            {'name': 'The Lovers', 'name_en': 'The Lovers', 'suit': 'Major Arcana', 'number': 6, 'emoji': '💑',
             'meaning': 'Love, harmony, relationships, values alignment, choices',
             'reversed_meaning': 'Self-love, disharmony, imbalance, misalignment of values', 'order': 6},
            {'name': 'The Chariot', 'name_en': 'The Chariot', 'suit': 'Major Arcana', 'number': 7, 'emoji': '🏇',
             'meaning': 'Control, willpower, success, action, determination',
             'reversed_meaning': 'Lack of control, lack of direction, aggression', 'order': 7},
            {'name': 'Strength', 'name_en': 'Strength', 'suit': 'Major Arcana', 'number': 8, 'emoji': '🦁',
             'meaning': 'Strength, courage, persuasion, influence, compassion',
             'reversed_meaning': 'Inner strength, self-doubt, weakness, insecurity', 'order': 8},
            {'name': 'The Hermit', 'name_en': 'The Hermit', 'suit': 'Major Arcana', 'number': 9, 'emoji': '🕯️',
             'meaning': 'Soul searching, introspection, being alone, inner guidance',
             'reversed_meaning': 'Isolation, withdrawal, rejection', 'order': 9},
            {'name': 'Wheel of Fortune', 'name_en': 'Wheel of Fortune', 'suit': 'Major Arcana', 'number': 10, 'emoji': '🎡',
             'meaning': 'Good luck, karma, life cycles, destiny, a turning point',
             'reversed_meaning': 'Bad luck, resistance to change, breaking cycles', 'order': 10},
            {'name': 'Justice', 'name_en': 'Justice', 'suit': 'Major Arcana', 'number': 11, 'emoji': '⚖️',
             'meaning': 'Justice, fairness, truth, cause and effect, law',
             'reversed_meaning': 'Unfairness, lack of accountability, dishonesty', 'order': 11},
            {'name': 'The Hanged Man', 'name_en': 'The Hanged Man', 'suit': 'Major Arcana', 'number': 12, 'emoji': '🙃',
             'meaning': 'Pause, surrender, letting go, new perspectives',
             'reversed_meaning': 'Delays, resistance, stalling, indecision', 'order': 12},
            {'name': 'Death', 'name_en': 'Death', 'suit': 'Major Arcana', 'number': 13, 'emoji': '💀',
             'meaning': 'Endings, change, transformation, transition',
             'reversed_meaning': 'Resistance to change, inability to move on, stagnation', 'order': 13},
            {'name': 'Temperance', 'name_en': 'Temperance', 'suit': 'Major Arcana', 'number': 14, 'emoji': '🍷',
             'meaning': 'Balance, moderation, patience, purpose',
             'reversed_meaning': 'Imbalance, excess, lack of long-term vision', 'order': 14},
            {'name': 'The Devil', 'name_en': 'The Devil', 'suit': 'Major Arcana', 'number': 15, 'emoji': '😈',
             'meaning': 'Shadow self, attachment, addiction, restriction, sexuality',
             'reversed_meaning': 'Releasing limiting beliefs, exploring dark thoughts, detachment', 'order': 15},
            {'name': 'The Tower', 'name_en': 'The Tower', 'suit': 'Major Arcana', 'number': 16, 'emoji': '🗼',
             'meaning': 'Sudden change, upheaval, chaos, revelation, awakening',
             'reversed_meaning': 'Disaster avoided, delayed disaster, resistance to change', 'order': 16},
            {'name': 'The Star', 'name_en': 'The Star', 'suit': 'Major Arcana', 'number': 17, 'emoji': '⭐',
             'meaning': 'Hope, faith, purpose, renewal, spirituality',
             'reversed_meaning': 'Lack of faith, despair, self-trust, disconnection', 'order': 17},
            {'name': 'The Moon', 'name_en': 'The Moon', 'suit': 'Major Arcana', 'number': 18, 'emoji': '🌙',
             'meaning': 'Illusion, fear, anxiety, subconscious, intuition',
             'reversed_meaning': 'Release of fear, repressed emotion, inner confusion', 'order': 18},
            {'name': 'The Sun', 'name_en': 'The Sun', 'suit': 'Major Arcana', 'number': 19, 'emoji': '☀️',
             'meaning': 'Positivity, fun, warmth, success, vitality',
             'reversed_meaning': 'Temporary depression, lack of success, sadness', 'order': 19},
            {'name': 'Judgment', 'name_en': 'Judgment', 'suit': 'Major Arcana', 'number': 20, 'emoji': '📯',
             'meaning': 'Judgment, reflection, evaluation, awakening, absolution',
             'reversed_meaning': 'Lack of self awareness, doubt, self-loathing', 'order': 20},
            {'name': 'The World', 'name_en': 'The World', 'suit': 'Major Arcana', 'number': 21, 'emoji': '🌍',
             'meaning': 'Completion, accomplishment, travel, achievement, fulfillment',
             'reversed_meaning': 'Incompletion, lack of closure, inability to find closure', 'order': 21},
            
            # Minor Arcana - Wands (14 cards)
            {'name': 'Ace of Wands', 'name_en': 'Ace of Wands', 'suit': 'Wands', 'number': 1, 'emoji': '🔥',
             'meaning': 'Inspiration, new opportunities, growth, potential',
             'reversed_meaning': 'Lack of direction, lack of passion, boredom, delays', 'order': 22},
            {'name': 'Two of Wands', 'name_en': 'Two of Wands', 'suit': 'Wands', 'number': 2, 'emoji': '🔥',
             'meaning': 'Future planning, progress, decisions, discovery',
             'reversed_meaning': 'Lack of planning, disorganization, fear of unknown', 'order': 23},
            {'name': 'Three of Wands', 'name_en': 'Three of Wands', 'suit': 'Wands', 'number': 3, 'emoji': '🔥',
             'meaning': 'Exploration, expansion, foresight, leadership',
             'reversed_meaning': 'Lack of foresight, delays, obstacles to long-term goals', 'order': 24},
            {'name': 'Four of Wands', 'name_en': 'Four of Wands', 'suit': 'Wands', 'number': 4, 'emoji': '🔥',
             'meaning': 'Celebration, harmony, home, community',
             'reversed_meaning': 'Lack of support, transition, home conflict', 'order': 25},
            {'name': 'Five of Wands', 'name_en': 'Five of Wands', 'suit': 'Wands', 'number': 5, 'emoji': '🔥',
             'meaning': 'Competition, conflict, disagreements, tension',
             'reversed_meaning': 'Conflict avoidance, tension release, truce', 'order': 26},
            {'name': 'Six of Wands', 'name_en': 'Six of Wands', 'suit': 'Wands', 'number': 6, 'emoji': '🔥',
             'meaning': 'Success, victory, public recognition, progress',
             'reversed_meaning': 'Lack of recognition, private success, fall from grace', 'order': 27},
            {'name': 'Seven of Wands', 'name_en': 'Seven of Wands', 'suit': 'Wands', 'number': 7, 'emoji': '🔥',
             'meaning': 'Challenge, competition, protection, perseverance',
             'reversed_meaning': 'Giving up, overwhelmed, defensive', 'order': 28},
            {'name': 'Eight of Wands', 'name_en': 'Eight of Wands', 'suit': 'Wands', 'number': 8, 'emoji': '🔥',
             'meaning': 'Rapid action, movement, quick decisions, speed',
             'reversed_meaning': 'Delays, frustration, resisting change, slowing down', 'order': 29},
            {'name': 'Nine of Wands', 'name_en': 'Nine of Wands', 'suit': 'Wands', 'number': 9, 'emoji': '🔥',
             'meaning': 'Resilience, courage, persistence, test of faith',
             'reversed_meaning': 'Stubbornness, rigidity, defensiveness, refusing to compromise', 'order': 30},
            {'name': 'Ten of Wands', 'name_en': 'Ten of Wands', 'suit': 'Wands', 'number': 10, 'emoji': '🔥',
             'meaning': 'Burden, responsibility, hard work, completion',
             'reversed_meaning': 'Inability to delegate, overstressed, burnt out, breakdown', 'order': 31},
            {'name': 'Page of Wands', 'name_en': 'Page of Wands', 'suit': 'Wands', 'number': 11, 'emoji': '🔥',
             'meaning': 'Inspiration, ideas, discovery, limitless potential',
             'reversed_meaning': 'Lack of direction, procrastination, creating conflict', 'order': 32},
            {'name': 'Knight of Wands', 'name_en': 'Knight of Wands', 'suit': 'Wands', 'number': 12, 'emoji': '🔥',
             'meaning': 'Energy, passion, inspired action, adventure, impulsiveness',
             'reversed_meaning': 'Lack of direction, no self-control, haste, scattered energy', 'order': 33},
            {'name': 'Queen of Wands', 'name_en': 'Queen of Wands', 'suit': 'Wands', 'number': 13, 'emoji': '🔥',
             'meaning': 'Courage, determination, joy, radiance, vibrancy',
             'reversed_meaning': 'Selfishness, jealousy, insecurities, lack of confidence', 'order': 34},
            {'name': 'King of Wands', 'name_en': 'King of Wands', 'suit': 'Wands', 'number': 14, 'emoji': '🔥',
             'meaning': 'Natural-born leader, vision, entrepreneur, honor',
             'reversed_meaning': 'Impulsiveness, haste, ruthless, high expectations', 'order': 35},
            
            # Minor Arcana - Cups (14 cards)
            {'name': 'Ace of Cups', 'name_en': 'Ace of Cups', 'suit': 'Cups', 'number': 1, 'emoji': '💧',
             'meaning': 'New feelings, spirituality, intuition, love',
             'reversed_meaning': 'Emotional loss, blocked creativity, emptiness', 'order': 36},
            {'name': 'Two of Cups', 'name_en': 'Two of Cups', 'suit': 'Cups', 'number': 2, 'emoji': '💧',
             'meaning': 'Unified love, partnership, mutual attraction',
             'reversed_meaning': 'Self-love, break-ups, disharmony, distrust', 'order': 37},
            {'name': 'Three of Cups', 'name_en': 'Three of Cups', 'suit': 'Cups', 'number': 3, 'emoji': '💧',
             'meaning': 'Celebration, friendship, creativity, collaborations',
             'reversed_meaning': 'Independence, alone time, hardcore partying, three\'s a crowd', 'order': 38},
            {'name': 'Four of Cups', 'name_en': 'Four of Cups', 'suit': 'Cups', 'number': 4, 'emoji': '💧',
             'meaning': 'Meditation, contemplation, apathy, reevaluation',
             'reversed_meaning': 'Clarity, acceptance, moving forward, awareness', 'order': 39},
            {'name': 'Five of Cups', 'name_en': 'Five of Cups', 'suit': 'Cups', 'number': 5, 'emoji': '💧',
             'meaning': 'Loss, grief, self-pity, regret',
             'reversed_meaning': 'Acceptance, moving on, finding peace, forgiveness', 'order': 40},
            {'name': 'Six of Cups', 'name_en': 'Six of Cups', 'suit': 'Cups', 'number': 6, 'emoji': '💧',
             'meaning': 'Revisiting the past, childhood memories, innocence, joy',
             'reversed_meaning': 'Living in the past, forgiveness, moving forward', 'order': 41},
            {'name': 'Seven of Cups', 'name_en': 'Seven of Cups', 'suit': 'Cups', 'number': 7, 'emoji': '💧',
             'meaning': 'Choices, wishful thinking, illusion, fantasy',
             'reversed_meaning': 'Lack of purpose, disarray, confusion, clarity', 'order': 42},
            {'name': 'Eight of Cups', 'name_en': 'Eight of Cups', 'suit': 'Cups', 'number': 8, 'emoji': '💧',
             'meaning': 'Walking away, disillusionment, leaving behind, searching for truth',
             'reversed_meaning': 'Acceptance, stagnation, fear of change, staying in bad situation', 'order': 43},
            {'name': 'Nine of Cups', 'name_en': 'Nine of Cups', 'suit': 'Cups', 'number': 9, 'emoji': '💧',
             'meaning': 'Contentment, satisfaction, gratitude, wish come true',
             'reversed_meaning': 'Lack of inner joy, smugness, dissatisfaction, inner happiness', 'order': 44},
            {'name': 'Ten of Cups', 'name_en': 'Ten of Cups', 'suit': 'Cups', 'number': 10, 'emoji': '💧',
             'meaning': 'Divine love, blissful relationships, harmony, alignment',
             'reversed_meaning': 'Disconnection, misalignment of values, broken home, domestic harmony', 'order': 45},
            {'name': 'Page of Cups', 'name_en': 'Page of Cups', 'suit': 'Cups', 'number': 11, 'emoji': '💧',
             'meaning': 'Happy surprise, dreamer, sensitivity, new feelings',
             'reversed_meaning': 'Emotional immaturity, insecurity, disappointment, creative block', 'order': 46},
            {'name': 'Knight of Cups', 'name_en': 'Knight of Cups', 'suit': 'Cups', 'number': 12, 'emoji': '💧',
             'meaning': 'Following the heart, idealist, romantic, charming',
             'reversed_meaning': 'Moodiness, disappointment, unrealistic, jealousy', 'order': 47},
            {'name': 'Queen of Cups', 'name_en': 'Queen of Cups', 'suit': 'Cups', 'number': 13, 'emoji': '💧',
             'meaning': 'Compassionate, caring, emotionally stable, intuitive',
             'reversed_meaning': 'Inner feelings, self-love, self-care, co-dependency', 'order': 48},
            {'name': 'King of Cups', 'name_en': 'King of Cups', 'suit': 'Cups', 'number': 14, 'emoji': '💧',
             'meaning': 'Emotional balance, compassion, diplomacy',
             'reversed_meaning': 'Emotional manipulation, moodiness, volatility', 'order': 49},
            
            # Minor Arcana - Swords (14 cards)
            {'name': 'Ace of Swords', 'name_en': 'Ace of Swords', 'suit': 'Swords', 'number': 1, 'emoji': '⚔️',
             'meaning': 'Breakthrough, clarity, sharp mind, new idea',
             'reversed_meaning': 'Confusion, clouded judgment, lack of clarity', 'order': 50},
            {'name': 'Two of Swords', 'name_en': 'Two of Swords', 'suit': 'Swords', 'number': 2, 'emoji': '⚔️',
             'meaning': 'Difficult choices, indecision, stalemate, denial',
             'reversed_meaning': 'Indecision, confusion, information overload, stalemate', 'order': 51},
            {'name': 'Three of Swords', 'name_en': 'Three of Swords', 'suit': 'Swords', 'number': 3, 'emoji': '⚔️',
             'meaning': 'Heartbreak, emotional pain, sorrow, grief',
             'reversed_meaning': 'Releasing pain, optimism, forgiveness', 'order': 52},
            {'name': 'Four of Swords', 'name_en': 'Four of Swords', 'suit': 'Swords', 'number': 4, 'emoji': '⚔️',
             'meaning': 'Rest, restoration, contemplation, recuperation',
             'reversed_meaning': 'Restlessness, burnout, lack of progress, stagnation', 'order': 53},
            {'name': 'Five of Swords', 'name_en': 'Five of Swords', 'suit': 'Swords', 'number': 5, 'emoji': '⚔️',
             'meaning': 'Unbridled ambition, win at all costs, sneakiness',
             'reversed_meaning': 'Resentment, desire to reconcile, forgiveness', 'order': 54},
            {'name': 'Six of Swords', 'name_en': 'Six of Swords', 'suit': 'Swords', 'number': 6, 'emoji': '⚔️',
             'meaning': 'Transition, leaving behind, moving on',
             'reversed_meaning': 'Stuck in past, running away, resisting transition', 'order': 55},
            {'name': 'Seven of Swords', 'name_en': 'Seven of Swords', 'suit': 'Swords', 'number': 7, 'emoji': '⚔️',
             'meaning': 'Deception, trickery, tactics and strategy, lies',
             'reversed_meaning': 'Coming clean, rethinking approach, deception', 'order': 56},
            {'name': 'Eight of Swords', 'name_en': 'Eight of Swords', 'suit': 'Swords', 'number': 8, 'emoji': '⚔️',
             'meaning': 'Imprisonment, entrapment, self-victimization',
             'reversed_meaning': 'Self acceptance, new perspective, freedom', 'order': 57},
            {'name': 'Nine of Swords', 'name_en': 'Nine of Swords', 'suit': 'Swords', 'number': 9, 'emoji': '⚔️',
             'meaning': 'Anxiety, worry, fear, depression, nightmares',
             'reversed_meaning': 'Hope, reaching out, despair, nightmares', 'order': 58},
            {'name': 'Ten of Swords', 'name_en': 'Ten of Swords', 'suit': 'Swords', 'number': 10, 'emoji': '⚔️',
             'meaning': 'Back-stabbed, defeat, crisis, betrayal, endings',
             'reversed_meaning': 'Recovery, regeneration, resisting an end, inevitable betrayal', 'order': 59},
            {'name': 'Page of Swords', 'name_en': 'Page of Swords', 'suit': 'Swords', 'number': 11, 'emoji': '⚔️',
             'meaning': 'New ideas, curiosity, thirst for knowledge, new ways of communicating',
             'reversed_meaning': 'Deception, manipulation, all talk, haste', 'order': 60},
            {'name': 'Knight of Swords', 'name_en': 'Knight of Swords', 'suit': 'Swords', 'number': 12, 'emoji': '⚔️',
             'meaning': 'Ambitious, action-oriented, driven to succeed, fast-thinking',
             'reversed_meaning': 'No direction, disregard for consequences, unpredictability', 'order': 61},
            {'name': 'Queen of Swords', 'name_en': 'Queen of Swords', 'suit': 'Swords', 'number': 13, 'emoji': '⚔️',
             'meaning': 'Clear boundaries, direct communication, independence',
             'reversed_meaning': 'Overly-emotional, easily influenced, bitterness, cold-hearted', 'order': 62},
            {'name': 'King of Swords', 'name_en': 'King of Swords', 'suit': 'Swords', 'number': 14, 'emoji': '⚔️',
             'meaning': 'Mental clarity, intellectual power, authority, truth',
             'reversed_meaning': 'Manipulative, cruel, weakness, intellectual power abuse', 'order': 63},
            
            # Minor Arcana - Pentacles (14 cards)
            {'name': 'Ace of Pentacles', 'name_en': 'Ace of Pentacles', 'suit': 'Pentacles', 'number': 1, 'emoji': '💰',
             'meaning': 'New opportunity, prosperity, new venture',
             'reversed_meaning': 'Lost opportunity, missed chance, bad investment', 'order': 64},
            {'name': 'Two of Pentacles', 'name_en': 'Two of Pentacles', 'suit': 'Pentacles', 'number': 2, 'emoji': '💰',
             'meaning': 'Priorities, time management, planning, resource allocation',
             'reversed_meaning': 'Overextended, unorganized, overwhelmed, scattered resources', 'order': 65},
            {'name': 'Three of Pentacles', 'name_en': 'Three of Pentacles', 'suit': 'Pentacles', 'number': 3, 'emoji': '💰',
             'meaning': 'Teamwork, collaboration, learning, implementation',
             'reversed_meaning': 'Lack of teamwork, disorganized, group conflict', 'order': 66},
            {'name': 'Four of Pentacles', 'name_en': 'Four of Pentacles', 'suit': 'Pentacles', 'number': 4, 'emoji': '💰',
             'meaning': 'Control, stability, security, possession, conservatism',
             'reversed_meaning': 'Greed, materialism, self-protection, financial insecurity', 'order': 67},
            {'name': 'Five of Pentacles', 'name_en': 'Five of Pentacles', 'suit': 'Pentacles', 'number': 5, 'emoji': '💰',
             'meaning': 'Need, poverty, insecurity, hardship, isolation',
             'reversed_meaning': 'Recovery, charity, poverty, isolation', 'order': 68},
            {'name': 'Six of Pentacles', 'name_en': 'Six of Pentacles', 'suit': 'Pentacles', 'number': 6, 'emoji': '💰',
             'meaning': 'Giving, receiving, sharing wealth, generosity, charity',
             'reversed_meaning': 'Strings attached, stinginess, power and domination, debt', 'order': 69},
            {'name': 'Seven of Pentacles', 'name_en': 'Seven of Pentacles', 'suit': 'Pentacles', 'number': 7, 'emoji': '💰',
             'meaning': 'Long-term view, sustainable results, perseverance, investment',
             'reversed_meaning': 'Lack of long-term vision, limited success or reward', 'order': 70},
            {'name': 'Eight of Pentacles', 'name_en': 'Eight of Pentacles', 'suit': 'Pentacles', 'number': 8, 'emoji': '💰',
             'meaning': 'Skill development, quality, mastery, commitment',
             'reversed_meaning': 'Lack of quality, no motivation, uninspired, no ambition', 'order': 71},
            {'name': 'Nine of Pentacles', 'name_en': 'Nine of Pentacles', 'suit': 'Pentacles', 'number': 9, 'emoji': '💰',
             'meaning': 'Abundance, luxury, self-sufficiency, financial independence',
             'reversed_meaning': 'Self-worth, over-investment in work, financial setbacks', 'order': 72},
            {'name': 'Ten of Pentacles', 'name_en': 'Ten of Pentacles', 'suit': 'Pentacles', 'number': 10, 'emoji': '💰',
             'meaning': 'Wealth, financial security, family, long-term success, contribution',
             'reversed_meaning': 'Financial failure, lack of stability, family disputes', 'order': 73},
            {'name': 'Page of Pentacles', 'name_en': 'Page of Pentacles', 'suit': 'Pentacles', 'number': 11, 'emoji': '💰',
             'meaning': 'Desire for manifestation, goal-setting, new opportunity',
             'reversed_meaning': 'Lack of commitment, greediness, laziness, short-term thinking', 'order': 74},
            {'name': 'Knight of Pentacles', 'name_en': 'Knight of Pentacles', 'suit': 'Pentacles', 'number': 12, 'emoji': '💰',
             'meaning': 'Efficiency, routine, conservatism, methodical',
             'reversed_meaning': 'Laziness, boredom, feeling "stuck", perfectionism', 'order': 75},
            {'name': 'Queen of Pentacles', 'name_en': 'Queen of Pentacles', 'suit': 'Pentacles', 'number': 13, 'emoji': '💰',
             'meaning': 'Nurturing, practical, providing financially, a working parent',
             'reversed_meaning': 'Self-care, work-home conflict, imbalance', 'order': 76},
            {'name': 'King of Pentacles', 'name_en': 'King of Pentacles', 'suit': 'Pentacles', 'number': 14, 'emoji': '💰',
             'meaning': 'Abundance, prosperity, security, financial provider, leadership',
             'reversed_meaning': 'Authoritative, domineering, controlling, materialistic', 'order': 77},
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for card_data in cards_data:
            # Map suit name to Django choice
            suit_value = suit_mapping.get(card_data['suit'], card_data['suit'].lower())
            
            # Check if card already exists
            card, created = TarotCard.objects.get_or_create(
                suit=suit_value,
                number=card_data['number'],
                name=card_data['name'],
                defaults={
                    'name_en': card_data.get('name_en', card_data['name']),
                    'meaning': card_data['meaning'],
                    'reversed_meaning': card_data['reversed_meaning'],
                    'emoji': card_data['emoji'],
                    'order': card_data['order'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {card.name} ({card.get_suit_display()})')
                )
            else:
                # Update existing card if needed
                updated = False
                if card.meaning != card_data['meaning']:
                    card.meaning = card_data['meaning']
                    updated = True
                if card.reversed_meaning != card_data['reversed_meaning']:
                    card.reversed_meaning = card_data['reversed_meaning']
                    updated = True
                if card.emoji != card_data['emoji']:
                    card.emoji = card_data['emoji']
                    updated = True
                if card.order != card_data['order']:
                    card.order = card_data['order']
                    updated = True
                if card.name_en != card_data.get('name_en', card_data['name']):
                    card.name_en = card_data.get('name_en', card_data['name'])
                    updated = True
                
                if updated:
                    card.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Updated: {card.name} ({card.get_suit_display()})')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.NOTICE(f'○ Skipped: {card.name} ({card.get_suit_display()}) - already exists')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nSummary:\n'
                f'  Created: {created_count} cards\n'
                f'  Updated: {updated_count} cards\n'
                f'  Skipped: {skipped_count} cards\n'
                f'  Total: {created_count + updated_count + skipped_count} cards'
            )
        )

