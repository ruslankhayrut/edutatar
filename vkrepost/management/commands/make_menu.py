import logging

from django.core.management.base import BaseCommand

from edutatar.settings import EDU_LOGIN, EDU_PASSWORD
from gmail_api import gmail_attachments
from gmail_api.daily_menu import EdutatarSession, MenuUploader

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args: str, **options: str) -> None:
        g_session = gmail_attachments.connect()
        edu_session = EdutatarSession(EDU_LOGIN, EDU_PASSWORD)
        edu_session.login()
        uploader = MenuUploader(edu_session, g_session)
        uploader.make_it()
