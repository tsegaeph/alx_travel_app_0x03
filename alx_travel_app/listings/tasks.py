from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(customer_email, booking_id):
    subject = f'Booking Confirmation #{booking_id}'
    message = f'Thank you for your booking! Your booking ID is {booking_id}.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])
    return f'Email sent to {customer_email}'
