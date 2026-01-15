from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, EmailVerification, NEW, CODE_VERIFIED, DONE
from django.utils.timezone import now
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from apps.main.utility import send_email



class SendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required =True)

    def validate_email(self, value):
        email = value.lower().strip()
        if CustomUser.objects.filter(email = email, auth_status = DONE).exists():
            raise ValidationError({
                'success': False,
                'message': "Bu email, allaqachon royxatdan otgan. Login Qiling"
            })
        return email
    
    def save(self):
        email = self.validated_data['email']

        user, created = CustomUser.objects.get_or_create(
            email = email,
            defaults = {
                'auth_status':NEW,
                'is_active': False
            }
        )
        if not user.can_resend_code():
            raise ValidationError({
                'success': False,
                'message': "Iltimos 2 daqiqa kuting va qayta urinib koring"
            })
        
        code = user.generate_verification_code()

        send_email(email, code)

        return user, code

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required =True, max_length= 4, min_length=4)

    def validate(self, data):
        email = data.get('email').lower().strip()
        code = data.get('code')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError({
                'success': False,
                'message': "Email topilmadi. Avval email yuboring"
            })
        
        verification = EmailVerification.objects.filter( user =user, code= code, is_verified = False).order_by('-created_at').first()

        if not verification:
            raise ValidationError({
                'success': False,
                'message': 'Kod notogri yoki allaqachon ishlatilgan'
            })
        
        if verification.is_expired():
            raise ValidationError({
                'success': False,
                'message': "Kodning muddati o'tgan. yangi kod sorang"
            })
        
        data['user'] = user
        data['verification'] = verification
        return data
    

    def save(self):
        user = self.validated_data['user']
        verification = self.validated_data['verification']

        verification.is_verified = True
        verification.save()

        user.auth_status = CODE_VERIFIED
        user.save()

        return user
    
class CompleteSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required =True, min_length=8)
    password_confirm = serializers.CharField(write_only = True, required = True)
    first_name = serializers.CharField(required= True, max_length = 30)
    last_name = serializers.CharField(required= True, max_length = 30)
    phone_number = serializers.CharField(required=False, max_length=20)

    def validate_email(self, value):
        email = value.lower().strip()

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError({
                'success': False,
                'message': "Email topilmadi. Avval email Tasdiqlang"
            })
        
        if user.auth_status != CODE_VERIFIED:
            raise ValidationError({
                'success': False,
                'message': 'Avval emailni tasdiqlang'
            })
        if user.auth_status == DONE:
            raise ValidationError({
                'success': False,
                'message': 'Siz allaqachon royxatdan otgansiz'
            })
        return email
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError({
                'success': False,
                'message': 'Parollar bir xil emas'
            })
        
        validate_password(data['password'])
        return data
    
    def validate_first_name(self, value):
        if len(value) < 2:
            raise ValidationError("Ism kamida 3 harfdan iborat bo'lishi kerak")
        
        if not value.replace(' ', '').isalpha():
            raise ValidationError("Ism faqat harflardan iborat bo'lishi kerak.")
        
        return value.strip()
    
    def validate_last_name(self, value):
        if len(value) < 2:
            raise ValidationError("Familiya kamida 3 harfdan iborat bo'lishi kerak")
        
        if not value.replace(' ', '').isalpha():
            raise ValidationError("Familiya faqat harflardan iborat bo'lishi kerak.")
        
        return value.strip()
    
    def save(self):
        email = self.validated_data['email']
        user = CustomUser.objects.get(email= email)

        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.phone_number = self.validated_data.get('phone_number', '')
        user.set_password(self.validated_data['password'])

        user.auth_status = DONE
        user.is_active = True
        user.save()

        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only = True, required = True)

    def validate(self, data):
        email = data.get('email').lower().strip()
        password = data.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)        
        except CustomUser.DoesNotExist:
            raise ValidationError({
                'success': False,
                'message': "Email yoki parol notog'ri"
            })
        
        if user.auth_status != DONE:
            raise ValidationError({
                'success': False,
                'message': "Avval ro'yxatdan oting"
            })
        
        user = authenticate(email= email, password=password)
        if not user:
            raise ValidationError({
                'success': False,
                'message': "Email yoki parol notogri"
            })
        data['user'] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'photo', 'bio', 'auth_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'username', 'auth_status', 'created_at', 'updated_at']


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields =['first_name', 'username', 'last_name', 'phone_number', 'bio', 'photo']
    
    def validate_first_name(self, value):
        if len(value) < 2:
            raise ValidationError("Ism kamida 3 harfdan iborat bo'lishi kerak")
        
        if not value.replace(' ', '').isalpha():
            raise ValidationError("Ism faqat harflardan iborat bo'lishi kerak.")
        
        return value.strip()
    
    def validate_last_name(self, value):
        if len(value) < 2:
            raise ValidationError("Familiya kamida 3 harfdan iborat bo'lishi kerak")
        
        if not value.replace(' ', '').isalpha():
            raise ValidationError("Familiya faqat harflardan iborat bo'lishi kerak.")
        
        return value.strip()
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password =serializers.CharField(write_only = True, required = True)
    new_password =serializers.CharField(write_only = True, required=True, min_length =8)
    new_password_confirm =serializers.CharField(write_only = True, required = True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise ValidationError({
                'success': False,
                'message': 'New Passwords dont match'
            })
        
        validate_password(data['new_password'])
        return data
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError('Eski parol notogri')
        return value
    
