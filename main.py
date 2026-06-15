import telebot
from telebot import types
from datetime import datetime
import threading
import time
import os
import logging

from config import supabase 

# បង្ខំឱ្យវាទៅអូសទាញយក Key ពីផ្ទាំង Environment Variables របស់ Render ផ្ទាល់តែម្ដង មិនបាច់ឆ្លងកាត់ config ឡើយ
TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
import helpers
# បង្ខំឱ្យ Python រត់ចូលទៅអាន និងចុះឈ្មោះ @bot.message_handler ក្នុងឯកសារទាំងពីរនេះ
from admin_handlers import *
from student_handlers import *

# 👁️ ៣. បង្ខំឱ្យ TeleBot បោះ Error គ្រប់យ៉ាងមកបង្ហាញលើ Terminal ខ្មៅ ហាមលាក់!
logger = logging.getLogger('telebot')
formatter = logging.Formatter('%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"')
console_output_handler = logging.StreamHandler()
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)
logger.setLevel(logging.DEBUG)

# ========================================================
# 🔗 🔌 ផ្ដុំប្រព័ន្ធ Handlers ទាំងអស់ចូលគ្នា (លំដាប់ទី ១)
# ========================================================
#admin_handlers.register_admin_handlers(bot)    # 👑 ដំណើរការមុខងារ Admin ទាំងអស់
register_admin_teacher_handlers(bot, supabase)  # 👩‍🏫 ដំណើរការមុខងារគ្រូ
# ========================================================
# ========================================================
# 🎯 មុខងារផ្លូវកាត់ពិសេស៖ ដាក់ក្នុង main.py ផ្ទាល់ ធានា Admin ចុចលោតផ្ទាំងសិស្ស ១០០%
# ========================================================
@bot.message_handler(func=lambda message: message.text == "👁️ ផ្ទាំងសិស្ស (Student Panel)")
def force_admin_enter_student_panel(message):
    chat_id = message.chat.id
    
    # 🚀 ហៅផ្ទាំងប៊ូតុងសិស្សានុសិស្ស ចេញពី helpers.py មកបង្ហាញជូន Admin ភ្លាមៗ
    bot.send_message(
        chat_id, 
        "🔄 **លោកអ្នកកំពុងស្ថិតនៅក្នុង៖ ផ្ទាំងបង្ហាញរបស់សិស្ស (Student View)**\n"
        "--------------------------------------------------\n"
        "💡 លោកគ្រូ/Admin អាចចុចតេស្តប៊ូតុងសិស្សានុសិស្សនៅខាងក្រោមបានសេរីបាទ។",
        reply_markup=helpers.main_menu('km')
    )
