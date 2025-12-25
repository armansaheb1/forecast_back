from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import CustomUser, File, FortuneProfile, TarotCard


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for Custom User model"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number', 
                    'gender', 'relationship_status', 'job_status', 'language', 
                    'is_verified', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_verified', 
                   'gender', 'relationship_status', 'job_status', 'language', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('اطلاعات شخصی'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 
                      'date_of_birth', 'gender', 'avatar', 'bio', 'language')
        }),
        (_('اطلاعات رابطه و شغل'), {
            'fields': ('relationship_status', 'job_status', 'occupation')
        }),
        (_('اطلاعات مکانی'), {
            'fields': ('country', 'city', 'address')
        }),
        (_('دسترسی‌ها'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 
                      'groups', 'user_permissions'),
        }),
        (_('تاریخ‌های مهم'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    ordering = ['-date_joined']


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'image', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['image', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']


@admin.register(FortuneProfile)
class FortuneProfileAdmin(admin.ModelAdmin):
    """Admin interface for Fortune Profile model"""
    
    list_display = ['id', 'name', 'user', 'age', 'gender', 'job_status', 
                    'relationship_status', 'city', 'country', 'created_at']
    list_filter = ['gender', 'job_status', 'relationship_status', 
                   'country', 'created_at', 'updated_at']
    search_fields = ['name', 'user__username', 'user__email', 'city', 'country', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']
    
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('user', 'name', 'birth_date', 'age', 'gender')
        }),
        (_('وضعیت'), {
            'fields': ('job_status', 'relationship_status')
        }),
        (_('مکان'), {
            'fields': ('city', 'country')
        }),
        (_('یادداشت‌ها'), {
            'fields': ('notes',)
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(TarotCard)
class TarotCardAdmin(admin.ModelAdmin):
    """Admin interface for Tarot Card model"""
    
    list_display = ['id', 'name', 'suit', 'number', 'order', 'image_preview', 'created_at']
    list_filter = ['suit', 'created_at', 'updated_at']
    search_fields = ['name', 'name_en', 'meaning', 'reversed_meaning']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    ordering = ['order', 'suit', 'number']
    
    fieldsets = (
        (_('اطلاعات کارت'), {
            'fields': ('name', 'name_en', 'names_translations', 'suit', 'number', 'order', 'emoji')
        }),
        (_('عکس کارت'), {
            'fields': ('image', 'image_preview')
        }),
        (_('معانی'), {
            'fields': ('meaning', 'reversed_meaning')
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">بدون عکس</span>')
    image_preview.short_description = 'پیش‌نمایش عکس'
