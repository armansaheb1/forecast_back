from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'age', 'gender', 
            'relationship_status', 'job_status', 'occupation',
            'city', 'country', 'address', 'bio', 'avatar',
            'language', 'is_verified', 'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'date_joined', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }
    
    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        if value:
            from datetime import date
            today = date.today()
            if value > today:
                raise serializers.ValidationError("تاریخ تولد نمی‌تواند در آینده باشد.")
            # Check if age is reasonable (between 13 and 120)
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 13:
                raise serializers.ValidationError("سن باید حداقل 13 سال باشد.")
            if age > 120:
                raise serializers.ValidationError("تاریخ تولد نامعتبر است.")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='تأیید رمز عبور'
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'phone_number',
            'date_of_birth', 'gender', 'language'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "رمزهای عبور مطابقت ندارند."
            })
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("این ایمیل قبلاً استفاده شده است.")
        return value
    
    def validate_username(self, value):
        """Validate username uniqueness"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً استفاده شده است.")
        return value
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'age', 'gender',
            'relationship_status', 'job_status', 'occupation',
            'city', 'country', 'address', 'bio', 'avatar', 'language'
        ]
    
    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        if value:
            from datetime import date
            today = date.today()
            if value > today:
                raise serializers.ValidationError("تاریخ تولد نمی‌تواند در آینده باشد.")
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 13:
                raise serializers.ValidationError("سن باید حداقل 13 سال باشد.")
            if age > 120:
                raise serializers.ValidationError("تاریخ تولد نامعتبر است.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='تأیید رمز عبور جدید'
    )
    
    def validate(self, attrs):
        """Validate passwords"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "رمزهای عبور جدید مطابقت ندارند."
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز عبور فعلی اشتباه است.")
        return value

