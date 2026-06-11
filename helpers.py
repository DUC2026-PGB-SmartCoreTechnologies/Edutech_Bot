import os
import json
from telebot import types
from config import supabase

# ========================================================
# 🌐 មុខងារទាញយកអត្ថបទភាសាតាម Multi-language
# ========================================================
def get_string(lang, key):
    file_path = f"locales/{lang}.json"
    if not os.path.exists(file_path): 
        lang = 'km'
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            strings = json.load(f)
        return strings.get(key, key)
    except:
        return key

# ========================================================
# 🌐 ប៊ូតុងប្រភេទ Inline Keyboard សម្រាប់ឱ្យសិស្សរើសភាសា
# ========================================================
def lang_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ភាសាខ្មែរ 🇰🇭", callback_data="lang_km"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")
    )
    return markup

# ========================================================
# 🎛️ ផ្ទាំង Menu គ្រាប់ចុចសិស្ស (ReplyKeyboardMarkup)
# ========================================================
def main_menu(lang):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton(get_string(lang, 'btn_hw')),
        types.KeyboardButton(get_string(lang, 'btn_hol')),
        types.KeyboardButton("📤 Upload Homework (ប្រគល់កិច្ចការ)"),
        types.KeyboardButton("📝 Submit Leave Request (សុំច្បាប់)"),
        types.KeyboardButton(get_string(lang, 'btn_schedule')),
        types.KeyboardButton(get_string(lang, 'btn_lang')),
        types.KeyboardButton(get_string(lang, 'btn_logout'))
    )
    return markup

# ========================================================
# 🎛️ ផ្ទាំង Menu គ្រាប់ចុចពណ៌ប្រផេះធំៗសម្រាប់ Admin
# ========================================================
def admin_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("➕ បង្កើតគណនីគ្រូ"),
        types.KeyboardButton("📋 មើលបញ្ជីគ្រូ"),
        types.KeyboardButton("👁️ ផ្ទាំងសិស្ស (Student Panel)"),  # 🟢 គ្រាប់ចុចគន្លឹះប្តូរផ្ទាំង
        types.KeyboardButton("🔙 ចាកចេញ (Logout)")
    )
    return markup

