from django.core.mail import send_mail
from django.conf import settings


def send_email(email, code):
    subject = "Your Verification Code: "
    message = (
        f"Your verification code is: {code}\n\n"
        "This code will expire in 5 minutes.\n"
        "If you did not request this, please ignore this email."
    )
    send_mail(
        subject, 
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently = False,

    )
