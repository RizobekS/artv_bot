# auction/management/commands/send_message.py
from django.core.management.base import BaseCommand
from telegram import Bot
from registration.models import Participant

from registration_bot.settings import TELEGRAM_TOKEN


class Command(BaseCommand):
    help = 'Отправка сообщения всем участникам аукциона'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='Сообщение для отправки участникам')

    def handle(self, *args, **options):
        message_text = options['message']
        bot = Bot(token=TELEGRAM_TOKEN)

        participants = Participant.objects.filter(chat_id__isnull=False)
        for participant in participants:
            try:
                bot.send_message(chat_id=participant.chat_id, text=message_text)
                self.stdout.write(self.style.SUCCESS(f"Сообщение отправлено {participant.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка при отправке для {participant.name}: {e}"))
