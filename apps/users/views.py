from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import SendCodeSerializer, VerifyCodeSerializer, CompleteSignUpSerializer, LoginSerializer, UserProfileSerializer, UpdateProfileSerializer, ChangePasswordSerializer
from .models import CustomUser, DONE
from apps.main.utility import send_email
from django.contrib.auth import login
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json


class SendCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SendCodeSerializer

    def post(self, request):
        serializer = SendCodeSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user, code = serializer.save()

        return Response({
            'success': True,
            'message': f"Tasdiqlash kodi {user.email} ga jonatildi",

        }, status=status.HTTP_200_OK)

class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class =VerifyCodeSerializer

    def post(self, request):
        serializer = VerifyCodeSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response({
            'success': True, 
            'message': "Email tasdiqlandi. Endi royxatdan oting.",
            'data': {
                'email': user.email,
                'auth_status': user.auth_status
            }
        }, status=status.HTTP_200_OK)

class CompleteSignUpView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CompleteSignUpSerializer

    def post(self, request):
        serializer = CompleteSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        tokens = user.get_tokens()

        return Response({
            'success': True,
            'message': "You successfully signed up",
            'data': {
                'user': UserProfileSerializer(user).data,
                'tokens': tokens
            },
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)
        tokens = user.get_tokens()

        return Response({
            'success': True,
            'message': "Logged in successfully",
            'data': {
                'user': UserProfileSerializer(user).data,
                'tokens':tokens
            }
        }, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        logout(request)
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'success': False, 
                    'message': 'Refresh token required'
                    },status=status.HTTP_400_BAD_REQUEST)


            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                'success': True,
                'message': "Logged out successfully"

            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': "Xatolik yuz berdi"
            }, status=status.HTTP_400_BAD_REQUEST)
            
class ProfileView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
    
class UpdateProfileView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial = partial)
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)

        return Response({
            'success': True, 
            'message': "Profile Updated Successfully",
            'data': UserProfileSerializer(serializer.instance).data
        })

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'success': True, 
            'message': "Password Changed successfully"
        }, status=status.HTTP_200_OK)
    
class ResendCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email', '').lower().strip()

        if not email:
            return Response({
                'success': False,
                'message': "Email ni kiriting"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email = email)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Could find the email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.auth_status == DONE:
            return Response({
                'success': False,
                'message': 'Siz allaqachon royxatdan otgansiz. Login qiling'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.can_resend_code():
            return Response({
                'success': False,
                'message': 'Iltimos 2 daqiqa kuting'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        code = user.generate_verification_code()
        send_email(email, code)
        return Response({
            'success': True,
            'message': f"Tasdiqlash kodi {email} ga jonatildi"
        }, status=status.HTTP_200_OK)
    

# Templates views
@method_decorator(never_cache, name='dispatch')
class SendCodeHTMLView(TemplateView):
    template_name = 'users/send_code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Send Verification Code'
        return context

class VerifyCodeHTMLView(TemplateView):
    template_name = 'users/verify_code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Verify Code'
        context['email'] = self.request.GET.get('email', '')
        return context

class CompleteSignupHTMLView(TemplateView):
    template_name = 'users/complete_signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Complete Signup'
        context['email'] = self.request.GET.get('email', '')
        return context

class LoginHTMLView(TemplateView):
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

class LogoutHTMLView(TemplateView):
    template_name = 'users/logout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Logout'
        return context

@login_required
def profile_html(request):
    context = {
        'title': 'Profile',
        'user': request.user
    }
    return render(request, 'users/profile.html', context)

@login_required
def update_profile_html(request):
    context = {
        'title': 'Update Profile',
        'user': request.user
    }
    return render(request, 'users/update_profile.html', context)

@login_required
def change_password_html(request):
    context = {
        'title': 'Change Password'
    }
    return render(request, 'users/change_password.html', context)