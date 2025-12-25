from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from datetime import date
import json


# Create your models here.

class CustomUser(AbstractUser):
    """
    Custom User model with extended fields for user profile information
    """
    
    # Gender choices
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
        ('O', 'سایر'),
        ('N', 'ترجیح می‌دهم نگویم'),
    ]
    
    # Relationship status choices
    RELATIONSHIP_STATUS_CHOICES = [
        ('single', 'مجرد'),
        ('married', 'متأهل'),
        ('divorced', 'مطلقه'),
        ('widowed', 'بیوه'),
        ('in_relationship', 'در رابطه'),
        ('complicated', 'پیچیده'),
        ('prefer_not_to_say', 'ترجیح می‌دهم نگویم'),
    ]
    
    # Job status choices
    JOB_STATUS_CHOICES = [
        ('employed', 'شاغل'),
        ('unemployed', 'بیکار'),
        ('student', 'دانشجو'),
        ('retired', 'بازنشسته'),
        ('self_employed', 'خویش‌فرما'),
        ('freelancer', 'فریلنسر'),
        ('homemaker', 'خانه‌دار'),
        ('prefer_not_to_say', 'ترجیح می‌دهم نگویم'),
    ]
    
    # Basic Information
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="شماره تلفن باید در فرمت صحیح وارد شود. مثال: +989123456789"
            )
        ],
        verbose_name='شماره تلفن'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ تولد'
    )
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='جنسیت'
    )
    
    # Relationship Information
    relationship_status = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='وضعیت رابطه'
    )
    
    # Job Information
    job_status = models.CharField(
        max_length=20,
        choices=JOB_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='وضعیت شغلی'
    )
    
    occupation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شغل'
    )
    
    # Location Information
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شهر'
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='ایران',
        verbose_name='کشور'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='آدرس'
    )
    
    # Profile Information
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='بیوگرافی'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='عکس پروفایل'
    )
    
    # Language preference
    # Ordered by marketing priority and business potential for fortune telling app
    LANGUAGE_CHOICES = [
        # Tier 1: Primary target markets (high interest + purchasing power)
        ('en', 'English'),                    # Global market, high purchasing power
        ('fa', 'فارسی (Persian)'),            # Primary target: Iran, Afghanistan - very high interest
        ('ar', 'العربية (Arabic)'),            # Middle East: huge market, high interest
        ('tr', 'Türkçe (Turkish)'),           # Turkey: large market, strong interest
        ('es', 'Español (Spanish)'),          # Latin America + Spain: huge market
        ('ur', 'اردو (Urdu)'),                # Pakistan + India: large market, high interest
        
        # Tier 2: High purchasing power markets
        ('fr', 'Français (French)'),          # France, Canada, Africa: high purchasing power
        ('de', 'Deutsch (German)'),           # Germany, Austria, Switzerland: very high purchasing power
        ('it', 'Italiano (Italian)'),         # Italy: high purchasing power, interest in mysticism
        ('pt', 'Português (Portuguese)'),     # Brazil + Portugal: huge market
        ('ru', 'Русский (Russian)'),          # Russia + CIS: large market, interest in fortune telling
        ('ja', '日本語 (Japanese)'),            # Japan: very high purchasing power
        ('ko', '한국어 (Korean)'),             # South Korea: high purchasing power, tech-savvy
        ('he', 'עברית (Hebrew)'),             # Israel: high purchasing power, tech-savvy
        
        # Tier 3: Large population markets with growing interest
        ('hi', 'हिन्दी (Hindi)'),              # India: huge market, growing mobile usage
        ('id', 'Bahasa Indonesia (Indonesian)'),  # Indonesia: huge market, high interest
        ('th', 'ไทย (Thai)'),                 # Thailand: strong interest in fortune telling
        ('vi', 'Tiếng Việt (Vietnamese)'),    # Vietnam: growing market, interest in fortune telling
        ('bn', 'বাংলা (Bengali)'),            # Bangladesh: large market, growing
        ('ms', 'Bahasa Melayu (Malay)'),      # Malaysia + Indonesia: large market
        ('zh', '中文 (Chinese)'),              # China: huge market but competitive
        
        # Tier 4: Regional markets with good potential
        ('pl', 'Polski (Polish)'),            # Poland: growing market, good purchasing power
        ('nl', 'Nederlands (Dutch)'),         # Netherlands: high purchasing power
        ('uk', 'Українська (Ukrainian)'),     # Ukraine: growing market
        ('ro', 'Română (Romanian)'),          # Romania: growing market
        ('el', 'Ελληνικά (Greek)'),           # Greece: interest in mysticism
        ('cs', 'Čeština (Czech)'),            # Czech Republic: good purchasing power
        ('sv', 'Svenska (Swedish)'),          # Sweden: high purchasing power
        ('no', 'Norsk (Norwegian)'),          # Norway: very high purchasing power
        ('da', 'Dansk (Danish)'),             # Denmark: high purchasing power
        ('fi', 'Suomi (Finnish)'),            # Finland: high purchasing power
        ('hu', 'Magyar (Hungarian)'),         # Hungary: growing market
        ('az', 'Azərbaycan (Azerbaijani)'),   # Azerbaijan: regional market
        
        # Tier 5: Indian subcontinent languages (large populations)
        ('ta', 'தமிழ் (Tamil)'),              # Tamil: large diaspora, growing
        ('te', 'తెలుగు (Telugu)'),            # Telugu: large population
        ('mr', 'मराठी (Marathi)'),            # Marathi: large population
        ('gu', 'ગુજરાતી (Gujarati)'),         # Gujarati: large population
        ('pa', 'ਪੰਜਾਬੀ (Punjabi)'),           # Punjabi: large population
        ('ml', 'മലയാളം (Malayalam)'),        # Malayalam: growing market
        ('kn', 'ಕನ್ನಡ (Kannada)'),            # Kannada: growing market
        ('ne', 'नेपाली (Nepali)'),            # Nepali: regional market
        
        # Tier 6: Southeast Asian markets
        ('my', 'မြန်မာ (Burmese)'),           # Myanmar: growing market
        ('km', 'ខ្មែរ (Khmer)'),              # Cambodia: growing market
        ('lo', 'ລາວ (Lao)'),                  # Laos: regional market
        ('si', 'සිංහල (Sinhala)'),            # Sri Lanka: regional market
        
        # Tier 7: African markets
        ('sw', 'Kiswahili (Swahili)'),        # East Africa: large market, growing
        ('am', 'አማርኛ (Amharic)'),            # Ethiopia: large population
        ('ha', 'Hausa'),                      # West Africa: large market
        ('yo', 'Yorùbá (Yoruba)'),            # Nigeria: large population
        ('ig', 'Igbo'),                       # Nigeria: large population
        ('zu', 'isiZulu (Zulu)'),             # South Africa: regional market
        ('af', 'Afrikaans'),                  # South Africa: regional market
        
        # Other
        ('eo', 'Esperanto'),                  # Constructed language
    ]
    
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name='زبان'
    )
    
    # Additional fields
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تأیید شده'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name() or self.email}"
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class File(models.Model):
    image = models.ImageField(upload_to="coffee")
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coffee_readings',
        verbose_name='کاربر'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return f"File {self.id} - {self.image.name}"


