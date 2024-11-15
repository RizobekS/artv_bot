import os

from django.conf import settings
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from registration.models import Participant

from .settings import TELEGRAM_TOKEN

# Состояния для ConversationHandler
ASK_NAME, ASK_PHONE = range(2)
# Пути к файлам и константы
PHOTO_PATH = os.path.join(settings.BASE_DIR, "artv_gallery.jpg")  # Путь к фото, которое вы загрузили
MAP_LINK = "https://yandex.com/maps/?whatshere%5Bzoom%5D=16&whatshere%5Bpoint%5D=69.248458,41.279456&si=b4wud2ud6tgn511fur4k6qb8hr"


# Начальная команда /start
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        """Assalomu alaykum! “ART VERNISSAGE” auksion uyiga xush kelibsiz! Itimos, o’zingizni F.I.O. kiriting\n\n----------------\n\nДобро пожаловать в аукционный дом «ART VERNISSAGE». Введите Ваши данные, пожалуйста (Ф.И.О.)""")
    return ASK_NAME


# Обработчик для получения ФИО
def ask_name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    # Создаём кнопку для отправки номера телефона
    contact_button = KeyboardButton("Поделиться номером телефона", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True)
    update.message.reply_text(
        """Aloqa uchun telefon raqamingizni kiriting\n\n----------------\n\nВведите номер телефона для обратной связи""",
        reply_markup=reply_markup)
    return ASK_PHONE


# Обработчик для получения номера телефона
def ask_phone(update: Update, context: CallbackContext) -> int:
    contact = update.message.contact
    phone_number = contact.phone_number if contact else update.message.text
    name = context.user_data['name']
    chat_id = update.message.chat_id  # Сохраняем chat_id

    # Сохранение в базе данных
    Participant.objects.create(name=name, phone_number=phone_number, chat_id=chat_id)

    # Текст сообщения
    message_text = f"""
    Siz {name} ismi bilan "O'zbekiston tasviriy san'atining arboblari" yopiq auksionida potentsial ishtirokchi sifatida ro'yxatdan o'tgansiz!\n
    Telefon raqamingiz: {phone_number}\n
    Auksionga qo'yilgan lotlar bilan ART GALLERY galereyamizda quyidagi manzil bo'yicha tanishish mumkin: Toshkent sh, Muqimiy ko'chasi, 1 prospekt, 8-a y.\n
    Murojaat uchun telefon\n+998555141212\n+998555151707\n
    [Xarita uchun havola]({MAP_LINK})\n\n
    -----------------\n\n
    Вы зарегистрированы в качестве потенциального участника закрытого аукциона "Корифеи живописи Узбекистана", под именем {name}!\n
    Ваш телефон номер: {phone_number}\n
    Ознакомиться с выставленными на аукцион лотами можно в нашей галерее Art gallery по адресу: г. Ташкент, ул. Мукимий, проспект 1, дом 8-а\n
    Телефон для связи +998555141212\n+998555151707\n
    [Ссылка на карту]({MAP_LINK})
    """

    # Отправляем фото с подписью
    with open(PHOTO_PATH, "rb") as photo:
        update.message.reply_photo(photo=photo, caption=message_text, parse_mode='Markdown')

    return ConversationHandler.END


# Функция завершения
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END


# Главная функция
def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Добавляем ConversationHandler для поэтапной регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
            ASK_PHONE: [MessageHandler(Filters.contact | Filters.text, ask_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
