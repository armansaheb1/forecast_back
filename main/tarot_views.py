import logging
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from decouple import config
from openai import OpenAI
from . import models
from .serializers import TarotCardSerializer
from .language_utils import get_user_language, get_language_prompts, SUPPORTED_LANGUAGES

logger = logging.getLogger('main')

# Initialize OpenAI client
OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    logger.warning("OPENAI_API_KEY not set in environment variables")
    openai_client = None


class TarotCardsView(APIView):
    """
    API endpoint to get all Tarot cards with images.
    Returns list of all cards available in the system.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all Tarot cards with localized names"""
        try:
            # Get language from query parameter or user preference
            language = request.query_params.get('language')
            if not language:
                user = request.user if request.user.is_authenticated else None
                language = get_user_language(user, request)
            
            cards = models.TarotCard.objects.all().order_by('order', 'suit', 'number')
            
            # Get image size parameters from query (for mobile optimization)
            # Default: 140x220 (exact size for card frame)
            image_width = request.query_params.get('image_width')
            image_height = request.query_params.get('image_height')
            
            # Parse size parameters
            parsed_width = None
            parsed_height = None
            if image_width:
                try:
                    parsed_width = int(image_width)
                except (ValueError, TypeError):
                    pass
            if image_height:
                try:
                    parsed_height = int(image_height)
                except (ValueError, TypeError):
                    pass
            
            # Default to exact card size if not specified
            if parsed_width is None:
                parsed_width = 140  # Exact card width
            if parsed_height is None:
                parsed_height = 220  # Exact card height
            
            # Pass language and image size to serializer context
            serializer = TarotCardSerializer(
                cards, 
                many=True, 
                context={
                    'request': request, 
                    'language': language,
                    'image_width': parsed_width,
                    'image_height': parsed_height,
                }
            )
            
            return Response({
                'cards': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching Tarot cards: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch Tarot cards.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TarotReadingView(APIView):
    """
    API endpoint for Tarot card reading with AI interpretation.
    Accepts card IDs and profile information, returns detailed AI-generated reading.
    
    Request body:
    - card_ids: List of card IDs (required)
    - is_reversed: List of booleans indicating if cards are reversed (optional)
    - profile_id: ID of the fortune profile (required)
    - language: Optional language code
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle POST request for Tarot reading"""
        try:
            # Get card IDs from request - handle both JSON string and list
            card_ids_raw = request.data.get('card_ids', [])
            card_ids = []
            
            if isinstance(card_ids_raw, str):
                # If it's a JSON string, parse it
                try:
                    card_ids = json.loads(card_ids_raw)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse card_ids JSON: {e}")
                    raise ValidationError("Field 'card_ids' must be a valid JSON array")
            elif isinstance(card_ids_raw, list):
                card_ids = card_ids_raw
            else:
                raise ValidationError("Field 'card_ids' (list) is required")
            
            if not card_ids:
                raise ValidationError("Field 'card_ids' cannot be empty")
            
            # Get reversed status (optional, defaults to all False)
            is_reversed_raw = request.data.get('is_reversed', [])
            is_reversed = []
            
            if isinstance(is_reversed_raw, str):
                # If it's a JSON string, parse it
                try:
                    is_reversed = json.loads(is_reversed_raw)
                except (json.JSONDecodeError, ValueError):
                    is_reversed = [False] * len(card_ids)
            elif isinstance(is_reversed_raw, list):
                is_reversed = is_reversed_raw
            else:
                is_reversed = [False] * len(card_ids)
            
            # Ensure is_reversed has same length as card_ids
            if len(is_reversed) != len(card_ids):
                is_reversed = [False] * len(card_ids)
            
            # Get profile data from request (full profile data, not just profile_id)
            profile_data_raw = request.data.get('profile')
            if not profile_data_raw:
                # Fallback: try to get profile_id for backward compatibility
                profile_id = request.data.get('profile_id')
                if profile_id:
                    try:
                        profile = models.FortuneProfile.objects.get(pk=profile_id)
                        profile_data = {
                            'name': profile.name,
                            'age': profile.age or profile.calculated_age,
                            'gender': profile.gender,
                            'job_status': profile.job_status,
                            'relationship_status': profile.relationship_status,
                            'city': profile.city,
                            'country': profile.country,
                            'notes': profile.notes,
                        }
                    except models.FortuneProfile.DoesNotExist:
                        raise ValidationError(f"Profile {profile_id} not found. Please provide full profile data in 'profile' field.")
                else:
                    raise ValidationError("Field 'profile' is required with full profile data (name, age, relationship_status, etc.)")
            else:
                # Use profile data from request
                profile_data = {
                    'name': profile_data_raw.get('name', ''),
                    'age': profile_data_raw.get('age'),
                    'gender': profile_data_raw.get('gender'),
                    'job_status': profile_data_raw.get('job_status'),
                    'relationship_status': profile_data_raw.get('relationship_status'),
                    'city': profile_data_raw.get('city'),
                    'country': profile_data_raw.get('country'),
                    'notes': profile_data_raw.get('notes'),
                }
                # Validate required fields
                if not profile_data['name']:
                    raise ValidationError("Profile 'name' is required")
            
            # Get language
            request_language = request.data.get('language')
            if request_language and request_language in SUPPORTED_LANGUAGES:
                user_language = request_language
            else:
                user = request.user if request.user.is_authenticated else None
                user_language = get_user_language(user, request)
            
            # Get cards from database
            cards = models.TarotCard.objects.filter(id__in=card_ids)
            if cards.count() != len(card_ids):
                raise ValidationError("Some card IDs are invalid")
            
            cards_list = list(cards)
            card_data = []
            for i, card in enumerate(cards_list):
                card_data.append({
                    'id': card.id,
                    'name': card.name,
                    'suit': card.get_suit_display(),
                    'meaning': card.meaning or '',
                    'reversed_meaning': card.reversed_meaning or '',
                    'is_reversed': is_reversed[i] if i < len(is_reversed) else False,
                })
            
            # Validate OpenAI API Key
            if not OPENAI_API_KEY or not openai_client:
                logger.error("OpenAI API Key is not configured")
                return Response(
                    {'error': 'OpenAI API Key is not configured.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            prompts = get_language_prompts(user_language)
            
            # Build profile information (use None values as empty strings)
            profile_info = f"""
Name: {profile_data.get('name', '')}
Age: {profile_data.get('age', '') if profile_data.get('age') is not None else ''}
Gender: {profile_data.get('gender', '') if profile_data.get('gender') else ''}
Job Status: {profile_data.get('job_status', '') if profile_data.get('job_status') else ''}
Relationship Status: {profile_data.get('relationship_status', '') if profile_data.get('relationship_status') else ''}
"""
            if profile_data.get('city'):
                profile_info += f"City: {profile_data['city']}\n"
            if profile_data.get('country'):
                profile_info += f"Country: {profile_data['country']}\n"
            if profile_data.get('notes'):
                profile_info += f"Notes: {profile_data['notes']}\n"
            
            # Build cards information for prompt
            cards_info = "\n".join([
                f"Card {i+1}: {card['name']} ({card['suit']}) - "
                f"Position: {'Reversed' if card['is_reversed'] else 'Upright'} - "
                f"Base Meaning: {card['reversed_meaning'] if card['is_reversed'] else card['meaning']}"
                for i, card in enumerate(card_data)
            ])
            
            # Generate complete reading in one request with JSON response
            try:
                complete_prompt = f"""You are a professional Tarot card reader. Based on the following information, provide a complete Tarot reading with individual card interpretations and an overall reading.

Profile Information:
{profile_info}

Cards Drawn:
{cards_info}

Please provide a complete Tarot reading in JSON format with the following structure:
{{
  "individual_interpretations": [
    {{
      "card_id": {card_data[0]['id']},
      "card_name": "{card_data[0]['name']}",
      "is_reversed": {str(card_data[0]['is_reversed']).lower()},
      "interpretation": "Detailed personalized interpretation for this card considering the querent's profile, card position, and life situation. Write in {user_language} language. Be warm, empathetic, and provide actionable insights."
    }},
    ... (one object for each card)
  ],
  "overall_reading": "A comprehensive overall reading that synthesizes all cards together, considers the querent's profile, provides guidance on how cards relate to each other, offers actionable insights, and addresses the overall message. Write in {user_language} language. Be warm, empathetic, and provide a complete narrative."
}}

Requirements:
1. For each card, provide a detailed, personalized interpretation considering:
   - The querent's profile (age, gender, job status, relationship status)
   - The card's position (upright or reversed)
   - How this card relates to their current life situation
   - Specific guidance and insights

2. For the overall reading:
   - Synthesize all cards together to tell a cohesive story
   - Consider the querent's profile and life situation
   - Provide guidance on how the cards relate to each other
   - Offer actionable insights and advice
   - Address the overall message the cards are conveying

3. Write everything in {user_language} language
4. Be warm, empathetic, and provide actionable insights
5. Return ONLY valid JSON, no additional text before or after

Return the JSON response now:"""
                
                completion = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": prompts.get('system', 'You are a professional Tarot card reader. You always respond with valid JSON format.'),
                        },
                        {
                            "role": "user",
                            "content": complete_prompt,
                        },
                    ],
                    response_format={"type": "json_object"},
                )
                
                response_content = completion.choices[0].message.content or "{}"
                
                # Parse JSON response
                try:
                    reading_data = json.loads(response_content)
                    
                    # Extract individual interpretations
                    individual_interpretations = []
                    if 'individual_interpretations' in reading_data:
                        for i, interpretation_data in enumerate(reading_data['individual_interpretations']):
                            if i < len(card_data):
                                individual_interpretations.append({
                                    'card_id': card_data[i]['id'],
                                    'card_name': card_data[i]['name'],
                                    'is_reversed': card_data[i]['is_reversed'],
                                    'interpretation': interpretation_data.get('interpretation', 
                                        card_data[i]['reversed_meaning'] if card_data[i]['is_reversed'] else card_data[i]['meaning']),
                                })
                            else:
                                # Fallback if GPT returned more interpretations than cards
                                individual_interpretations.append({
                                    'card_id': interpretation_data.get('card_id', 0),
                                    'card_name': interpretation_data.get('card_name', 'Unknown'),
                                    'is_reversed': interpretation_data.get('is_reversed', False),
                                    'interpretation': interpretation_data.get('interpretation', ''),
                                })
                    else:
                        # Fallback: create interpretations from card data
                        for card in card_data:
                            individual_interpretations.append({
                                'card_id': card['id'],
                                'card_name': card['name'],
                                'is_reversed': card['is_reversed'],
                                'interpretation': card['reversed_meaning'] if card['is_reversed'] else card['meaning'],
                            })
                    
                    # Extract overall reading
                    overall_reading = reading_data.get('overall_reading', 'Unable to generate overall reading at this time.')
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response from GPT: {str(e)}")
                    logger.error(f"Response content: {response_content[:500]}")
                    # Fallback: use card meanings
                    individual_interpretations = []
                    for card in card_data:
                        individual_interpretations.append({
                            'card_id': card['id'],
                            'card_name': card['name'],
                            'is_reversed': card['is_reversed'],
                            'interpretation': card['reversed_meaning'] if card['is_reversed'] else card['meaning'],
                        })
                    overall_reading = "Unable to generate overall reading at this time."
                    
            except Exception as e:
                logger.error(f"Error generating complete reading: {str(e)}", exc_info=True)
                # Fallback: use card meanings
                individual_interpretations = []
                for card in card_data:
                    individual_interpretations.append({
                        'card_id': card['id'],
                        'card_name': card['name'],
                        'is_reversed': card['is_reversed'],
                        'interpretation': card['reversed_meaning'] if card['is_reversed'] else card['meaning'],
                    })
                overall_reading = "Unable to generate overall reading at this time."
            
            # Get image size parameters from request data or query
            image_width = request.data.get('image_width') or request.query_params.get('image_width')
            image_height = request.data.get('image_height') or request.query_params.get('image_height')
            
            # Parse size parameters
            parsed_width = None
            parsed_height = None
            if image_width:
                try:
                    parsed_width = int(image_width)
                except (ValueError, TypeError):
                    pass
            if image_height:
                try:
                    parsed_height = int(image_height)
                except (ValueError, TypeError):
                    pass
            
            # Default to exact card size if not specified
            if parsed_width is None:
                parsed_width = 140  # Exact card width
            if parsed_height is None:
                parsed_height = 220  # Exact card height
            
            # Serialize cards with images (pass language and image size to serializer)
            card_serializer = TarotCardSerializer(
                cards, 
                many=True, 
                context={
                    'request': request, 
                    'language': user_language,
                    'image_width': parsed_width,
                    'image_height': parsed_height,
                }
            )
            
            return Response({
                'cards': card_serializer.data,
                'individual_interpretations': individual_interpretations,
                'overall_reading': overall_reading,
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

