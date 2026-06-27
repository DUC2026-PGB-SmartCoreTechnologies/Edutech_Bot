import telebot
from config import supabase, TELEGRAM_TOKEN

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def force_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    print(f"🚀 [FOUND IT] ចាប់បានសារហើយ! ID របស់បងគឺ: {user_id}")
    
    try:
        # 🔥 បង្ខំញាត់ចូលតារាង admins ភ្លាមៗ
        supabase.table("admins").upsert({"telegram_id": user_id, "role": "SUPER_ADMIN"}).execute()
        supabase.table("users").upsert({"telegram_id": user_id, "role": "SUPER_ADMIN", "status": "APPROVED", "language": "km"}).execute()
        
        print("✅ [SUPABASE] បញ្ចូល ID ទៅ Supabase រួចរាល់!")
        bot.send_message(chat_id, "🔥 [មហាសំរេច] កូដថ្មីបានបង្ខំបញ្ចូល ID បងទៅ Supabase ជោគជ័យហើយ!")
    except Exception as e:
        print(f"❌ Error: {e}")
        bot.send_message(chat_id, f"❌ ទាក់បញ្ហា Supabase: {e}")

if __name__ == "__main__":
    print("🛰️ Bot ថ្មី (test_force) កំពុងឈររង់ចាំស្ដាប់សារ...")
    bot.infinity_polling()