from django.core.mail import send_mail
from django.conf import settings
from .models import MailingAttempt


def send_mailing(mailing):
    recipients = mailing.recipients.all()
    for client in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='Письмо отправлено успешно'
            )
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failed',
                server_response=str(e)
            )