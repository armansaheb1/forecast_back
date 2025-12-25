import json
import os
import time
import logging
from urllib.parse import urlencode
from django.urls import reverse
from rest_framework import serializers
from .models import File, FortuneProfile, TarotCard

logger = logging.getLogger('main')

# #region agent log
def _debug_log(location, message, data=None, hypothesis_id=None):
    try:
        log_entry = {
            'id': f'log_{int(time.time() * 1000)}_{hash(location)}',
            'timestamp': int(time.time() * 1000),
            'location': location,
            'message': message,
            'data': data or {},
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': hypothesis_id or 'A'
        }
        os.makedirs('/forecast_back/.cursor', exist_ok=True)
        with open('/forecast_back/.cursor/debug.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
# #endregion


class FileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)

    class Meta:
        model = File
        fields = ['id', 'image', 'image_url', 'user', 'user_username', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_image(self, value):
        # #region agent log
        _debug_log('serializers.py:22', 'validate_image entry', {
            'value_type': str(type(value)),
            'is_list': isinstance(value, list),
            'has_size': hasattr(value, 'size') if not isinstance(value, list) else False,
            'has_content_type': hasattr(value, 'content_type') if not isinstance(value, list) else False
        }, 'H')
        # #endregion
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        
        # #region agent log
        _debug_log('serializers.py:25', 'Before accessing value.size', {
            'value_type': str(type(value)),
            'has_size_attr': hasattr(value, 'size')
        }, 'I')
        # #endregion
        
        try:
            file_size = value.size
            # #region agent log
            _debug_log('serializers.py:25', 'Successfully got value.size', {'size': file_size}, 'I')
            # #endregion
        except Exception as e:
            # #region agent log
            _debug_log('serializers.py:25', 'Error accessing value.size', {
                'error_type': str(type(e).__name__),
                'error_message': str(e),
                'value_type': str(type(value))
            }, 'I')
            # #endregion
            raise serializers.ValidationError(f"Cannot retrieve file size: {str(e)}")
        
        if file_size > max_size:
            raise serializers.ValidationError(
                f"File size cannot exceed {max_size / (1024*1024)}MB"
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        # #region agent log
        _debug_log('serializers.py:32', 'Before accessing value.content_type', {
            'has_content_type_attr': hasattr(value, 'content_type')
        }, 'J')
        # #endregion
        
        try:
            content_type = value.content_type
            # #region agent log
            _debug_log('serializers.py:32', 'Successfully got value.content_type', {'content_type': content_type}, 'J')
            # #endregion
        except Exception as e:
            # #region agent log
            _debug_log('serializers.py:32', 'Error accessing value.content_type', {
                'error_type': str(type(e).__name__),
                'error_message': str(e)
            }, 'J')
            # #endregion
            raise serializers.ValidationError(f"Cannot retrieve file content type: {str(e)}")
        
        if content_type not in allowed_types:
            raise serializers.ValidationError(
                f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        return value


class CoffeeReadingResponseSerializer(serializers.Serializer):
    content = serializers.CharField()
    role = serializers.CharField()


class FortuneProfileSerializer(serializers.ModelSerializer):
    """Serializer for FortuneProfile model"""
    
    class Meta:
        model = FortuneProfile
        fields = [
            'id',
            'name',
            'birth_date',
            'age',
            'gender',
            'job_status',
            'relationship_status',
            'city',
            'country',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate profile data"""
        # Auto-calculate age if birth_date is provided
        if 'birth_date' in data and data['birth_date']:
            from datetime import date
            today = date.today()
            age = today.year - data['birth_date'].year - (
                (today.month, today.day) < (data['birth_date'].month, data['birth_date'].day)
            )
            if 'age' not in data or not data['age']:
                data['age'] = age
        return data
    
    def create(self, validated_data):
        """Create profile and assign to user if authenticated"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class TarotCardSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()  # Override to return localized name
    
    class Meta:
        model = TarotCard
        fields = ['id', 'name', 'name_en', 'suit', 'number', 'image', 'image_url', 
                  'meaning', 'reversed_meaning', 'emoji', 'order', 'names_translations']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_name(self, obj):
        """Get localized name based on request language"""
        # Get language from context (passed from view) or request
        language_code = self.context.get('language')
        
        # If not in context, try to get from request
        if not language_code:
            request = self.context.get('request')
            if request:
                # Try to get language from query parameter first
                # Handle both DRF Request and Django WSGIRequest
                if hasattr(request, 'query_params'):
                    language_code = request.query_params.get('language')
                elif hasattr(request, 'GET'):
                    language_code = request.GET.get('language')
                
                # If not in query, try Accept-Language header
                if not language_code:
                    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
                    if accept_language:
                        # Parse Accept-Language header (e.g., "en-US,en;q=0.9,fa;q=0.8")
                        languages = [lang.split(';')[0].strip()[:2] for lang in accept_language.split(',')]
                        for lang in languages:
                            if lang in ['en', 'fa', 'ar', 'es', 'fr', 'de', 'it', 'ru', 'hi', 'zh']:
                                language_code = lang
                                break
                # If still not found, try user preference
                if not language_code and hasattr(request, 'user') and request.user.is_authenticated:
                    language_code = getattr(request.user, 'language', None)
        
        # Default to English if still not found
        if not language_code:
            language_code = 'en'
        
        return obj.get_name(language_code)
    
    def get_image_url(self, obj):
        # #region agent log
        _debug_log('serializers.py:208', 'get_image_url entry', {
            'card_id': obj.id,
            'card_name': obj.name,
            'has_image_field': obj.image is not None,
            'image_field_value': str(obj.image) if obj.image else None,
            'has_url_attr': hasattr(obj.image, 'url') if obj.image else False
        }, 'A')
        # #endregion
        
        request = self.context.get('request')
        
        # Get optional size parameters from context (for mobile optimization)
        # Default size for tarot cards in app: 140x220 (exact size for card frame)
        image_width = self.context.get('image_width', 140)  # Exact card width
        image_height = self.context.get('image_height', 220)  # Exact card height
        
        # #region agent log
        _debug_log('serializers.py:218', 'Before image check', {
            'card_id': obj.id,
            'has_request': request is not None,
            'request_method': request.method if request else None,
            'image_width': image_width,
            'image_height': image_height
        }, 'B')
        # #endregion
        
        if obj.image and hasattr(obj.image, 'url'):
            try:
                # #region agent log
                _debug_log('serializers.py:225', 'Before accessing image.url', {
                    'card_id': obj.id,
                    'image_name': str(obj.image.name) if hasattr(obj.image, 'name') else None
                }, 'C')
                # #endregion
                
                # Use the optimized image endpoint with size parameters
                if request:
                    # Build URL to the optimized image endpoint
                    try:
                        # Build the endpoint path directly
                        image_endpoint = f"/api/v1/tarot/cards/{obj.id}/image/"
                        # Add size parameters as query string
                        params = {}
                        if image_width:
                            params['width'] = image_width
                        if image_height:
                            params['height'] = image_height
                        
                        if params:
                            image_endpoint = f"{image_endpoint}?{urlencode(params)}"
                        
                        absolute_url = request.build_absolute_uri(image_endpoint)
                        # #region agent log
                        _debug_log('serializers.py:238', 'Built absolute URI with optimization', {
                            'card_id': obj.id,
                            'absolute_url': absolute_url,
                            'base_url': request.build_absolute_uri('/')
                        }, 'E')
                        # #endregion
                        return absolute_url
                    except Exception as e:
                        # Fallback to original image if building URL fails
                        logger.warning(f"Failed to build optimized image URL: {e}")
                        try:
                            absolute_url = request.build_absolute_uri(obj.image.url)
                            return absolute_url
                        except Exception as e2:
                            logger.error(f"Failed to build absolute URI for original image: {e2}")
                            return None
                else:
                    # No request context, return relative URL to optimized endpoint
                    image_url = f"/api/v1/tarot/cards/{obj.id}/image/"
                    params = []
                    if image_width:
                        params.append(f"width={image_width}")
                    if image_height:
                        params.append(f"height={image_height}")
                    if params:
                        image_url = f"{image_url}?{'&'.join(params)}"
                    # #region agent log
                    _debug_log('serializers.py:244', 'Returning relative optimized URL (no request)', {
                        'card_id': obj.id,
                        'image_url': image_url
                    }, 'E')
                    # #endregion
                    return image_url
            except Exception as e:
                # #region agent log
                _debug_log('serializers.py:250', 'Error accessing image.url', {
                    'card_id': obj.id,
                    'error_type': str(type(e).__name__),
                    'error_message': str(e)
                }, 'D')
                # #endregion
                return None
        else:
            # #region agent log
            _debug_log('serializers.py:258', 'No image or no url attr', {
                'card_id': obj.id,
                'has_image': obj.image is not None,
                'has_url_attr': hasattr(obj.image, 'url') if obj.image else False
            }, 'A')
            # #endregion
            return None

