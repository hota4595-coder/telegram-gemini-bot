import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# --- 1. ضع مفاتيحك السرية هنا ---
TELEGRAM_TOKEN = "8618697567:AAE9O8brmvGa-jzp9msuXI1YxnGUnYj4z2s"
GOOGLE_API_KEY = "AIzaSyBOjxXLx_hgciJqrf7aYs3ll2k01qN9QSo"

# --- 2. إعدادات أساسية ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# إعداد نموذج الذكاء الاصطناعي (Gemini)
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # --- التعديل الأهم: استخدام اسم النموذج الجديد ---
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("تم إعداد نموذج Gemini بنجاح.")
except Exception as e:
    logger.error(f"فشل إعداد نموذج Gemini: {e}")
    model = None

# --- 3. دوال البوت ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ترسل رسالة ترحيب عند إرسال أمر /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"أهلاً بك يا {user.mention_html()}! أنا بوت ذكاء اصطناعي. أرسل لي أي سؤال وسأحاول الإجابة.",
    )

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تعالج الرسائل النصية (الأسئلة) وترد عليها باستخدام Gemini."""
    if not model:
        await update.message.reply_text("عذرًا، خدمة الذكاء الاصطناعي غير متاحة حاليًا بسبب مشكلة في الإعداد.")
        return

    question_text = update.message.text
    logger.info(f"تم استلام سؤال: {question_text}")

    try:
        # إرسال رسالة "أفكر" للمستخدم
        thinking_message = await update.message.reply_text("لحظة، أفكر في إجابة...")
        
        # توليد الإجابة من Gemini
        response = model.generate_content(question_text)
        
        # تعديل رسالة "أفكر" إلى الإجابة النهائية
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_message.message_id,
            text=response.text
        )
        logger.info("تم إرسال الرد بنجاح.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء معالجة السؤال: {e}")
        await update.message.reply_text("عذرًا، حدث خطأ أثناء محاولة الإجابة على سؤالك.")

def main() -> None:
    """الدالة الرئيسية التي تقوم بتشغيل البوت."""
    logger.info("بدء تشغيل البوت...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # إضافة معالجات الأوامر والرسائل
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    logger.info("البوت بدأ في استقبال الرسائل...")
    application.run_polling()

# --- 4. نقطة انطلاق البرنامج ---
if __name__ == "__main__":
    main()
