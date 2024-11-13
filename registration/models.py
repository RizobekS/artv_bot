from ckeditor.fields import RichTextField
from django.db import models
from telegram import Bot

from registration_bot.settings import TELEGRAM_TOKEN


class Participant(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    chat_id = models.CharField(max_length=50, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    registration_order = models.PositiveIntegerField(editable=False, null=True)

    def __str__(self):
        return f"{self.registration_order}. {self.name}"

    def save(self, *args, **kwargs):
        # Проверяем, есть ли изменение статуса оплаты
        if self.pk:  # Только для уже существующих записей
            previous = Participant.objects.get(pk=self.pk)
            if not previous.is_paid and self.is_paid:  # Если is_paid изменился с False на True
                self.send_congratulatory_message()

        # Присваиваем порядковый номер только при первой регистрации
        if not self.pk:
            last_participant = Participant.objects.order_by('-registration_order').first()
            self.registration_order = last_participant.registration_order + 1 if last_participant else 1

        super().save(*args, **kwargs)

    def send_congratulatory_message(self):
        if self.chat_id:  # Отправка только если chat_id указан
            bot = Bot(token=TELEGRAM_TOKEN)
            try:
                message_text = f"""Tabriklaymiz, siz Art Vernissage yopiq auksioni ishtirokchisiga aylandingiz!\n Sizning tartib raqamingiz - {self.registration_order}\n\n===================\n\nПоздравляю, вы стали участником закрытого аукциона Art Vernissage!\nВаш порядковый номер - {self.registration_order}"""
                bot.send_message(chat_id=self.chat_id, text=message_text)
                print(f"Сообщение отправлено участнику: {self.name}")
            except Exception as e:
                print(f"Ошибка при отправке для {self.name}: {e}")


class AuctionMessage(models.Model):
    title = models.CharField(max_length=355)
    content = RichTextField()  # Поле с поддержкой форматирования
    send_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
