import os
import telebot

# មិនត្រូវដាក់ Token ផ្ទាល់នៅទីនេះទេ Render នឹងផ្តល់ឱ្យតាមក្រោយ
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello")

if __name__ == "__main__":
    print("Bot is running on Cloud...")
    bot.infinity_polling()