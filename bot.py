import telebot
from rembg import remove
import io
from PIL import Image
import os
from flask import Flask
import threading
import time

# ТВОЙ ТОКЕН
TOKEN = '8434433794:AAHmpoHbK9FE592lM9MopgOpjKh3s9yK_mo'
bot = telebot.TeleBot(TOKEN)

# Создаём Flask приложение — оно нужно, чтобы Render не ругался
app = Flask(name)

@app.route('/')
def index():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

# Функция запуска бота в отдельном потоке
def run_bot():
    print("🤖 Бот запущен и готов к работе...")
    bot.polling()

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        "👋 Привет! Отправь мне фото, и я удалю водяные знаки/фон.\n\n"
        "📸 *Как отправить:*\n"
        "— как фото (Telegram сожмёт)\n"
        "— как файл (оригинальное качество)\n\n"
        "👇 Просто отправь изображение!",
        parse_mode='Markdown'
    )

# Обработка фото
@bot.message_handler(content_types=['photo', 'document'])
def handle_photo(message):
    try:
        msg = bot.reply_to(message, "🔄 Обрабатываю... это займёт несколько секунд")
        
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            is_photo = True
        else:
            file_id = message.document.file_id
            is_photo = False
        
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        result_bytes = remove(downloaded_file)
        
        if is_photo:
            bot.send_photo(
                message.chat.id, 
                result_bytes,
                caption="✅ Готово! Водяные знаки удалены"
            )
        else:
            bot.send_document(
                message.chat.id,
                ('cleaned.png', result_bytes),
                caption="✅ Готово! Водяные знаки удалены"
            )
        
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}\n\nПопробуй другое фото или отправь как файл.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.reply_to(message, "Отправь мне фото, а не текст 😊")

# Запуск
if name == 'main':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask-сервер (обязательно для Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
