import telebot
import os
import sqlite3
import random
from flask import Flask
from threading import Thread

# ၁။ Render ရဲ့ Port Error ကို ရှင်းဖို့ Flask Setup လုပ်ခြင်း
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render က ပေးတဲ့ PORT ကို ဖတ်မယ်၊ မရှိရင် 10000 သုံးမယ်
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ၂။ Bot Setup
TOKEN = os.getenv('BOT_TOKEN') # Render Environment Variable ထဲမှာ ထည့်ရမည့်အမည်
bot = telebot.TeleBot(TOKEN)

SLAP_STICKERS = [
    'CAACAgIAAxkBAAEQZulpgFZFlmZaaa1ztgoSNLFhMtsTIAACIQADDbbSGZ9iP3-ywRAcOAQ',
    'CAACAgIAAxkBAAEQZutpgFaWsSfAaOmNJOuIn1pTQlERowACLQADDbbSGVMtxqHEkftyOAQ'
]

def init_db():
    conn = sqlite3.connect('slap_master.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS stats (username TEXT PRIMARY KEY, count INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

def add_slap_count(username):
    conn = sqlite3.connect('slap_master.db', check_same_thread=False)
    c = conn.cursor()
    username = username.lower().replace('@', '')
    c.execute('INSERT OR IGNORE INTO stats (username, count) VALUES (?, 0)', (username,))
    c.execute('UPDATE stats SET count = count + 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def get_slap_count(username):
    conn = sqlite3.connect('slap_master.db', check_same_thread=False)
    c = conn.cursor()
    username = username.lower().replace('@', '')
    c.execute('SELECT count FROM stats WHERE username = ?', (username,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else 0

init_db()

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Group ထဲမှာ ပုံနဲ့ Username တွဲပို့ပြီး ပါးရိုက်လို့ရပါပြီ!")

@bot.message_handler(content_types=['photo'])
def handle_slap_photo(message):
    if message.caption:
        slapper = message.from_user.first_name
        victim = message.caption.strip()
        add_slap_count(victim)
        count = get_slap_count(victim)
        bot.send_sticker(message.chat.id, random.choice(SLAP_STICKERS))
        bot.send_message(message.chat.id, f" **ဖြောင်း!!!**\n\n{slapper} က {victim} ကို ရိုက်လိုက်ပြီ!\n\n စုစုပေါင်း: {count} ချက်ရှိပြီ။", parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive() # Port ကို ဖွင့်ပေးရန်
    print("Bot is starting...")
    bot.infinity_polling()