# 🚀 មុខងារមេ /start (បង្ហាញមគ្គុទ្ទេសក៍ណែនាំគ្រប់តួនាទី - GROUP COMPATIBLE)
# ========================================================
@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # 📝 ផ្ទាំងអត្ថបទណែនាំ (Markdown Format)
    welcome_guide = (
        "🎯 **[ ស្វាគមន៍មកកាន់ប្រព័ន្ធគ្រប់គ្រងសាលារៀន DUC ]**\n"
        "--------------------------------------------------\n"
        "🤖 ខ្ញុំជា Bot ជំនួយការផ្លូវការរបស់សាលារៀន។ សូមអានការណែនាំខាងក្រោមដើម្បីចូលប្រើប្រាស់គណនីរបស់អ្នក៖\n\n"
        
        "👤 **១. សម្រាប់សិស្សានុសិស្ស (Student Guide)៖**\n"
        "👉 **របៀប Login៖** មិនបាច់វាយបញ្ជាអ្វីទាំងអស់! សូមវាយបញ្ចូលតែ **លេខកូដសម្ងាល់សិស្ស (Student ID)** របស់អ្នក រួចចុចផ្ញើមកកាន់ Bot ភ្លាមជាការស្រេច (ឧទាហរណ៍៖ `STU001`)។\n"
        "👉 **របៀបចុះឈ្មោះថ្មី៖** ប្រសិនបើមិនទាន់មាន ID ទេ សូមវាយបញ្ជា `/register` ដើម្បីស្នើសុំចុះឈ្មោះ។\n\n"
        
        "👑 **២. សម្រាប់ថ្នាក់ដឹកនាំ/រដ្ឋបាល (Admin Guide)៖**\n"
        "👉 **របៀប Login៖** សូមវាយបញ្ជា `/login` តាមដោយដកឃ្លា និងលេខកូដសម្ងាត់មេរបស់សាលា។\n"
        "✍️ គំរូត្រឹមត្រូវ៖ `/login DUC_Admin@2026`\n\n"
        
        "👩‍🏫 **៣. សម្រាប់លោកគ្រូ-អ្នកគ្រូ (Teacher Guide)៖**\n"
        "👉 **របៀប Login៖** សូមវាយបញ្ជា `/tlogin` តាមដោយដកឃ្លា និងលេខកូដសម្ងាត់គ្រូបង្រៀន។\n"
        "✍️ គំរូត្រឹមត្រូវ៖ `/tlogin TCH_Password@2026`\n"
        "--------------------------------------------------\n"
        "🌐 *សូមជ្រើសរើសភាសាខាងក្រោម ដើម្បីចាប់ផ្ដើមដំណើរការ៖*"
    )
    
    # 🌐 បង្កើត Inline Keyboard ភាសាដាច់ដោយឡែក ការពារ Error AttributeError
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ភាសាខ្មែរ 🇰🇭", callback_data="lang_km"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"))
    
    try:
        # 🔄 បង្កើត ឬអាប់ដេតគណនីបម្រុងទុកឱ្យគេក្នុង Supabase (ប្រើ on_conflict ការពារ Error ស្ទួន)
        supabase.table("users").upsert(
            {"telegram_id": user_id, "status": "PENDING", "language": "km"}, 
            on_conflict="telegram_id"
        ).execute()
        print(f"📩 [CONNECTED] Sync ទិន្នន័យ ID: {user_id} ចូល Supabase រួចរាល់។")
        
    except Exception as e:
        print(f"❌ [SUPABASE SYNC ERROR]៖ {e}")
        # ទោះបីជាដាច់ណេត Supabase ក៏កូដនៅតែរត់ទៅផ្ញើសារដដែល មិនឱ្យគាំង Bot ទេ
        
    try:
        # 📤 ផ្ញើអត្ថបទព្រមទាំងប៊ូតុងជ្រើសរើសភាសាទៅកាន់ Chat (ទោះក្នុងគ្រុបក៏លោតដែរ)
        bot.send_message(chat_id, welcome_guide, parse_mode='Markdown', reply_markup=markup)
        print(f"✅ [SUCCESS] បានបាញ់ផ្ញើសារ Guide ទៅកាន់ Chat ID: {chat_id} ជោគជ័យ!")
    except Exception as e:
        print(f"❌ [SEND MESSAGE ERROR]៖ {e}")

