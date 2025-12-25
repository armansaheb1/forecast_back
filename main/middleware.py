import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('main')


class RateLimitMiddleware:
    """
    Middleware for rate limiting API requests.
    Limits requests per IP address.
    Compatible with both sync and async requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limit settings (requests per minute)
        self.rate_limit = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 10)
        self.rate_limit_window = 60  # seconds
        
    def __call__(self, request):
        # Only apply rate limiting to API endpoints
        if request.path.startswith('/api/'):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Create cache key
            cache_key = f'rate_limit_{ip}'
            
            # Get current request count
            requests = cache.get(cache_key, 0)
            
            if requests >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded. Please try again later.',
                        'retry_after': self.rate_limit_window
                    },
                    status=429
                )
            
            # Increment request count
            cache.set(cache_key, requests + 1, self.rate_limit_window)
        
        response = self.get_response(request)
        return response

