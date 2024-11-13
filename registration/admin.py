from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.html import strip_tags
from telegram import Bot, ParseMode

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


def send_latest_auction_message():
    try:
        # Получаем последнее сообщение для отправки
        message = AuctionMessage.objects.latest('send_date')
        if not message:
            print("Нет доступных сообщений для отправки.")
            return

        message_text = message.content  # Оставляем HTML или Markdown теги

        # Отправка сообщения только оплатившим участникам
        bot = Bot(token=TELEGRAM_TOKEN)
        paid_participants = Participant.objects.filter(is_paid=True, chat_id__isnull=False)
        if not paid_participants:
            print("Нет участников с оплатой для отправки сообщений.")
            return

        for participant in paid_participants:
            try:
                # Указываем режим разметки HTML или MarkdownV2
                bot.send_message(chat_id=participant.chat_id, text=message_text, parse_mode=ParseMode.HTML)
                print(f"Сообщение отправлено участнику: {participant.name}")
            except Exception as e:
                print(f"Ошибка при отправке для {participant.name}: {e}")

    except AuctionMessage.DoesNotExist:
        print("Нет сообщений для отправки.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


class AuctionMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'send_date')

    # Добавляем обработчик для сохранения и отправки сообщений
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        send_latest_auction_message()  # Вызываем функцию отправки сообщения при сохранении сообщения



admin.site.register(Participant, ParticipantAdmin)
admin.site.register(AuctionMessage, AuctionMessageAdmin)
