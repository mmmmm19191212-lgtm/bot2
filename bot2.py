import json
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

DATA_FILE = "banned_media.json"
DISABLED_FILE = "disabled.flag"  # فایل برای حالت خاموش

# بارگذاری لیست از فایل
def load_banned():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"photos": [], "gifs": [], "stickers": []}

# ذخیره در فایل
def save_banned(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

banned = load_banned()

# بررسی فعال یا غیرفعال بودن ربات
def is_disabled():
    try:
        with open(DISABLED_FILE, "r") as f:
            return f.read().strip() == "1"
    except:
        return False

def disable_bot():
    with open(DISABLED_FILE, "w") as f:
        f.write("1")

def enable_bot():
    with open(DISABLED_FILE, "w") as f:
        f.write("0")

# افزودن فایل ممنوعه در چت خصوصی
async def add_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_disabled():
        return

    added = False
    msg = update.message

    if msg.photo:
        file_id = msg.photo[-1].file_id
        if file_id not in banned["photos"]:
            banned["photos"].append(file_id)
            added = True

    elif msg.animation:
        file_id = msg.animation.file_id
        if file_id not in banned["gifs"]:
            banned["gifs"].append(file_id)
            added = True

    elif msg.sticker:
        file_id = msg.sticker.file_id
        if file_id not in banned["stickers"]:
            banned["stickers"].append(file_id)
            added = True

    elif msg.text and msg.text.strip() == "1361649093":
        disable_bot()
        await msg.reply_text("🚫 ربات غیرفعال شد. برای فعال‌سازی دوباره باید از VS Code اجراش کنی.")
        sys.exit(0)  # پایان کامل اجرای برنامه

    if added:
        save_banned(banned)
        await msg.reply_text("✅ به لیست ممنوعه اضافه شد.")
    elif not msg.text:
        await msg.reply_text("❌ لطفاً عکس، گیف یا استیکر بفرست یا بنویس 'خاموش شو' برای خاموش کردن ربات.")

# بررسی پیام‌ها در گروه
async def check_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_disabled():
        return

    msg = update.message

    # بررسی عکس
    if msg.photo:
        file_id = msg.photo[-1].file_id
        if file_id in banned["photos"]:
            await msg.delete()
            await msg.reply_text("⚠️ این عکس در گروه ممنوع است.", reply_to_message_id=msg.message_id)
            print(f"🚫 عکس ممنوعه حذف شد: {file_id}")
            return

    # بررسی گیف
    if msg.animation:
        file_id = msg.animation.file_id
        if file_id in banned["gifs"]:
            await msg.delete()
            await msg.reply_text("⚠️ این گیف در گروه ممنوع است.", reply_to_message_id=msg.message_id)
            print(f"🚫 گیف ممنوعه حذف شد: {file_id}")
            return

    # بررسی استیکر
    if msg.sticker:
        file_id = msg.sticker.file_id
        if file_id in banned["stickers"]:
            await msg.delete()
            await msg.reply_text("⚠️ این استیکر در گروه ممنوع است.", reply_to_message_id=msg.message_id)
            print(f"🚫 استیکر ممنوعه حذف شد: {file_id}")
            return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    enable_bot()
    await update.message.reply_text(
        "سلام 👋\n"
        "من فعال شدم.\n"
        "عکس، گیف یا استیکر بفرست تا در لیست ممنوعه ذخیره کنم.\n"
        "برای خاموش کردن ربات بنویس: «خاموش شو»"
    )

def main():
    TOKEN = "8389911993:AAGukw5C636cbEm5TmkttzCQ42SKJt3qSog"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.ANIMATION | filters.Sticker.ALL | filters.TEXT) & filters.ChatType.PRIVATE,
        add_media
    ))
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.ANIMATION | filters.Sticker.ALL) & filters.ChatType.GROUPS,
        check_messages
    ))

    print("🤖 ربات فعال است...")
    app.run_polling()

if __name__ == "__main__":
    main()
