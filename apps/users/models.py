from django.db import models

from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.timezone import now
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
import random
from datetime import timedelta


NEW = 'new'
CODE_VERIFIED = 'code_verified'
DONE = 'done'

class CustomUser(AbstractUser):
    AUTH_STATUS_CHOICES = (
        (NEW, 'NEW'),
        (CODE_VERIFIED, 'CODE_VERIFIED'),
        (DONE, 'DONE'),
    )
    email = models.EmailField(unique=True)
    auth_status = models.CharField( max_length=20, choices=AUTH_STATUS_CHOICES, default=NEW)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='users_photo/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
    
    def __str__(self):
        return self.username
    
    def generate_verification_code(self):
        code = ''.join([str(random.randint(0, 9)) for _ in range(4)])

        EmailVerification.objects.filter( user=self, is_verified=False).delete()
        EmailVerification.objects.create( user=self, code=code )
        return code
    
    def generate_username(self):
        if not self.username or self.username.startswith('user_'):
            base_username = f"user_{uuid.uuid4().hex[:8]}"
            username = base_username
            counter = 1
            
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                
            self.username = username
    
    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    def can_resend_code(self):
        last_code = EmailVerification.objects.filter(
            user=self,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not last_code:
            return True
            
        time_passed = now() - last_code.created_at
        return time_passed.total_seconds() > 120

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        self.generate_username()
        
        super().save(*args, **kwargs)
    


class EmailVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=4)
    is_verified = models.BooleanField(default=False)
    expiration_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'email_verification'
        verbose_name = 'Email Tasdiqlash'
        verbose_name_plural = 'Email Tasdiqlash'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"
    
    def is_expired(self):
        return now()>self.expiration_time
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.expiration_time = now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
    


