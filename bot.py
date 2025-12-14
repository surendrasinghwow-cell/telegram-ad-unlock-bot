from telebot import TeleBot, types
import time, random

BOT_TOKEN = "${{shared.8510803619:AAG4blR0lD1A9cW2LCgyi73iE3A3V0t4U7E}}"
GROUP_ID = -1002291113941
ADMIN_IDS = [7408733118]

SMARTLINKS = [
    "https://www.effectivegatecpm.com/kw0dj9s6wv?key=068a6b2e068d4306b47a2a1d3f0691ab"
]

bot = TeleBot(BOT_TOKEN, threaded=True)

video_db = {}
pending = {}
cooldown = {}
video_counter = 100

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "✅ Bot activated. Go back to group.")

@bot.message_handler(content_types=['video'])
def video_handler(msg):
    global video_counter
    if msg.chat.id != GROUP_ID: return
    if msg.from_user.id not in ADMIN_IDS: return

    video_counter += 1
    vid = f"V{video_counter}"
    video_db[vid] = msg.video.file_id

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔓 Unlock Video", callback_data=f"unlock_{vid}"))

    bot.reply_to(msg, f"🔞 Video Locked\nID: {vid}", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("unlock_"))
def unlock(c):
    uid = c.from_user.id
    vid = c.data.split("_")[1]
    key = (uid, vid)

    if key in cooldown and time.time() - cooldown[key] < 30:
        bot.answer_callback_query(c.id, "⏳ Wait", show_alert=True)
        return

    cooldown[key] = time.time()
    pending[uid] = (vid, time.time())

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔓 Continue", url=random.choice(SMARTLINKS)))
    kb.add(types.InlineKeyboardButton("✅ I Completed", callback_data="check"))

    bot.send_message(uid, f"Unlock video {vid}", reply_markup=kb)
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(c):
    uid = c.from_user.id
    if uid not in pending:
        bot.answer_callback_query(c.id, "❌ No request", show_alert=True)
        return

    vid, start = pending[uid]
    if time.time() - start < 15:
        bot.answer_callback_query(c.id, "⏳ Complete properly", show_alert=True)
        return

    if vid not in video_db:
        bot.send_message(uid, "❌ Video expired")
        return

    bot.send_video(uid, video_db[vid], caption=f"🔥 Unlocked {vid}")
    del pending[uid]
    bot.answer_callback_query(c.id)

bot.infinity_polling(skip_pending=True)
