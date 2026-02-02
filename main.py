import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import random
import os

# Render/GitHub မှာ Token လုံခြုံစေရန် Environment Variable သုံးထားသည်
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ပါးရိုက်တဲ့ Sticker ID များ (Unicode ပျောက်မှာစိုးလို့ Code ဖြင့်ရေးသည်)
SLAP_STICKERS = [
    'CAACAgIAAxkBAAEQZulpgFZFlmZaaa1ztgoSNLFhMtsTIAACIQADDbbSGZ9iP3-ywRAcOAQ',
    'CAACAgIAAxkBAAEQZutpgFaWsSfAaOmNJOuIn1pTQlERowACLQADDbbSGVMtxqHEkftyOAQ'
]

# Database Setup
def init_db():
    conn = sqlite3.connect('slap_master.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats 
                 (username TEXT PRIMARY KEY, count INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def add_slap_count(username):
    conn = sqlite3.connect('slap_master.db')
    c = conn.cursor()
    username = username.lower().replace('@', '')
    c.execute('INSERT OR IGNORE INTO stats (username, count) VALUES (?, 0)', (username,))
    c.execute('UPDATE stats SET count = count + 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def get_slap_count(username):
    conn = sqlite3.connect('slap_master.db')
    c = conn.cursor()
    username = username.lower().replace('@', '')
    c.execute('SELECT count FROM stats WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

init_db()

# Start Command & Button
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # Emoji Unicode: \U0001F449 = 
    btn_text = "ပါးရိုက်ချက်များ ကြည့်ရန် \U0001F449 (နှိပ်ပါ)"
    markup.add(KeyboardButton(btn_text))
    bot.send_message(message.chat.id, "Bot အသင့်ဖြစ်ပါပြီ! \U0001F44B\n\nပုံပို့တဲ့အခါ Caption မှာ Username ရေးပေးရင် ပါးရိုက်ပေးမှာနော်။", reply_markup=markup)

# Photo Handler
@bot.message_handler(content_types=['photo'])
def handle_slap_photo(message):
    if message.caption:
        slapper_name = message.from_user.first_name
        victim_username = message.caption.strip()
        
        add_slap_count(victim_username)
        total_slaps = get_slap_count(victim_username)
        
        sticker = random.choice(SLAP_STICKERS)
        bot.send_sticker(message.chat.id, sticker)
        
        display_name = victim_username if victim_username.startswith('@') else f"@{victim_username}"
        # Unicode: \U0001F4A5 = , \U0001F915 = 
        response = (f"\U0001F4A5 **ဖြောင်း!!!**\n\n"
                    f"{slapper_name} က {display_name} ကို ပါးရိုက်လိုက်သည်။\n\n"
                    f"\U0001F915 {display_name} အရိုက်ခံရတာ စုစုပေါင်း ({total_slaps}) ချက်ရှိပြီ!")
        
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        bot.reply_to(message, "ဘယ်သူ့ကို ရိုက်မှာလဲ? Caption မှာ Username ရေးပေးပါ။")

# Stats Button Handler
@bot.message_handler(func=lambda message: "ပါးရိုက်ချက်များ ကြည့်ရန်" in message.text)
def show_my_stats(message):
    user = message.from_user
    # Username မရှိရင် နာမည်နဲ့ ရှာမယ်
    my_uname = user.username if user.username else user.first_name
    count = get_slap_count(my_uname)
    bot.reply_to(message, f"\U0001F464 {user.first_name} \n\U0001F44B မင်းက စုစုပေါင်း {count} ချက် အရိုက်ခံထားရတယ်။")

# Bot ကို အမြဲ Run ထားစေမည့် Polling
print("Bot is starting...")
bot.infinity_polling()
