from django.db import models

class Participant(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    chat_id = models.CharField(max_length=50, blank=True, null=True)  # Поле для хранения chat_id

    def __str__(self):
        return self.name