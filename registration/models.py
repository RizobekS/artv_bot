from ckeditor.fields import RichTextField
from django.db import models

class Participant(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    chat_id = models.CharField(max_length=50, blank=True, null=True)  # Поле для хранения chat_id
    is_paid = models.BooleanField(default=False)  # Флаг оплаты
    registration_order = models.PositiveIntegerField(editable=False, null=True)  # Порядковый номер регистрации

    def __str__(self):
        return f"{self.registration_order}. {self.name}"

    def save(self, *args, **kwargs):
        # Присваиваем порядковый номер только при первой регистрации
        if not self.pk:
            last_participant = Participant.objects.order_by('-registration_order').first()
            self.registration_order = last_participant.registration_order + 1 if last_participant else 1
        super().save(*args, **kwargs)


class AuctionMessage(models.Model):
    title = models.CharField(max_length=355)
    content = RichTextField()  # Поле с поддержкой форматирования
    send_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
