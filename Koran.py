import telebot
import requests
import random
import time
import logging
import os
from dotenv import load_dotenv

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logger.error("❌ BOT_TOKEN غير موجود في ملف .env")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# ================= start =================
@bot.message_handler(commands=["start"])
def start(message):
    logger.info(f"مستخدم جديد: {message.from_user.id}")
    bot.send_message(
        message.chat.id,
        "🌙 مرحبًا بك في بوت القرآن والسنة\n\n"
        "📖 أرسل رقم صفحة (1 – 604) لعرض صفحة من المصحف\n\n"
        "🕋 أرسل الأمر:\n"
        "/hadith\n"
        "للحصول على حديث نبوي عشوائي"
    )

# ================= hadith =================
@bot.message_handler(commands=["hadith"])
def send_hadith(message):
    try:
        # اختيار كتاب حديث عشوائي
        books = ["bukhari", "muslim", "abudawud", "tirmidzi", "nasai", "ibnumajah"]
        book = random.choice(books)

        # نطاق محدود لتقليل الأخطاء
        url = f"https://api.hadith.gading.dev/books/{book}?range=1-300"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # تحقق من البنية
        if "data" not in data or "hadiths" not in data["data"]:
            raise ValueError("Invalid hadith API response")

        hadiths = data["data"]["hadiths"]
        hadith = random.choice(hadiths)

        text = (
            f"🕋 حديث نبوي\n"
            f"📚 المصدر: {data['data'].get('name', 'غير معروف')}\n\n"
            f"{hadith.get('arab', 'نص الحديث غير متوفر')}"
        )

        bot.send_message(message.chat.id, text)
        logger.info(f"تم إرسال حديث من {book} للمستخدم {message.from_user.id}")

    except Exception as e:
        logger.error(f"خطأ في جلب الحديث: {e}")
        bot.send_message(
            message.chat.id,
            "⚠️ تعذر جلب حديث حاليًا، حاول مرة أخرى لاحقًا"
        )

# ================= pages =================
@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def send_page(message):
    page = int(message.text)

    if not 1 <= page <= 604:
        bot.reply_to(message, "❌ رقم الصفحة يجب أن يكون بين 1 و 604")
        return

    img_url = f"https://quran.ksu.edu.sa/png_big/{page}.png"

    try:
        img = requests.get(img_url, timeout=10)
        img.raise_for_status()

        bot.send_photo(
            message.chat.id,
            img.content,
            caption=f"📖 صفحة رقم {page}"
        )
        logger.info(f"تم إرسال صفحة {page} للمستخدم {message.from_user.id}")

    except Exception as e:
        logger.error(f"خطأ في جلب الصفحة {page}: {e}")
        bot.reply_to(message, "⚠️ حدث خطأ أثناء جلب الصفحة")

# ================= fallback =================
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ أرسل رقم صفحة أو استخدم /hadith"
    )

# ================= run =================
if __name__ == "__main__":
    logger.info("🚀 البوت يعمل الآن...")
    while True:
        try:
            bot.polling(skip_pending=True)
        except Exception as e:
            logger.error(f"خطأ في الاتصال: {e}")
            time.sleep(5)
