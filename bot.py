import os
import logging
from datetime import datetime, time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

import pytz
from flask import Flask, request
import threading

app = Flask(__name__)

TOKEN = "7917769229:AAHrqDzs9c64KRcHpNXLJZ0V6GMpLTjsZz0"
TIMEZONE = pytz.timezone("Asia/Oral")

SCHEDULE = {
    "Monday": [
        {"subject": "Physics", "start": time(8, 30), "end": time(10, 10), "room": "353"},
        {"subject": "Math", "start": time(10, 15), "end": time(11, 40), "room": "223"},
        {"subject": "ICT", "start": time(11, 50), "end": time(13, 40), "room": "253"},
        {"subject": "Mathcie", "start": time(13, 50), "end": time(15, 15), "room": "223"},
    ],
    "Tuesday": [
        {"subject": "Math", "start": time(8, 30), "end": time(10, 10), "room": "223"},
        {"subject": "Kazakh Lang & Lit", "start": time(10, 15), "end": time(11, 40), "room": "351"},
        {"subject": "Physics", "start": time(11, 50), "end": time(13, 40), "room": "133"},
        {"subject": "ICT", "start": time(13, 50), "end": time(15, 15), "room": "255"},
    ],
    "Wednesday": [
        {"subject": "Math", "start": time(8, 30), "end": time(10, 10), "room": "223"},
        {"subject": "Physics", "start": time(10, 15), "end": time(11, 40), "room": "256"},
        {"subject": "KSM", "start": time(11, 50), "end": time(13, 40), "room": "324"},
        {"subject": "nvp,curator", "start": time(13, 50), "end": time(15, 15), "room": "324,304"},
        {"subject": "ICT", "start": time(15, 35), "end": time(17, 0), "room": "255"},
    ],
    "Thursday": [
        {"subject": "Math", "start": time(8, 30), "end": time(10, 10), "room": "223"},
        {"subject": "musorka_CIE", "start": time(10, 15), "end": time(11, 40), "room": "255"},
        {"subject": "Physra", "start": time(11, 50), "end": time(13, 40), "room": "ozinbilesin"},
        {"subject": "Programming", "start": time(13, 50), "end": time(15, 15), "room": "257"},
        {"subject": "CIE_Phys", "start": time(15, 35), "end": time(17, 0), "room": "223"},
    ],
    "Friday": [
        {"subject": "cie_ksm/kaz", "start": time(8, 30), "end": time(10, 10), "room": "351"},
        {"subject": "Math", "start": time(10, 15), "end": time(11, 40), "room": "223"},
    ],
}


updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher



def notify(context: CallbackContext):
    now = datetime.now(TIMEZONE).time()
    today = datetime.now(TIMEZONE).strftime("%A")

    if today not in SCHEDULE:
        return

    for lesson in SCHEDULE[today]:
        if lesson["start"] == now:
            message = (
                f"🔔 Урок: {lesson['subject']}\n"
                f"🚪 Кабинет: {lesson['room']}\n"
                f"⏰ Начало: {lesson['start'].strftime('%H:%M')}"
            )
            context.bot.send_message(chat_id=context.job.context, text=message)


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.job_queue.run_repeating(notify, interval=60, first=0, context=chat_id)
    update.message.reply_text("✅ Вы подписаны на уведомления!")


@app.route("/")
def index():
    return "Bot is alive!", 200


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    print("Update:", request.get_json())
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "OK", 200


dispatcher.add_handler(CommandHandler("start", start))


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook(f"https://one2a-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=PORT)