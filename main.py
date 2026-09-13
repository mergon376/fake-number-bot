import telebot
import os
from flask import Flask

# ⚠️ ضع توكن البوت الحقيقي الخاص بك من BotFather هنا بين علامات التنصيص
TOKEN = "123456789:ABCdefGhIJKlmNoPQR

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت الأرقام الوهمية! الخدمة تحت التطوير حالياً.")

@server.route('/')
def webhook():
    return "Bot is running!", 200

if __name__ == "__main__":
    import threading
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)
