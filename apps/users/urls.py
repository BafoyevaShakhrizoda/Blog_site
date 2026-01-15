
from django.urls import path
from .views import (
    SendCodeView, VerifyCodeView, CompleteSignUpView, LoginView, 
    LogoutView, ProfileView, UpdateProfileView, ChangePasswordView, ResendCodeView,
    SendCodeHTMLView, VerifyCodeHTMLView, CompleteSignupHTMLView, 
    LoginHTMLView, LogoutHTMLView, profile_html, update_profile_html, change_password_html
)

app_name = 'users'

urlpatterns = [
    path('api/send-code/', SendCodeView.as_view(), name='send_code_api'),
    path('api/verify-code/', VerifyCodeView.as_view(), name='verify_code_api'),
    path('api/complete-signup/', CompleteSignUpView.as_view(), name='complete_signup_api'),
    path('api/resend-code/', ResendCodeView.as_view(), name='resend_code_api'),
    path('api/login/', LoginView.as_view(), name='login_api'),
    path('api/logout/', LogoutView.as_view(), name='logout_api'),
    path('api/profile/', ProfileView.as_view(), name='profile_api'),
    path('api/profile/update/', UpdateProfileView.as_view(), name='update_profile_api'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password_api'),

    path('send-code/', SendCodeHTMLView.as_view(), name='send_code_html'),
    path('verify-code/', VerifyCodeHTMLView.as_view(), name='verify_code_html'),
    path('complete-signup/', CompleteSignupHTMLView.as_view(), name='complete_signup_html'),
    path('login/', LoginHTMLView.as_view(), name='login_html'),
    path('logout/', LogoutHTMLView.as_view(), name='logout_html'),
    path('profile/', profile_html, name='profile_html'),
    path('profile/update/', update_profile_html, name='update_profile_html'),
    path('change-password/', change_password_html, name='change_password_html'),
]