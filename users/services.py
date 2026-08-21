from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import email_verification_token


def send_verification_email(user, request):
    """Отправляет письмо с ссылкой для подтверждения email"""
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = f"{request.scheme}://{request.get_host()}/users/verify/{uid}/{token}/"

    print(f"Ссылка для подтверждения: {verification_url}")

    send_mail(
        subject='Подтверждение email',
        message=f'Перейдите по ссылке для подтверждения email: {verification_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )