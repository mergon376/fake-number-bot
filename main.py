import telebot
import os

# ضع توكن البوت الخاص بك هنا من BotFather
TOKEN = "ضع_التوكن_هنا"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت الأرقام الوهمية! الخدمة تحت التطوير حالياً.")

if __name__ == "__main__":
    bot.infinity_polling()
