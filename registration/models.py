import os

from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from telegram import Bot, InputMediaPhoto

from registration_bot.settings import TELEGRAM_TOKEN, GROUP_CHAT_ID


class Participant(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    chat_id = models.CharField(max_length=50, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    registration_order = models.PositiveIntegerField(editable=False, null=True)

    def __str__(self):
        return f"{self.registration_order}. {self.name}"

    def save(self, *args, **kwargs):
        if self.pk:  # Только для уже существующих записей
            previous = Participant.objects.get(pk=self.pk)
            if not previous.is_paid and self.is_paid:  # Если is_paid изменился с False на True
                self.send_congratulatory_message()
        # Проверка для новой регистрации (нового участника)
        is_new = not self.pk  # True, если это новая запись

        # Присваиваем порядковый номер только при первой регистрации
        if is_new:
            last_participant = Participant.objects.order_by('-registration_order').first()
            self.registration_order = last_participant.registration_order + 1 if last_participant else 1

        super().save(*args, **kwargs)

        # Если это новый участник, отправляем уведомление в группу
        if is_new:
            self.notify_group_of_registration()

    def send_congratulatory_message(self):
        if self.chat_id:  # Отправка только если chat_id указан
            bot = Bot(token=TELEGRAM_TOKEN)
            try:
                # Текст сообщения
                message_text = (
                    f"Tabriklaymiz, siz Art Vernissage yopiq auksioni ishtirokchisiga aylandingiz!\n"
                    f"Sizning tartib raqamingiz - {self.registration_order}\n\n"
                    f"Auktsion bo'lib o'tadigan joy xaritasi: [Restoran Miras](https://yandex.com/maps/org/miras/156735956162?si=b4wud2ud6tgn511fur4k6qb8hr)\n"
                    f"Manzil: Toshkent sh. Amir Temur ko'chasi, 60\n"
                    f"Sana va vaqt: 2024-yil 27-noyabr, soat 18:00\n"
                    f"Biz sizni tadbirda kutamiz!\n\n"
                    f"------------------\n\n"
                    f"Поздравляю, вы стали участником закрытого аукциона Art Vernissage!\n"
                    f"Ваш порядковый номер - {self.registration_order}\n\n"
                    f"Карта проведения аукциона: [Ресторан Miras](https://yandex.com/maps/org/miras/156735956162?si=b4wud2ud6tgn511fur4k6qb8hr)\n"
                    f"Адрес: г. Ташкент, ул. Амира Темура, д. 60\n"
                    f"Дата и время: 27 ноября 2024 года, 18:00\n\n"
                    f"Ждём вас на мероприятии!"
                )

                # Пути к фотографиям
                photo_paths = [
                    os.path.join(settings.BASE_DIR, "1.jpg"),  # Первая фотография
                    os.path.join(settings.BASE_DIR, "2.jpg"),  # Вторая фотография
                ]

                # Отправка фотографий с подписью
                media_group = [
                    InputMediaPhoto(media=open(photo_path, 'rb')) for photo_path in photo_paths
                ]
                bot.send_media_group(chat_id=self.chat_id, media=media_group)

                # Отправка текста с ссылкой
                bot.send_message(chat_id=self.chat_id, text=message_text, parse_mode="Markdown")
                print(f"Сообщение с фото отправлено участнику: {self.name}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения для {self.name}: {e}")

    def notify_group_of_registration(self):
        # Формируем текст сообщения
        message_text = (
            f"Новый участник зарегистрирован:\n"
            f"Имя: {self.name}\n"
            f"Телефон: {self.phone_number}\n"
            f"Порядковый номер: {self.registration_order}"
        )

        bot = Bot(token=TELEGRAM_TOKEN)
        try:
            bot.send_message(chat_id=GROUP_CHAT_ID, text=message_text)
            print(f"Сообщение о регистрации отправлено в группу: {self.name}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения в группу: {e}")


class AuctionMessage(models.Model):
    title = models.CharField(max_length=355)
    content = RichTextField()  # Поле с поддержкой форматирования
    send_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
