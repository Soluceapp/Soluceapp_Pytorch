from django.test import TestCase
from unittest import TestCase
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tests.variables import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

# Create your tests here : pour tester dans venv : py src/manage.py test
class EmailTestCase(TestCase):
    def setUp(self) :
        settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
        settings.EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
        settings.EMAIL_HOST_USER = '2cf4d4c5d110b3'
        settings.EMAIL_HOST_PASSWORD = '********37ae'
        settings.EMAIL_PORT = '2525'

    def test_send_mail(self):
        subject = "Test de l'application Pytorch.Soluceapp"
        html_message = "ceci cela"
        #render_to_string ('tests/mail_template.html',{'context':'values'})
        plain_message = strip_tags(html_message)
        from_email = 'contact@soluceapp.com'
        to = 'test.test@test.com'
        message = EmailMessage(subject=subject, body=plain_message, from_email=from_email, to=(to,))
        with open('tests/attachement.pdf') as file:
            message.attach('attachment.pdf',file.read(),'file/pdf')

        message.send()