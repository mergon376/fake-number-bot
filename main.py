import telebot
import os

# التوكن الحقيقي الخاص ببوتك تم وضعه بنجاح
TOKEN = "8669917083:AAE3Zmnv-fIKo0QbIeXxGaloc_8H3_0Bctg"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت الأرقام الوهمية! الخدمة تحت التطوير حالياً.")

if __name__ == "__main__":
    print("البوت يعمل الآن بنجاح...")
    bot.infinity_polling()
