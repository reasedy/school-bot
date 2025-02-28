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
        {"subject": "Math", "start": time(10, 15), "end": time(17, 10), "room": "223"},
        {"subject": "check", "start": time(17, 12), "end": time(17, 17), "room": "223"},
    ],
}

updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher


def daily_notify(context: CallbackContext):
    today = datetime.now(TIMEZONE).strftime("%A")

    if today in SCHEDULE and len(SCHEDULE[today]) > 0:
        first_lesson = SCHEDULE[today][0]
        message = (
            f"Доброе утро! 🌞\n"
            f"Сегодня первый урок:\n"
            f"🔔 {first_lesson['subject']}\n"
            f"🚪 Кабинет: {first_lesson['room']}\n"
            f"⏰ Начало: {first_lesson['start'].strftime('%H:%M')}"
        )
        context.bot.send_message(chat_id=context.job.context, text=message)


def notify(context: CallbackContext):
    now = datetime.now(TIMEZONE).time()
    today = datetime.now(TIMEZONE).strftime("%A")

    if today not in SCHEDULE:
        return

    for index, lesson in enumerate(SCHEDULE[today]):
        if lesson["end"] == now:
            next_lesson = SCHEDULE[today][index + 1] if index + 1 < len(SCHEDULE[today]) else None
            if next_lesson:
                message = (
                    f"✅ Урок завершён: {lesson['subject']}\n"
                    f"Следующий урок:\n"
                    f"🔔 {next_lesson['subject']}\n"
                    f"🚪 Кабинет: {next_lesson['room']}\n"
                    f"⏰ Начало: {next_lesson['start'].strftime('%H:%M')}"
                )
                context.bot.send_message(chat_id=context.job.context, text=message)


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.job_queue.run_daily(daily_notify, time(8, 0), context=chat_id)
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