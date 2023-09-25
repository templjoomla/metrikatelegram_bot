import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urlparse, parse_qs


# Функция для отправки сообщения о переходе в телеграм канал
def send_to_channel(update, context):
    user = update.message.from_user
    # Извлекаем utm-метки из ссылки
    text = update.message.text
    parsed_url = urlparse(text)
    query_params = parse_qs(parsed_url.query)
    client_id = query_params.get('clientid', [''])[0]

    message = f"Пользователь {user.username} перешел в канал с utm-метками:\n"
    message += f"utm_source: {utm_source}\n"
    message += f"utm_medium: {utm_medium}\n"
    message += f"utm_campaign: {utm_campaign}\n"
    message += f"clientid: {client_id}"

    # Отправляем сообщение в чат
    context.bot.send_message(chat_id=CHAT_ID, text=message)

    # Добавляем информацию в Google Таблицу
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    # Открываем таблицу
    worksheet = client.open(GOOGLE_SHEET_NAME).sheet1

    # Добавляем информацию в таблицу
    row_data = [user.username, utm_source, utm_medium, utm_campaign, client_id]
    worksheet.append_row(row_data)

# Функция для обработки команды /start (если необходимо)
def start(update, context):
    update.message.reply_text('Привет! Этот бот отправляет информацию о переходе в телеграм канал.')

# Функция для обработки текстовых сообщений (если необходимо)
def text_message(update, context):
    text = update.message.text
    if text == 'Как дела?':
        update.message.reply_text('У меня всё хорошо, спасибо!')

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Добавляем обработчики команд и текстовых сообщений (если необходимо)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message))

    # Добавляем обработчик для отправки информации о переходе
    dp.add_handler(MessageHandler(Filters.text, send_to_channel), group=1)

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
