import asyncio
import io
from deep_translator import GoogleTranslator
from PIL import Image, ImageOps, ImageEnhance
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 1. دالة الترحيب عند إرسال /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "مرحباً بك في بوتك الثاني المطور والذكي! 🤖✨\n"
        "المطور بواسطة كريفيارد (Graveyard) ومنتجب.\n\n"
        "💬 يمكنك محاورتي والدردشة معي بلا حدود (كأنني جيمني تماماً).\n"
        "📝 أرسل أي نص بلغة أخرى لأقوم بترجمته فوراً إلى العربية.\n"
        "📸 أرسل أي صورة لتعديلها بشكل احترافي بضغطة زر!"
    )
    await update.message.reply_text(welcome_text)

# 2. الدالة الذكية لإدارة الحوار المفتوح والترجمة والتعرف على المطورين
async def handle_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_text_lower = user_text.lower()
    
    # التحقق من هوية المطور
    if any(word in user_text for word in ["مطور", "صانع", "برمج", "عملك", "من أنت"]) or "developer" in user_text_lower:
        await update.message.reply_text(
            "تم تصميمي وبرمجتي بالكامل بواسطة المطور العبقري **كريفيارد (Graveyard)** أو **منتجب** باستخدام لغة بايثون! 👨‍💻 البرمجة هي قوتي الحقيقية. 🚀"
        )
        return

    # شروط تبادل التحية والدردشة الشخصية (الحوار كأنه شخص حقيقي)
    greetings = {
        "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته! أهلاً بك يا صديقي المبدع. كيف حالك اليوم؟ 😊",
        "مرحبا": "أهلاً وسهلاً بك! سعيد جداً بالحديث معك ومحاورتك. كيف يمكنني مساعدتك؟ ✨",
        "كيف حالك": "أنا بوت ذكي بأفضل حال طالما أن كود بايثون الخاص بي مستقر ويعمل! 🤖 كيف حالك أنت؟",
        "شكرا": "العفو! هذا واجبي دائماً كصديق ومساعد ذكي برمجته بأيدي كريفيارد ومنتجب. 🌹"
    }
    
    for key, response in greetings.items():
        if key in user_text:
            await update.message.reply_text(response)
            return

    # إذا لم يكن الكلام تحية أو سؤال عن المطور، وكان باللغة العربية أو عبارة عن سؤال حواري
    is_arabic = any("\u0600" <= char <= "\u06FF" for char in user_text)
    if is_arabic or len(user_text.split()) < 4 or "كيف" in user_text or "هل" in user_text:
        await update.message.reply_text(
            f"أنا أفهمك تماماً وأسمعك جيداً! 🧠 بصفتي بوت ذكي برمجني كريفيارد ومنتجب، أنا جاهز لأي حوار مستمر أو نقاش تطلبه معي!"
        )
        return

    # إذا أرسل نصاً إنجليزياً أو بلغة أخرى، يعتبره البوت تلقائياً نصاً مخصصاً للترجمة
    waiting_message = await update.message.reply_text("جاري التحليل والترجمة الذكية... ⏳")
    try:
        translated_result = GoogleTranslator(source='auto', target='ar').translate(user_text)
        await waiting_message.edit_text(f"ترجمة النص الاحترافية: 👇\n\n{translated_result}")
    except Exception as e:
        await waiting_message.edit_text("عذراً، حدث خطأ أثناء الاتصال بالخادم. يرجى التأكد من تشغيل الـ VPN طالما أننا نعمل من الهاتف.")

# 3. استقبال الصور ومعالجتها بلا حدود
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    context.user_data['photo_file_id'] = photo_file.file_id
    
    keyboard = [
        [InlineKeyboardButton("🤍 أبيض وأسود", callback_data="filter_bw"),
         InlineKeyboardButton("🎨 ألوان مشبعة", callback_data="filter_bright")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("وصلتني الصورة بنجاح! اختر الفلتر الاحترافي المفضل لديك: 👇", reply_markup=reply_markup)

# دالة معالجة أزرار الصور والتأثيرات الاحترافية
async def handle_filter_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("جاري التعديل... ⏳")
    file_id = context.user_data.get('photo_file_id')
    if not file_id: return
    file = await context.bot.get_file(file_id)
    photo_bytes = await file.download_as_bytearray()
    img = Image.open(io.BytesIO(photo_bytes))
    
    if query.data == "filter_bw": 
        img = ImageOps.grayscale(img)
    elif query.data == "filter_bright": 
        img = ImageEnhance.Color(img).enhance(2.5)

    output_bytes = io.BytesIO()
    img.save(output_bytes, format='JPEG')
    output_bytes.seek(0)
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=output_bytes, caption="تم تعديل صورتك بنجاح بواسطة بايثون! ✨📸")

# 4. تشغيل وإدارة البوت
def main():
    # 🌟 التوكن الجديد مدمج وجاهز هنا بشكل كامل
    TOKEN = "7849697811:AAEaiTfdYcfYM4lNPv0-sb3Z2wsJgcmkFgY"
    
    app = Application.builder().token(TOKEN).build()
    
    # ربط جميع أنواع الرسائل بالدوال البرمجية المخصصة لها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_filter_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_conversation))
    
    print("البوت الثاني (المحاور والمترجم الشامل) يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    try:
        asyncio.get_running_loop()
        import nest_asyncio
        nest_asyncio.apply()
    except RuntimeError:
        pass
    main()
          
