from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from registration.models import Participant

from .settings import TELEGRAM_TOKEN


# Состояния для ConversationHandler
ASK_NAME, ASK_PHONE = range(2)

# Начальная команда /start
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("""Assalomu alaykum! “ART VERNISSAGE” auksion uyiga xush kelibsiz! Itimos, o’zingizni F.I.O. kiriting

----------------
    
Добро пожаловать в аукционный дом «ART VERNISSAGE». Введите Ваши данные, пожалуйста (Ф.И.О.)""")
    return ASK_NAME

# Обработчик для получения ФИО
def ask_name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    # Создаём кнопку для отправки номера телефона
    contact_button = KeyboardButton("Поделиться номером телефона", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True)
    update.message.reply_text("""Aloqa uchun telefon raqamingizni kiriting
    
----------------

Введите номер телефона для обратной связи
""", reply_markup=reply_markup)
    return ASK_PHONE

# Обработчик для получения номера телефона
def ask_phone(update: Update, context: CallbackContext) -> int:
    contact = update.message.contact
    phone_number = contact.phone_number if contact else update.message.text
    name = context.user_data['name']
    chat_id = update.message.chat_id  # Сохраняем chat_id

    # Сохранение в базе данных
    Participant.objects.create(name=name, phone_number=phone_number, chat_id=chat_id)
    update.message.reply_text(f"""Siz {name} nomi bilan ART VERNISSAGE yopiq auksionida potentsial ishtirokchi sifatida ro'yxatdan o'tgansiz!\nTelefon raqamingiz: {phone_number}

----------------

Вы зарегистрированы в качестве потенциального участника закрытого аукциона ART VERNISSAGE, под именем {name}!\nВаш телефон номер: {phone_number}
""")

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