# ========================================================
# 📥 ផ្នែកទទួលឯកសារ UPLOAD កិច្ចការផ្ទះ (API Storage/Insert Mode)
# ========================================================
@bot.message_handler(content_types=['photo', 'document'])
def handle_homework_upload(message):
    user_id = message.from_user.id
    
    try:
        user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
        user = user_res.data[0] if user_res.data else None
        
        if user and user['status'] == 'UPLOAD_MODE':
            stu_res = supabase.table("students").select("name, class_level").eq("student_id", user['student_id']).execute()
            std = stu_res.data[0]
            
            # ស្វែងរកកិច្ចការផ្ទះចុងក្រោយ
            hw_res = supabase.table("homework").select("id, deadline_at").eq("class_level", std['class_level']).order("id", desc=True).limit(1).execute()
            
            if hw_res.data:
                latest_hw = hw_res.data[0]
                dl_time = datetime.fromisoformat(latest_hw['deadline_at'].replace('+00:00', ''))
                
                if datetime.now() > dl_time:
                    supabase.table("users").update({"status": "APPROVED"}).eq("telegram_id", user_id).execute()
                    bot.reply_to(message, "❌ **មិនអាចប្រគល់បានទេ!** កិច្ចការផ្ទះនេះបានហួសកាលកំណត់ (Overdue) ហើយ។")
                    return

                file_id = message.photo[-1].file_id if message.content_type == 'photo' else message.document.file_id
                ext = "jpg" if message.content_type == 'photo' else message.document.file_name.split('.')[-1]
                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                
                filename = f"stu_{user['student_id']}_{message.message_id}.{ext}"
                full_path = f"student_assignments/{filename}"
                
                if not os.path.exists('student_assignments'):
                    os.makedirs('student_assignments')
                    
                with open(full_path, 'wb') as f: 
                    f.write(downloaded)
                
                # 🔗 Insert ទិន្នន័យប្រគល់កិច្ចការចូល Supabase
                sub_res = supabase.table("student_submissions").insert({
                    "homework_id": latest_hw['id'], 
                    "student_id": user['student_id'], 
                    "class_level": std['class_level'], 
                    "submitted_file": filename
                }).execute()
                
                submission_id = sub_res.data[0]['id']
                
                supabase.table("users").update({"status": "APPROVED"}).eq("telegram_id", user_id).execute()
                bot.reply_to(message, f"📥 **ប្រគល់កិច្ចការផ្ទះជោគជ័យ!** (Submission ID: `{submission_id}`)", reply_markup=helpers.main_menu(user['language']))
                
                admin_alert = f"🔔 **សិស្សប្រគល់កិច្ចការផ្ទះថ្មី៖**\n👤 ឈ្មោះ៖ {std['name']}\n🏫 ថ្នាក់៖ {std['class_level']}\n🆔 Submission ID: `{submission_id}`\n\n👉 លោកគ្រូដាក់ពិន្ទុ៖ `/grade {submission_id},ពិន្ទុ,មតិវាយតម្លៃ`"
                helpers.notify_all_admins(bot, admin_alert, attachment=full_path, is_photo=(message.content_type == 'photo'))
    except Exception as e:
        bot.reply_to(message, f"❌ API Upload Error: {e}")

# ========================================================
# 🎓 លំដាប់ទី ៣៖ ដំណើរការមុខងារសិស្សទាំងអស់ (ទុកនៅបាតក្រោមគេបង្អស់)
# ========================================================
register_student_handlers(bot, supabase)  

# ========================================================
# # ==========================================
# # 🌐 បើក Web Server Flask การពារ Bot Sleep លើ Render
# # ==========================================


# # from flask import Flask
# # web_app = Flask('')
# # @web_app.route('/')
# # def home(): return "DUC API System Sprint 4 Baseline Live!"

# # def run_web_server():
# #     bot_port = int(os.environ.get("PORT", 10000))
# #     web_app.run(host='0.0.0.0', port=bot_port)

# # threading.Thread(target=run_web_server, daemon=True).start()

# if __name__ == "__main__":
#     print("🎯 [SUCCESS] DUC System API Core Engine is live and Polling...")
#     bot.infinity_polling()
#     student_handlers.register_student_handlers(bot)
# 🛰️ ៤. ដុតបញ្ឆេះប្រព័ន្ធមេ (Core Engine Polling)
# ========================================================
if __name__ == "__main__":
    print("🎯 [SUCCESS] DUC System API Core Engine is live and Polling...")
   # 💡 បន្ថែម allowed_updates ដើម្បីបង្ខំឱ្យ Bot ចាប់យកទាំងអក្សរ រូបភាព និងឯកសារ PDF គ្រប់ពេល
bot.infinity_polling(allowed_updates=['message', 'edited_message', 'callback_query'])
