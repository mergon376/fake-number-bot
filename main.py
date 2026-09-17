import telebot
import requests
import time
from threading import Thread
import os

# 1. توكن البوت الخاص بك من BotFather
TELEGRAM_TOKEN = '8932968608:AAHHXeegMilCmDEc8ndzkF3e-V3BX4i4N1k'

# 2. رمز الـ API الثابت الخاص بك من موقع Ringbeta
RINGBETA_API_TOKEN = '8f32d791099f39e86bb44785132f7a73'

# الرابط الأساسي الرسمي المستخرج من خوادم الإنتاج لمنع الحظر
BASE_URL = "https://ringbeta.com"


bot = telebot.TeleBot(TELEGRAM_TOKEN)

# إعداد سيرفر ويب وهمي لمنع توقف منصة Render المجانية
from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح على منصة Render!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def get_jwt_token():
    url = f"{BASE_URL}/api/v1/auth/token"
    payload = {"api_token": RINGBETA_API_TOKEN}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        return None
    except Exception:
        return None

def get_us_supplier_id(jwt_token):
    url = f"{BASE_URL}/api/v1/phone/options"
    headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            options = response.json()
            for option in options:
                if option.get("countrycode", "").lower() == "us" and option.get("stock", 0) > 0:
                    return option.get("supplierId")
            for option in options:
                if option.get("countrycode", "").lower() == "us":
                    return option.get("supplierId")
        return "default_supplier"
    except Exception:
        return "default_supplier"

def check_for_sms(jwt_token, order_id, chat_id):
    sms_url = f"{BASE_URL}/api/v1/phone/sms" 
    headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/json"}
    params = {"orderId": order_id}
    
    bot.send_message(chat_id, "⏳ بدأ مؤقت البوت (مدته دقيقتان).. أرسل كود التحقق إلى الرقم الآن وسأعرضه لك فور وصوله هنا.")
    
    for _ in range(24):
        time.sleep(5)
        try:
            response = requests.get(sms_url, headers=headers, params=params)
            if response.status_code == 200:
                sms_data = response.json()
                if sms_data and (sms_data.get("sms") or sms_data.get("code")):
                    sms_text = sms_data.get("sms") or sms_data.get("text")
                    verification_code = sms_data.get("code") or sms_data.get("verification_code")
                    
                    alert_text = (
                        f"📩 **وصلت رسالة نصية جديدة!**\n\n"
                        f"💬 **محتوى الرسالة:**\n`{sms_text}`\n\n"
                        f"🔑 **كود التفعيل المستخرج:** `{verification_code}`"
                    )
                    bot.send_message(chat_id, alert_text, parse_mode="Markdown")
                    return 
        except Exception:
            pass
            
    bot.send_message(chat_id, "⚠️ انتهت مهلة الانتظار (دقيقتان) ولم يصل أي كود.")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "أهلاً بك في بوت الأرقام الأمريكية المطور! 🇺🇸📩\n\n"
        "لطلب واستئجار رقم أمريكي وبدء استقبال الأكواد، أرسل الأمر:\n"
        "➡️ /get_number"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['get_number'])
def rent_us_number(message):
    status_msg = bot.reply_to(message, "⏳ جاري توليد رمز المصادقة الفني JWT والاتصال بخوادم الإنتاج الرسمية...")
    
    jwt_token = get_jwt_token()
    if not jwt_token:
        bot.edit_message_text("❌ فشلت عملية المصادقة الفنية وتوليد الـ JWT مع سيرفر Ringbeta الرئيسي.", message.chat.id, status_msg.message_id)
        return

    bot.edit_message_text("⏳ جاري البحث عن المورد المتاح وتأكيد المخزون لـ 🇺🇸...", message.chat.id, status_msg.message_id)
    supplier_id = get_us_supplier_id(jwt_token)
    
    bot.edit_message_text("⏳ جاري استئجار الرقم الأمريكي الآن وإصدار العقد التلقائي...", message.chat.id, status_msg.message_id)
    rent_url = f"{BASE_URL}/api/v1/phone/rent"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "countrycode": "us",
        "supplierId": supplier_id,
        "period": 7,
        "reused": False,
        "count": 1
    }
    
    try:
        response = requests.post(rent_url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            phone = data.get("phone_number") or data.get("number") or data.get("phone")
            order_id = data.get("orderId") or data.get("id")
            
            success_text = (
                f"🎉 **تم حجز الرقم الأمريكي بنظام التأجير!**\n\n"
                f"🇺🇸 **الرقم الحركي:** `{phone}`\n"
                f"📋 **رقم الطلب (Order ID):** `{order_id}`\n"
                f"📅 **مدة الصلاحية:** 7 أيام\n\n"
                f"استخدم الرقم الآن في المنصة التي تريد تفعيلها..."
            )
            bot.edit_message_text(success_text, message.chat.id, status_msg.message_id, parse_mode="Markdown")
            check_for_sms(jwt_token, order_id, message.chat.id)
        else:
            bot.edit_message_text(f"❌ فشل حجز الرقم المباشر.\nرمز حالة السيرفر: {response.status_code}\nالتفاصيل: {response.text}", message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ تقني غير متوقع: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    # تشغيل سيرفر ويب لضمان استقرار البوت على المنصات السحابية المجانية مثل Render
    t = Thread(target=run_web_server)
    t.start()
    
    print("البوت يعمل بكامل صلاحياته البرمجية المحدثة الآن...")
    bot.infinity_polling()
    
