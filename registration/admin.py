from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.html import strip_tags
from telegram import Bot

from .management.commands.send_message import send_message_to_paid_participants
from .models import Participant, AuctionMessage
from .forms import MessageForm
from registration_bot.settings import TELEGRAM_TOKEN


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'registration_order', 'is_paid')

    # Добавляем кастомный URL для отправки сообщений
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-message/', self.admin_site.admin_view(self.send_message), name="send-message"),
        ]
        return custom_urls + urls

    # Обработчик для отправки сообщений
    def send_message(self, request):
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message_text = form.cleaned_data['message']
                bot = Bot(token=TELEGRAM_TOKEN)

                participants = Participant.objects.filter(chat_id__isnull=False)
                for participant in participants:
                    try:
                        bot.send_message(chat_id=participant.chat_id, text=message_text)
                    except Exception as e:
                        self.message_user(request, f"Ошибка при отправке для {participant.name}: {e}", level='error')

                self.message_user(request, "Сообщение успешно отправлено всем участникам!")
                return redirect("..")  # Возвращает к списку участников

        else:
            form = MessageForm()

        context = {
            'form': form,
            'title': "Отправка сообщения участникам",
        }
        return TemplateResponse(request, "admin/send_message.html", context)


class AuctionMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'send_date')


def send_latest_auction_message():
    message = AuctionMessage.objects.latest('send_date')
    send_message_to_paid_participants(strip_tags(message.content))


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(AuctionMessage, AuctionMessageAdmin)
