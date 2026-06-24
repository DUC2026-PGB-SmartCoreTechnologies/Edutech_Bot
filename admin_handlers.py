import telebot
from telebot import types
from datetime import datetime

_bot = None
_supabase = None

def register_admin_teacher_handlers(bot, supabase):
    global _bot, _supabase
    _bot = bot
    _supabase = supabase

    @bot.message_handler(commands=['login'])
    def admin_secret_login(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        try:
            admin_check = supabase.table("users").select("telegram_id").eq("role", "ADMIN").execute()
            if admin_check.data:
                existing_admin_id = admin_check.data[0].get('telegram_id')
                if str(user_id) != str(existing_admin_id):
                    bot.reply_to(message, "❌ សុំទោស! ប្រព័ន្ធគ្រប់គ្រងសាលា DUC មាន Admin មេរួចរាល់ហើយ។")
                    return
        except Exception as e:
            print(f"❌ Error: {e}")
            return

        text_input = message.text.strip()[6:].strip()
        if text_input != "DUC_Admin@2026":
            bot.reply_to(message, "❌ លេខសម្ងាត់ Admin មិនត្រឹមត្រូវទេ!")
            return

        try:
            supabase.table("users").upsert({"telegram_id": user_id, "role": "ADMIN", "status": "APPROVED", "language": "km"}, on_conflict="telegram_id").execute()
            bot.send_message(chat_id, "🟢 ផ្ទៀងផ្ទាត់សិទ្ធិ Admin មេជោគជ័យ!")
        except Exception as e:
            bot.reply_to(message, f"❌ កំហុស៖ {e}")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_system_inline_clicks(call):
        action = call.data
        if action == "addholiday":
            add_holiday_wizard(call.message)
            return
        
        # គ្រប់គ្រងប៊ូតុង Admin ផ្សេងៗទៀតនៅទីនេះ...
        # ឧទាហរណ៍៖ if action == "list_classes": list_classes_command(call.message)

    @bot.message_handler(commands=['addholiday'])
    def add_holiday_wizard(message):
        sent_msg = bot.send_message(message.chat.id, "🏖️ សូមបំពេញឈ្មោះថ្ងៃឈប់សម្រាក (ខ្មែរ)៖")
        bot.register_next_step_handler(sent_msg, process_hol_kh)

    def process_hol_kh(message):
        bot.register_next_step_handler(bot.send_message(message.chat.id, "👉 សូមបំពេញឈ្មោះថ្ងៃឈប់សម្រាក (អង់គ្លេស)៖"), process_hol_en, message.text.strip())

    def process_hol_en(message, name_kh):
        bot.register_next_step_handler(bot.send_message(message.chat.id, "👉 សូមបំពេញកាលបរិច្ឆេទ (YYYY-MM-DD)៖"), process_hol_final, name_kh, message.text.strip())

    def process_hol_final(message, name_kh, name_en):
        raw_date = message.text.strip()
        holiday_date = raw_date.replace("០", "0").replace("១", "1").replace("២", "2").replace("៣", "3").replace("៤", "4").replace("៥", "5").replace("៦", "6").replace("៧", "7").replace("៨", "8").replace("៩", "9")
        try:
            _supabase.table("holidays").insert({"event_name_km": name_kh, "event_name_en": name_en, "holiday_date": holiday_date, "announcement_sent": 1}).execute()
            _bot.send_message(message.chat.id, "✅ បញ្ចប់ជោគជ័យ!")
        except Exception as e:
            _bot.send_message(message.chat.id, f"❌ Error: {e}")

def list_classes_command(msg_obj):
    try:
        students_res = _supabase.table("students").select("class_level").execute()
        distinct_classes = set(s['class_level'].strip().upper() for s in students_res.data if s.get('class_level')) if students_res.data else set()
        msg = "🏫 [ បញ្ជីឈ្មោះថ្នាក់រៀនសកម្ម ]\n=========================\n"
        for i, c in enumerate(sorted(distinct_classes), 1): 
            msg += f"{i}. ថ្នាក់៖ {c}\n"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*[types.InlineKeyboardButton(f"📖 ថ្នាក់ {c}", callback_data=f"view_students:{c}") for c in sorted(distinct_classes)])
        _bot.send_message(msg_obj.chat.id, msg, reply_markup=markup)
    except Exception as e: 
        _bot.send_message(msg_obj.chat.id, f"❌ Error: {e}")
