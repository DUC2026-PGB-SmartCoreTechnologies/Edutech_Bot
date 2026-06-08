from threading import Thread
from flask import Flask

# បង្កើត Web Server ខ្លីមួយសម្រាប់ការពារកុំឱ្យ Render បិទ
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # ដំណើរការ Web Server លើ Port 10000 របស់ Render
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    # បង្កើត Thread ថ្មីមួយដើម្បីឱ្យ Flask រត់ទន្ទឹមគ្នាជាមួយ Bot
    t = Thread(target=run_flask)
    t.start()

# --- កូដ Bot របស់បងពីមុន ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "សូមស្វាគមន៍! Bot ដំណើរការ ២៤ ម៉ោងហើយបង។")

if __name__ == "__main__":
    print("Starting Flask Web Server...")
    keep_alive() # ហៅឱ្យ Web Server ដើរមុន
    
    print("Bot is running on Cloud...")
    bot.infinity_polling()