class FortuneProfile(models.Model):
    """
    Model for fortune reading profiles.
    Users can create multiple profiles for different people to get personalized readings.
    """
    
    # Gender choices
    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
        ('other', 'سایر'),
    ]
    
    # Relationship status choices
    RELATIONSHIP_STATUS_CHOICES = [
        ('single', 'مجرد'),
        ('married', 'متأهل'),
        ('divorced', 'مطلقه'),
        ('widowed', 'بیوه'),
        ('in_relationship', 'در رابطه'),
    ]
    
    # Job status choices
    JOB_STATUS_CHOICES = [
        ('employed', 'شاغل'),
        ('unemployed', 'بیکار'),
        ('student', 'دانشجو'),
        ('retired', 'بازنشسته'),
        ('self_employed', 'خویش‌فرما'),
        ('freelancer', 'فریلنسر'),
    ]
    
    # Owner of the profile
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='fortune_profiles',
        verbose_name='کاربر',
        null=True,
        blank=True,  # Allow anonymous profiles
    )
    
    # Basic Information
    name = models.CharField(max_length=200, verbose_name='نام')
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ تولد'
    )
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='سن'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='جنسیت'
    )
    
    # Relationship Information
    relationship_status = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='وضعیت رابطه'
    )
    
    # Job Information
    job_status = models.CharField(
        max_length=20,
        choices=JOB_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='وضعیت شغلی'
    )
    
    # Location Information
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شهر'
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='کشور'
    )
    
    # Additional notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت‌ها'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')
    
    class Meta:
        verbose_name = 'پروفایل فال'
        verbose_name_plural = 'پروفایل‌های فال'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username if self.user else 'Anonymous'}"
    
    @property
    def calculated_age(self):
        """Calculate age from birth date"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    def save(self, *args, **kwargs):
        # Auto-calculate age if birth_date is provided and age is not set
        if self.birth_date and not self.age:
            self.age = self.calculated_age
        super().save(*args, **kwargs)


class TarotCard(models.Model):
    """
    Model for Tarot cards with images.
    Admin can upload card images through Django admin panel.
    """
    
    # Card identification
    name = models.CharField(max_length=200, verbose_name='نام کارت (پیش‌فرض)')
    name_en = models.CharField(max_length=200, blank=True, null=True, verbose_name='نام انگلیسی')
    
    # Multilingual names - JSON field storing translations
    # Format: {"en": "The Fool", "fa": "احمق", "ar": "الأحمق", ...}
    names_translations = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='ترجمه نام‌ها',
        help_text='JSON object with language codes as keys and translated names as values. Example: {"en": "The Fool", "fa": "احمق", "ar": "الأحمق"}'
    )
    
    # Card type
    SUIT_CHOICES = [
        ('major', 'Major Arcana'),
        ('wands', 'Wands'),
        ('cups', 'Cups'),
        ('swords', 'Swords'),
        ('pentacles', 'Pentacles'),
    ]
    
    suit = models.CharField(
        max_length=20,
        choices=SUIT_CHOICES,
        verbose_name='نوع کارت'
    )
    
    number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='شماره کارت'
    )
    
    # Card image
    image = models.ImageField(
        upload_to='tarotcards',
        blank=True,
        null=True,
        verbose_name='عکس کارت'
    )
    
    # Card meanings (base meanings, will be enhanced by AI)
    meaning = models.TextField(
        blank=True,
        null=True,
        verbose_name='معنی کارت'
    )
    
    reversed_meaning = models.TextField(
        blank=True,
        null=True,
        verbose_name='معنی وارونه'
    )
    
    # Emoji for card representation
    emoji = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='ایموجی'
    )
    
    # Ordering
    order = models.IntegerField(
        default=0,
        verbose_name='ترتیب'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')
    
    class Meta:
        verbose_name = 'کارت تاروت'
        verbose_name_plural = 'کارت‌های تاروت'
        ordering = ['order', 'suit', 'number']
        unique_together = [['suit', 'number', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.get_suit_display()})"
    
    def get_name(self, language_code='en'):
        """
        Get card name in specified language.
        Falls back to English, then default name if translation not found.
        """
        if self.names_translations and language_code in self.names_translations:
            return self.names_translations[language_code]
        if self.name_en:
            return self.name_en
        return self.name
    
    @property
    def image_url(self):
        """Get full URL for card image"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
