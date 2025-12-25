import logging
import json
import re
from decouple import config
from openai import OpenAI
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from .language_utils import get_user_language, get_language_prompts, get_continuation_question_prompt, SUPPORTED_LANGUAGES

logger = logging.getLogger('main')

# Initialize OpenAI client
OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    logger.warning("OPENAI_API_KEY not set in environment variables")
    openai_client = None


class DreamInterpretationView(APIView):
    """
    API endpoint for Dream Interpretation.
    Accepts dream text and profile information, returns dream interpretation using OpenAI GPT-4o.
    
    Authentication: Optional (Users can use without login)
    
    Request body:
    - profile: Full profile data (required)
    - dream_text: Text description of the dream (required)
    - language: Optional language code (overrides user preference)
    """
    permission_classes = [AllowAny]  # Login is optional
    
    def post(self, request):
        """
        Handle POST request for Dream Interpretation
        
        Request body:
        - profile: Full profile data (required)
        - dream_text: Text description of the dream (required)
        - language: Optional language code
        """
        try:
            # Get profile data from request
            profile_data_raw = request.data.get('profile')
            if not profile_data_raw:
                raise ValidationError("Field 'profile' is required with full profile data (name, age, relationship_status, etc.)")
            
            # Parse JSON string if it's a string, otherwise use as dict
            if isinstance(profile_data_raw, str):
                try:
                    profile_data_raw = json.loads(profile_data_raw)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse profile JSON: {profile_data_raw}")
                    raise ValidationError(f"Invalid profile JSON format: {str(e)}")
            
            if not isinstance(profile_data_raw, dict):
                raise ValidationError("Invalid profile data format. Expected JSON string or dictionary.")
            
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
            
            # Get dream text
            dream_text = request.data.get('dream_text', '').strip()
            if not dream_text:
                raise ValidationError("Field 'dream_text' is required and cannot be empty")
            
            # Get language from request if provided
            request_language = request.data.get('language')
            if request_language and request_language in SUPPORTED_LANGUAGES:
                user_language = request_language
            else:
                user = request.user if request.user.is_authenticated else None
                user_language = get_user_language(user, request)
            
            prompts = get_language_prompts(user_language)
            
            # Validate OpenAI API Key
            if not OPENAI_API_KEY or not openai_client:
                logger.error("OpenAI API Key is not configured")
                return Response(
                    {
                        'error': 'OpenAI API Key is not configured. Please set OPENAI_API_KEY in environment variables.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Build prompt with profile information
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
            
            # Call OpenAI API
            try:
                system_prompt = prompts.get('system', 'You are a professional dream interpreter.')
                if 'system' not in prompts:
                    # Add dream interpretation specific system prompt if not in language prompts
                    system_prompt = f"You are a professional dream interpreter. You provide detailed, personalized interpretations of dreams based on symbolism, psychology, and cultural context. Be warm, empathetic, and provide actionable insights. Write in {user_language} language."
                
                user_prompt = f"""{profile_info}

Dream Description:
{dream_text}

Please provide a detailed dream interpretation for this person based on their profile information and the dream they described. Explain the symbolism, what the dream might mean in their current life situation, and provide guidance. Write in {user_language} language. Be warm, empathetic, and provide actionable insights."""
                
                completion = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                )
                
                result = completion.choices[0].message.content or ""
                
                # Generate continuation questions
                continuation_questions = []
                default_questions = {
                    'fa': [
                        'ببین عزیزم، می‌خوای بیشتر درباره نمادهای این خواب بدونی؟',
                        'بگو ببینم، می‌خوای بدونی این خواب درباره آینده‌ت چی می‌گه؟',
                        'داری می‌خوای بدونی باید روی چه چیزی تمرکز کنی؟'
                    ],
                    'en': [
                        'Hey sweetie, wanna know more about the symbols in your dream?',
                        'Tell me, you wanna know what this dream says about your future?',
                        'You wanna know what you should focus on?'
                    ]
                }
                
                try:
                    question_prompts = get_continuation_question_prompt(user_language)
                    question_completion = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": question_prompts['system'],
                            },
                            {
                                "role": "user",
                                "content": f"{question_prompts['user']}\n\nDream Interpretation:\n{result}",
                            },
                        ],
                    )
                    
                    questions_text = question_completion.choices[0].message.content or ""
                    logger.info(f"Raw questions text: {questions_text}")
                    
                    # Parse questions (one per line, remove numbers, bullets, etc.)
                    raw_questions = [
                        q.strip() 
                        for q in questions_text.split('\n') 
                        if q.strip()
                    ]
                    
                    # Clean questions: remove numbers, bullets, dashes at start
                    for q in raw_questions:
                        # Remove leading numbers, bullets, dashes, etc.
                        cleaned = re.sub(r'^[\d\.\-\*\•\-\s]+', '', q).strip()
                        # Remove markdown formatting
                        cleaned = re.sub(r'^[#\*\-]+\s*', '', cleaned).strip()
                        if cleaned and len(cleaned) > 10:  # Minimum length check
                            continuation_questions.append(cleaned)
                    
                    # If we don't have 3 questions, try to split by question marks
                    if len(continuation_questions) < 3:
                        full_text = questions_text.replace('\n', ' ')
                        # Split by question marks
                        parts = re.split(r'[؟?]', full_text)
                        continuation_questions = [
                            p.strip() + ('؟' if user_language == 'fa' or user_language == 'ar' else '?')
                            for p in parts 
                            if p.strip() and len(p.strip()) > 10
                        ][:3]
                    
                    # Ensure we have exactly 3 questions (pad with defaults if needed)
                    defaults = default_questions.get(user_language, default_questions['en'])
                    while len(continuation_questions) < 3:
                        continuation_questions.append(defaults[len(continuation_questions)])
                    
                    continuation_questions = continuation_questions[:3]  # Take only first 3
                    
                except Exception as e:
                    logger.warning(f"Failed to generate continuation questions: {str(e)}")
                    # Use default questions
                    defaults = default_questions.get(user_language, default_questions['en'])
                    continuation_questions = defaults
                
                return Response(
                    {
                        'result': result,
                        'next': continuation_questions,
                    },
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
                return Response(
                    {'error': f'Failed to generate dream interpretation: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
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

