import logging
from io import BytesIO
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from PIL import Image
from . import models

logger = logging.getLogger('main')


def get_tarot_card_image(request, card_id):
    """
    Serve tarot card image with optional resizing.
    
    Query parameters:
    - width: Desired width in pixels (optional)
    - height: Desired height in pixels (optional)
    - If both are provided, image will be resized maintaining aspect ratio
    - If only one is provided, the other will be calculated to maintain aspect ratio
    """
    try:
        card = get_object_or_404(models.TarotCard, pk=card_id)
        
        if not card.image:
            raise Http404("Card image not found")
        
        # Get original image
        image = Image.open(card.image)
        original_format = image.format or 'JPEG'
        
        # Parse size parameters from query string
        # Default size: 140x220 (exact card frame size)
        target_width = 140
        target_height = 220
        
        width_param = request.GET.get('width')
        height_param = request.GET.get('height')
        
        if width_param:
            try:
                target_width = int(width_param)
            except (ValueError, TypeError):
                target_width = 140  # Fallback to default
        
        if height_param:
            try:
                target_height = int(height_param)
            except (ValueError, TypeError):
                target_height = 220  # Fallback to default
        
        # Always resize to target dimensions (default 140x220)
        # Calculate dimensions maintaining aspect ratio
        original_width, original_height = image.size
        
        # Resize to fit within bounds while maintaining aspect ratio
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # Resize image with high-quality resampling
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        output = BytesIO()
        
        # Preserve format, default to JPEG
        if original_format == 'PNG':
            image.save(output, format='PNG', optimize=True)
            content_type = 'image/png'
        else:
            # Convert to RGB if necessary (for JPEG)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            image.save(output, format='JPEG', quality=85, optimize=True)
            content_type = 'image/jpeg'
        
        output.seek(0)
        
        # Return response
        response = HttpResponse(output.getvalue(), content_type=content_type)
        response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
        return response
        
    except Exception as e:
        logger.error(f"Error serving tarot card image: {str(e)}", exc_info=True)
        raise Http404("Error loading image")

