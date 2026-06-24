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
# ===================================================================================
# ===================================================================================
# 🎛️ ផ្ទាំង Menu គ្រាប់ចុច Inline សម្រាប់ Admin (កំណែទម្រង់ស៊ីគ្នាជាមួយ admin_handlers.py)
# ===================================================================================
def send_admin_panel(bot, chat_id):
    admin_msg = (
        "🏫 **ស្វាគមន៍លោកនាយក / លោកគ្រូ-អ្នកគ្រូ (DUC API Dashboard)**\n\n"
        
        "📊 **១. របាយការណ៍ទូទៅ & បញ្ជីរាយឈ្មោះ (Metrics & Lists)៖**\n"
        "🔹 មើលស្ថិតិសាលារួម៖ `/school_stats`\n"
        "🔹 មើលអត្រាប្រគល់កិច្ចការ៖ `/hw_analytics`\n"
        "🔹 រាយឈ្មោះថ្នាក់រៀនទាំងអស់៖ `/list_classes`\n"
        "🔹 រាយឈ្មោះផ្នែក/ដេប៉ាតាម៉ង់៖ `/list_depts`\n"
        "🔹 រាយឈ្មោះលោកគ្រូ-អ្នកគ្រូទាំងអស់៖ `/list_teachers`\n"
        "🔹 មុខវិជ្ជាសកម្មតាមផ្នែក ៖ `/list_depts`\n\n"
        
        "👤 **២. គ្រប់គ្រងសិស្ស និងវិន័យ (Students & Discipline)៖**\n"
        "🔹 ថែមសិស្សថ្មី (Wizard)៖ `/addstu`\n"
        "🔹 កត់ត្រាវិន័យ (Wizard)៖ `/adddiscipline`\n"
        "🔹 **អនុម័តសិស្សថ្មី៖** `/approve`\n"
        "🔹 មើលសិស្សចុះឈ្មោះថ្មី៖ `/checkreq` 🔍\n\n"
        
        "📝 **៣. គ្រប់គ្រងកិច្ចការផ្ទះ (Homework Management)៖**\n"
        "📅 ថែមតារាងកាលវិភាគ៖ `/addschedule`\n"
        "🔹 ដាក់ពិន្ទុ & Feedback ៖ `/grade`\n\n"
        
        "📅 **៤. សេចក្ដីជូនដំណឹង (Notices)៖**\n"
        "🔹 ថែមសេចក្ដីប្រកាស៖ `/addnotice`\n"
        "🔹 ថែមថ្ងៃឈប់សម្រាកសាលា៖ `/addholiday`\n\n"
        
        "🏢 **៥. គ្រប់គ្រងរចនាសម្ព័ន្ធសាលា (School Structures)៖**\n"
        "🔹 ថែមគណនីគ្រូថ្មី៖ `/addteacher`\n"
        "🔹 ថែមផ្នែកឱ្យគ្រូ៖ `/adddept`\n"
        "🔹 ថែមជំនាញឱ្យគ្រូ៖ `/addmajor`\n"
        "🔗 ភ្ជាប់គ្រុបថ្នាក់រៀនអូតូ ៖ `/setclass ឈ្មោះថ្នាក់`"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # 🎛️ 💡 កែសម្រួល៖ តម្រឹម callback_data ឱ្យត្រូវគ្នាជាមួយកូដ admin_handlers.py បេះបិទ
    btn_stats = types.InlineKeyboardButton("📊 មហារបាយការណ៍រួម", callback_data="school_stats")
    btn_analytics = types.InlineKeyboardButton("📈 អត្រាប្រគល់កិច្ចការ", callback_data="hw_analytics")
    
    btn_classes = types.InlineKeyboardButton("🏫 បញ្ជីថ្នាក់រៀន", callback_data="list_classes")
    btn_teachers = types.InlineKeyboardButton("👨‍🏫 បញ្ជីលោកគ្រូ-អ្នកគ្រូ", callback_data="list_teachers")
    
    btn_depts = types.InlineKeyboardButton("🏢 បញ្ជីដេប៉ាតាម៉ង់", callback_data="list_depts")
    # កែពី list_depts មកជា list_classes បណ្តោះអាសន្ន ឬទុកចោលកុំឱ្យជាន់គ្នា
    btn_subjects = types.InlineKeyboardButton("📚 មុខវិជ្ជាតាមផ្នែក", callback_data="list_classes") 
    
    btn_checkreq = types.InlineKeyboardButton("🔍 សិស្សចុះឈ្មោះថ្មី", callback_data="checkreq")
    btn_approve = types.InlineKeyboardButton("🟢 អនុម័ត (Approve) សិស្ស", callback_data="approve")
    
    btn_addstu = types.InlineKeyboardButton("👤 ថែមសិស្សថ្មី", callback_data="addstu")
    btn_addteacher = types.InlineKeyboardButton("➕ បង្កើតគណនីគ្រូថ្មី", callback_data="addteacher")
    
    btn_discipline = types.InlineKeyboardButton("⚖️ កត់ត្រាវិន័យ", callback_data="adddiscipline")
    btn_grade = types.InlineKeyboardButton("✍️ ដាក់ពិន្ទុសិស្ស", callback_data="grade")
    btn_notice = types.InlineKeyboardButton("📢 ថែមសេចក្ដីប្រកាស", callback_data="addnotice")
    btn_holiday = types.InlineKeyboardButton("🏖️ ថែមថ្ងៃឈប់សម្រាក", callback_data="addholiday") # បានបន្ថែមឱ្យត្រូវតាមទម្រង់ប្រព័ន្ធបាញ់សាររបស់លោកគ្រូ
    
    # 📥 រៀបចំដាក់គ្រាប់ចុចចូលក្នុងផ្ទាំង (Layout Grid)
    markup.add(btn_stats, btn_analytics)
    markup.add(btn_classes, btn_teachers)
    markup.add(btn_depts, btn_subjects)
    markup.add(btn_checkreq, btn_approve)
    markup.add(btn_addstu, btn_addteacher)
    markup.add(btn_grade, btn_notice)
    markup.add(btn_discipline)
    markup.add(btn_discipline, btn_holiday)
    
    # 📤 ១. បាញ់ចេញផ្ទាំង Dashboard និងគ្រាប់ចុច Inline Markup
    bot.send_message(chat_id, admin_msg, reply_markup=markup, parse_mode='Markdown')
    
    # 📤 ២. ផ្ញើសារប្រាប់ថាប្រព័ន្ធដំណើរការរួចរាល់
    bot.send_message(chat_id, "🎛️ **ផ្ទាំងបញ្ជាគ្រាប់ចុចរហ័ស (Admin Panel Loaded Successfully)**")
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
