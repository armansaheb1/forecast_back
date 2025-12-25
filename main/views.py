import logging
import os
import json
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from decouple import config
from openai import OpenAI
from . import models
from .serializers import FileSerializer, CoffeeReadingResponseSerializer, TarotCardSerializer
from .language_utils import get_user_language, get_language_prompts, get_continuation_question_prompt, SUPPORTED_LANGUAGES

logger = logging.getLogger('main')

# Initialize OpenAI client
OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    logger.warning("OPENAI_API_KEY not set in environment variables")
    openai_client = None


class GBuilderFile(APIView):
    """
    API endpoint for coffee cup reading.
    Accepts an image file and returns fortune reading using OpenAI GPT-4o.
    
    Authentication: Optional (Users can use without login, but login allows syncing data across devices)
    
    Language support:
    - Automatically uses user's preferred language
    - Can override with 'language' parameter in request body
    - Defaults to English (en) if no language preference is set
    
    Supported languages: 40+ languages including English, Persian, Arabic, 
    Turkish, Spanish, French, German, Italian, Chinese, Japanese, Korean, 
    Hindi, Bengali, and many more. See LANGUAGE_CHOICES in models for full list.
    """
    permission_classes = [AllowAny]  # Login is optional - users can use app without account

    def post(self, request):
        """
        Handle POST request for coffee reading
        
        Authentication: Optional (If authenticated, data is saved to user account for cross-device sync)
        
        Request body:
        - images: Image file (required)
        - language: Optional language code (overrides user preference)
        """
        try:
            # User may or may not be authenticated (login is optional)
            # If authenticated, data will be saved to their account for cross-device sync
            user = request.user if request.user.is_authenticated else None
            
            # Get language from request if provided (overrides user preference)
            request_language = request.data.get('language')
            if request_language and request_language in SUPPORTED_LANGUAGES:
                user_language = request_language
            else:
                user_language = None
            
            # Validate OpenAI API Key
            if not OPENAI_API_KEY or not openai_client:
                logger.error("OpenAI API Key is not configured")
                return Response(
                    {
                        'error': 'OpenAI API Key is not configured. Please set OPENAI_API_KEY in environment variables.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Validate input
            if 'images' not in request.data:
                logger.warning("Missing 'images' field in request")
                raise ValidationError("Field 'images' is required")

            image_files = request.data['images']
            
            # Normalize to list: if single file, convert to list
            if not isinstance(image_files, list):
                image_files = [image_files]
            
            # Validate file exists
            if not image_files or len(image_files) == 0:
                logger.warning("Empty image file in request")
                raise ValidationError("At least one image file is required")


            # Validate and create file records using serializer
            # This ensures file size (max 10MB) and file type validation is executed
            file_objs = []
            try:
                for idx, image_file in enumerate(image_files):
                    serializer = FileSerializer(
                        data={'image': image_file},
                        context={'request': request}
                    )
                    # Validate the data (this will call validate_image method)
                    serializer.is_valid(raise_exception=True)
                    # Save the file with user (None if not authenticated)
                    # If user is None, file is saved but not linked to any account
                    file_obj = serializer.save(user=user)
                    file_objs.append(file_obj)
                    logger.info(f"File {idx+1} created successfully: {file_obj.id} by user {user}")
            except ValidationError as e:
                # Clean up any files that were already saved
                for file_obj in file_objs:
                    try:
                        file_obj.delete()
                    except Exception:
                        pass
                # Re-raise ValidationError to be caught by outer exception handler
                logger.warning(f"File validation error: {str(e)}")
                raise
            except Exception as e:
                # Clean up any files that were already saved
                for file_obj in file_objs:
                    try:
                        file_obj.delete()
                    except Exception:
                        pass
                logger.error(f"Error creating file: {str(e)}")
                return Response(
                    {'error': f'Error saving file: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Build image URLs for all files
            request_obj = request._request if hasattr(request, '_request') else request
            image_urls = []
            for file_obj in file_objs:
                if hasattr(request_obj, 'build_absolute_uri'):
                    image_url = request_obj.build_absolute_uri(file_obj.image.url)
                else:
                    # Fallback to settings
                    media_root_url = getattr(settings, 'MEDIA_ROOT_URL', 'http://localhost:8000')
                    image_url = f"{media_root_url}{settings.MEDIA_URL}{file_obj.image.name}"
                image_urls.append(image_url)

            logger.info(f"Processing {len(image_urls)} image(s): {image_urls}")

            # Get user's preferred language
            # User may or may not be authenticated (login is optional)
            if user_language:
                language = user_language
            else:
                language = get_user_language(user, request)
            prompts = get_language_prompts(language)
            
            logger.info(f"Using language: {language} for user: {user}")

            # Initialize profile_data to None
            profile_data = None
            
            # Get profile data from request (full profile data, not just profile_id)
            profile_data_raw = request.data.get('profile')
            profile_info = ""
            if profile_data_raw:
                # Parse JSON string if it's a string, otherwise use as dict
                if isinstance(profile_data_raw, str):
                    try:
                        profile_data_raw = json.loads(profile_data_raw)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse profile JSON: {profile_data_raw}")
                        raise ValidationError(f"Invalid profile JSON format: {str(e)}")
                
                if profile_data_raw and isinstance(profile_data_raw, dict):
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
                    # Build profile information string
                    if profile_data.get('name'):
                        profile_info = f"""
Profile Information:
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
                else:
                    raise ValidationError("Invalid profile data format. Expected JSON string or dictionary.")

            # Call OpenAI API with all images
            try:
                # Build content array with all images
                image_content = [
                    {
                        "type": "image_url",
                        "image_url": {"url": url},
                    }
                    for url in image_urls
                ]
                
                # Build user message with profile info if available
                user_message_content = image_content.copy()
                if profile_info:
                    user_message_content.append({
                        "type": "text",
                        "text": f"{profile_info}\n{prompts['user']}"
                    })
                else:
                    user_message_content.append({
                        "type": "text",
                        "text": prompts['user']
                    })
                
                completion = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": prompts['system'],
                        },
                        {
                            "role": "user",
                            "content": user_message_content,
                        },
                    ],
                )

                response_data = completion.choices[0].message
                reading_content = response_data.content if response_data.content else ""
                logger.info(f"OpenAI API call successful for {len(file_objs)} file(s)")

                # Generate continuation questions
                import re
                continuation_questions = []
                default_questions = {
                    'fa': [
                        'ببین عزیزم، می‌خوای رازهای عشق رو که تو کاپت دیدم برات بگم؟',
                        'بگو ببینم، می‌خوای بدونی وضعیت مالی‌ت چی می‌گه؟',
                        'داری می‌خوای بدونی آینده شغلی‌ت چطوری میشه؟'
                    ],
                    'en': [
                        'Hey sweetie, wanna know the love secrets I saw in your cup?',
                        'Tell me, you wanna know what your finances are saying?',
                        'You wanna know how your career future is gonna be?'
                    ]
                }
                
                try:
                    question_prompts = get_continuation_question_prompt(language)
                    question_completion = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": question_prompts['system'],
                            },
                            {
                                "role": "user",
                                "content": f"{question_prompts['user']}\n\nCoffee Reading:\n{reading_content}",
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
                            p.strip() + ('؟' if language == 'fa' or language == 'ar' else '?')
                            for p in parts 
                            if p.strip() and len(p.strip()) > 10
                        ][:3]
                    
                    # Ensure we have exactly 3 questions (pad with defaults if needed)
                    defaults = default_questions.get(language, default_questions['en'])
                    while len(continuation_questions) < 3:
                        continuation_questions.append(defaults[len(continuation_questions)])
                    
                    continuation_questions = continuation_questions[:3]  # Take only first 3
                    
                    logger.info(f"Generated {len(continuation_questions)} continuation questions: {continuation_questions}")
                except Exception as e:
                    logger.warning(f"Failed to generate continuation questions: {str(e)}")
                    # Use default questions if generation fails
                    continuation_questions = default_questions.get(language, default_questions['en'])

                # Return JSON response with content and questions
                return Response({
                    'content': reading_content,
                    'questions': continuation_questions,
                }, status=status.HTTP_200_OK)

            except Exception as e:
                # Check if it's an OpenAI API error
                error_type = type(e).__name__
                if 'APIError' in error_type or 'OpenAI' in error_type:
                    logger.error(f"OpenAI API error: {str(e)}")
                    # Clean up files if API call fails
                    for file_obj in file_objs:
                        try:
                            file_obj.delete()
                        except Exception:
                            pass
                    return Response(
                        {'error': f'OpenAI API error: {str(e)}'},
                        status=status.HTTP_502_BAD_GATEWAY
                    )
                else:
                    logger.error(f"Unexpected error in OpenAI API call: {str(e)}")
                    # Clean up files if API call fails
                    for file_obj in file_objs:
                        try:
                            file_obj.delete()
                        except Exception:
                            pass
                    return Response(
                        {'error': f'Error processing image: {str(e)}'},
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


class HoroscopeView(APIView):
    """
    API endpoint for horoscope reading.
    Accepts a profile_id and returns horoscope reading using OpenAI GPT-4o.
    
    Authentication: Optional (Users can use without login)
    
    Request body:
    - profile_id: ID of the fortune profile (required)
    - language: Optional language code (overrides user preference)
    """
    permission_classes = [AllowAny]  # Login is optional
    
    def post(self, request):
        """
        Handle POST request for horoscope reading
        
        Request body:
        - profile_id: ID of the fortune profile (required)
        - language: Optional language code
        """
        try:
            # Initialize profile_data and profile_id to None
            profile_data = None
            profile_id = None
            
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
                # Parse JSON string if it's a string, otherwise use as dict
                if isinstance(profile_data_raw, str):
                    try:
                        profile_data_raw = json.loads(profile_data_raw)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse profile JSON: {profile_data_raw}")
                        raise ValidationError(f"Invalid profile JSON format: {str(e)}")
                
                if profile_data_raw and isinstance(profile_data_raw, dict):
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
                else:
                    raise ValidationError("Invalid profile data format. Expected JSON string or dictionary.")
            
            # Get language from request if provided
            request_language = request.data.get('language')
            if request_language and request_language in SUPPORTED_LANGUAGES:
                user_language = request_language
            else:
                user = request.user if request.user.is_authenticated else None
                user_language = get_user_language(user, request)
            
            prompts = get_language_prompts(user_language)
            
            # Ensure profile_data is defined before using it
            if profile_data is None:
                raise ValidationError("Profile data is required but was not provided or could not be parsed.")
            
            # Validate OpenAI API Key
            if not OPENAI_API_KEY or not openai_client:
                logger.error("OpenAI API Key is not configured")
                return Response(
                    {
                        'error': 'OpenAI API Key is not configured. Please set OPENAI_API_KEY in environment variables.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Build prompt with profile information (use None values as empty strings)
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
                completion = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": prompts['system'] if 'system' in prompts else "You are a professional fortune teller and astrologer.",
                        },
                        {
                            "role": "user",
                            "content": f"{profile_info}\n\nPlease provide a detailed horoscope reading for this person based on their profile information.",
                        },
                    ],
                )
                
                result = completion.choices[0].message.content or ""
                
                # Generate continuation questions
                import re
                continuation_questions = []
                default_questions = {
                    'fa': [
                        'ببین عزیزم، می‌خوای رازهای عشق رو که تو فال دیدم برات بگم؟',
                        'بگو ببینم، می‌خوای بدونی ستاره‌هات درباره پول چی می‌گن؟',
                        'داری می‌خوای بدونی آینده شغلی‌ت چطوری میشه؟'
                    ],
                    'en': [
                        'Hey sweetie, wanna know the love secrets I saw in your horoscope?',
                        'Tell me, you wanna know what your stars are saying about money?',
                        'You wanna know how your career future is gonna be?'
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
                                "content": f"{question_prompts['user']}\n\nHoroscope Reading:\n{result}",
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
                    
                    logger.info(f"Generated {len(continuation_questions)} continuation questions: {continuation_questions}")
                except Exception as e:
                    logger.warning(f"Failed to generate continuation questions: {str(e)}")
                    # Use default questions if generation fails
                    continuation_questions = default_questions.get(user_language, default_questions['en'])
                
                logger.info(f"Horoscope reading generated successfully for profile {profile_id if profile_id else profile_data.get('name', 'Unknown')}")
                
                return Response({
                    'result': result,
                    'next': continuation_questions,  # Use continuation questions instead of empty list
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                error_type = type(e).__name__
                if 'APIError' in error_type or 'OpenAI' in error_type:
                    logger.error(f"OpenAI API error: {str(e)}")
                    return Response(
                        {'error': f'OpenAI API error: {str(e)}'},
                        status=status.HTTP_502_BAD_GATEWAY
                    )
                else:
                    logger.error(f"Unexpected error in OpenAI API call: {str(e)}")
                    return Response(
                        {'error': f'Error processing horoscope: {str(e)}'},
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


class IChingView(APIView):
    """
    API endpoint for I Ching reading.
    Accepts hexagram lines and profile information, returns I Ching reading using OpenAI GPT-4o.
    
    Authentication: Optional (Users can use without login)
    
    Request body:
    - profile: Full profile data (required)
    - hexagram_lines: List of 6 integers (0-3), each representing sum of 3 coins (required)
    - language: Optional language code (overrides user preference)
    """
    permission_classes = [AllowAny]  # Login is optional
    
    def post(self, request):
        """
        Handle POST request for I Ching reading
        
        Request body:
        - profile: Full profile data (required)
        - hexagram_lines: List of 6 integers (0-3) (required)
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
            
            # Get hexagram lines
            hexagram_lines_raw = request.data.get('hexagram_lines')
            if not hexagram_lines_raw:
                raise ValidationError("Field 'hexagram_lines' is required (list of 6 integers, each 0-3)")
            
            # Parse JSON string if it's a string
            if isinstance(hexagram_lines_raw, str):
                try:
                    hexagram_lines_raw = json.loads(hexagram_lines_raw)
                except json.JSONDecodeError as e:
                    raise ValidationError(f"Invalid hexagram_lines JSON format: {str(e)}")
            
            if not isinstance(hexagram_lines_raw, list) or len(hexagram_lines_raw) != 6:
                raise ValidationError("hexagram_lines must be a list of exactly 6 integers (each 0-3)")
            
            hexagram_lines = [int(x) for x in hexagram_lines_raw]
            if not all(0 <= x <= 3 for x in hexagram_lines):
                raise ValidationError("Each hexagram line must be between 0 and 3 (sum of 3 coins)")
            
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
            
            # Convert hexagram lines to readable format
            # 0-1 = yin (broken line), 2-3 = yang (solid line)
            hexagram_description = []
            for i, line_sum in enumerate(hexagram_lines):
                line_type = "yin (broken)" if line_sum <= 1 else "yang (solid)"
                hexagram_description.append(f"Line {i+1}: {line_type} (sum: {line_sum})")
            
            hexagram_text = "\n".join(hexagram_description)
            
            # Call OpenAI API
            try:
                system_prompt = prompts.get('system', 'You are a professional I Ching fortune teller.')
                if 'system' not in prompts:
                    # Add I Ching specific system prompt if not in language prompts
                    system_prompt = f"You are a professional I Ching (Book of Changes) fortune teller. You provide detailed, personalized readings based on hexagrams. Be warm, empathetic, and provide actionable insights. Write in {user_language} language."
                
                user_prompt = f"""{profile_info}

Hexagram Lines (from bottom to top):
{hexagram_text}

Please provide a detailed I Ching reading for this person based on their profile information and the hexagram that was cast. Explain what the hexagram means, how it relates to their current situation, and provide guidance for their future. Write in {user_language} language. Be warm, empathetic, and provide actionable insights."""
                
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
                import re
                continuation_questions = []
                default_questions = {
                    'fa': [
                        'ببین عزیزم، می‌خوای بیشتر درباره معنای این هگزاگرام بدونی؟',
                        'بگو ببینم، می‌خوای بدونی این فال درباره آینده‌ت چی می‌گه؟',
                        'داری می‌خوای بدونی باید روی چه چیزی تمرکز کنی؟'
                    ],
                    'en': [
                        'Hey sweetie, wanna know more about what this hexagram means?',
                        'Tell me, you wanna know what this reading says about your future?',
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
                                "content": f"{question_prompts['user']}\n\nI Ching Reading:\n{result}",
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
                    {'error': f'Failed to generate I Ching reading: {str(e)}'},
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
                import re
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