# ========================================================
# 👑 ផ្ទាំងចងប៊ូតុង INLINE MENU សម្រាប់ Admin
# ========================================================
def send_admin_panel(bot, chat_id):
    admin_msg = (
        "🏫 **ស្វាគមន៍លោកនាយក / លោកគ្រូ-អ្នកគ្រូ (DUC API Dashboard)**\n\n"
        "📊 **១. របាយការណ៍ទូទៅ (Principal Metrics)៖**\n"
        "🔹 មើលស្ថិតិសាលារួម៖ `/school_stats`\n"
        "🔹 មើលអត្រាប្រគល់កិច្ចការ៖ `/hw_analytics`\n\n"
        "👤 **២. គ្រប់គ្រងសិស្ស និងវិន័យ (Students & Discipline)៖**\n"
        "🔹 ថែមសិស្ស៖ `/addstu ID,ឈ្មោះ,ភេទ(M/F),ថ្នាក់`\n"
        "🔹 កត់ត្រាវិន័យ៖ `/adddiscipline ID_សិស្ស,បញ្ហាកើតឡើង,វិធានការកែប្រែ`\n\n"
        "🔹 **អនុម័តសិស្សថ្មី៖** `/approve ID_Telegram`\n"
        "🔹 មើលសិស្សចុះឈ្មោះថ្មី៖ `/checkreq` 🔍\n\n"
        "📝 **៣. គ្រប់គ្រងកិច្ចការផ្ទះ (Homework Management)៖**\n"
        "📅 ថែមតារាងកាលវិភាគ៖ `/addschedule ថ្នាក់,មុខវិជ្ជា,IDគ្រូ,ថ្ងៃរៀន,ម៉ោងដើម,ម៉ោងចប់`\n"
        "🔹 ដាក់ពិន្ទុ & Feedback ឱ្យសិស្ស៖ `/grade ID_Submission,ពិន្ទុ,មតិយោបល់`\n\n"
        "📅 **៤. សេចក្ដីជូនដំណឹង (Notices)៖**\n"
        "🔹 ថែមសេចក្ដីប្រកាស៖ `/addnotice ចំណងជើង,ខ្លឹមសារព័ត៌មាន`"
        "🔹 ថែមថ្ងៃឈប់សម្រាកសាលា៖ `/addholiday ឈ្មោះខ្មែរ,ឈ្មោះអង់គ្លេស,ឆ្នាំ-ខែ-ថ្ងៃ`\n\n"
        "🏢 **៥. គ្រប់គ្រងរចនាសម្ព័ន្ធសាលា (School Structures)៖**\n"
        "🔹 ថែមផ្នែកឱ្យគ្រូ៖ `/adddept IDគ្រូ, ឈ្មោះផ្នែក`\n"
        "🔹 ថែមជំនាញឱ្យគ្រូ៖ `/addmajor IDគ្រូ, ឈ្មោះផ្នែក, ឈ្មោះជំនាញ`"
        "🔗 ភ្ជាប់គ្រុបថ្នាក់អូតូ (វាយក្នុងគ្រុប)៖ `/setclass ឈ្មោះថ្នាក់`"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_stats = types.InlineKeyboardButton("📊 ស្ថិតិសាលារួម", callback_data="adm_guide_stats")
    btn_analytics = types.InlineKeyboardButton("📈 អត្រាប្រគល់កិច្ចការ", callback_data="adm_guide_analytics")
    btn_checkreq = types.InlineKeyboardButton("🔍 មើលសិស្សចុះឈ្មោះថ្មី", callback_data="adm_guide_checkreq")
    btn_approve = types.InlineKeyboardButton("🟢 អនុម័ត (Approve) សិស្ស", callback_data="adm_guide_approve")
    btn_addstu = types.InlineKeyboardButton("👤 ថែមសិស្សថ្មី", callback_data="adm_guide_addstu")
    btn_discipline = types.InlineKeyboardButton("⚖️ កត់ត្រាវិន័យ", callback_data="adm_guide_discipline")
    btn_grade = types.InlineKeyboardButton("✍️ ដាក់ពិន្ទុសិស្ស", callback_data="adm_guide_grade")
    btn_notice = types.InlineKeyboardButton("📢 ថែមសេចក្ដីប្រកាស", callback_data="adm_guide_notice")
    btn_addteacher = types.InlineKeyboardButton("➕ បង្កើតគណនីគ្រូថ្មី", callback_data="adm_guide_addteacher")
    
    markup.add(btn_stats, btn_analytics)
    markup.add(btn_checkreq, btn_approve)
    markup.add(btn_addstu, btn_discipline)
    markup.add(btn_grade, btn_notice)
    markup.add(btn_addteacher)
    
    # 📤 បាញ់ទាំងសារ Inline និងផ្ទាំងគ្រាប់ចុចទូរស័ព្ទមកព្រមគ្នា
    bot.send_message(chat_id, admin_msg, parse_mode='Markdown', reply_markup=markup)
    bot.send_message(chat_id, "🎛️ **ផ្ទាំងបញ្ជាគ្រាប់ចុចរហ័ស (Admin Panel Loaded)**", reply_markup=admin_menu())

# ========================================================
# 🔔 ប្រព័ន្ធបាញ់សារដំណឹង (Notification)
# ========================================================
def notify_all_admins(bot, msg, attachment=None, is_photo=False):
    try:
        response = supabase.table("admins").select("telegram_id").execute()
        admins = response.data
        if admins:
            for adm in admins:
                admin_tele_id = adm.get('telegram_id')
                if not admin_tele_id: continue
                try:
                    if attachment and os.path.exists(attachment):
                        with open(attachment, 'rb') as f:
                            if is_photo: 
                                bot.send_photo(admin_tele_id, f, caption=msg, parse_mode='Markdown')
                            else: 
                                bot.send_document(admin_tele_id, f, caption=msg, parse_mode='Markdown')
                    else:
                        bot.send_message(admin_tele_id, msg, parse_mode='Markdown')
                except: 
                    pass
    except Exception as e:
        print(f"❌ Notify Admins Error: {e}")