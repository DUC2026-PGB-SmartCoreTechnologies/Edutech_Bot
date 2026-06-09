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
# 🎛️ ផ្ទាំង Menu គ្រាប់ចុចសិស្ស
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
# 👑 ផ្ទាំងចងប៊ូតុង INLINE MENU ឱ្យដូចតាមរូបថតរបស់បង ១០០%
# ========================================================
def send_admin_panel(bot, chat_id):
    # 📝 សារព័ត៌មានបង្ហាញនៅលើអេក្រង់ដូចរូបបងបេះបិទ
    admin_msg = (
        "🏫 **ស្វាគមន៍លោកនាយក / លោកគ្រូ-អ្នកគ្រូ (DUC API Dashboard)**\n\n"
        "📊 **១. របាយការណ៍ទូទៅ (Principal Metrics)៖**\n"
        "🔹 មើលស្ថិតិសាលារួម៖ `/school_stats`\n"
        "🔹 មើលអត្រាប្រគល់កិច្ចការ៖ `/hw_analytics`\n\n"
        "👤 **២. គ្រប់គ្រងសិស្ស និងវិន័យ (Students & Discipline)៖**\n"
        "🔹 ថែមសិស្ស៖ `/addstu ID,ឈ្មោះ,ភេទ(M/F),ថ្នាក់`\n"
        "🔹 កត់ត្រាវិន័យ៖ `/adddiscipline ID_សិស្ស,បញ្ហាកើតឡើង,វិធានការកែប្រែ`\n\n"
        "📝 **៣. គ្រប់គ្រងកិច្ចការផ្ទះ (Homework Management)៖**\n"
        "🔹 ដាក់ពិន្ទុ & Feedback ឱ្យសិស្ស៖ `/grade ID_Submission,ពិន្ទុ,មតិយោបល់`\n\n"
        "📅 **៤. សេចក្ដីជូនដំណឹង (Notices)៖**\n"
        "🔹 ថែមសេចក្ដីប្រកាស៖ `/addnotice ចំណងជើង,ខ្លឹមសារព័ត៌មាន`"
    )
    
    # 🎛️ បង្កើត Inline Keyboard ចុចភ្លាមលោត Guide ណែនាំភ្លាមៗ
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # 🔗 ជួរទី ១៖ ផ្នែករបាយការណ៍
    btn_stats = types.InlineKeyboardButton("📊 ស្ថិតិសាលារួម", callback_data="adm_guide_stats")
    btn_analytics = types.InlineKeyboardButton("📈 អត្រាប្រគល់កិច្ចការ", callback_data="adm_guide_analytics")
    
    # 🔗 ជួរទី ២៖ ផ្នែកសិស្ស និងវិន័យ
    btn_addstu = types.InlineKeyboardButton("👤 ថែមសិស្សថ្មី", callback_data="adm_guide_addstu")
    btn_discipline = types.InlineKeyboardButton("⚖️ កត់ត្រាវិន័យ", callback_data="adm_guide_discipline")
    
    # 🔗 ជួរទី ៣៖ ផ្នែកកិច្ចការ និងសេចក្តីប្រកាស
    btn_grade = types.InlineKeyboardButton("✍️ ដាក់ពិន្ទុសិស្ស", callback_data="adm_guide_grade")
    btn_notice = types.InlineKeyboardButton("📢 ថែមសេចក្ដីប្រកាស", callback_data="adm_guide_notice")
    
    # 🔗 ជួរទី ៤៖ ប៊ូតុងបង្កើតគ្រូ (ប៊ូតុងចងបន្ថែម)
    btn_addteacher = types.InlineKeyboardButton("➕ បង្កើតគណនីគ្រូថ្មី", callback_data="adm_guide_addteacher")

    # ផ្ដុំប៊ូតុងទាំងអស់ចូលក្នុង Markup
    markup.add(btn_stats, btn_analytics)
    markup.add(btn_addstu, btn_discipline)
    markup.add(btn_grade, btn_notice)
    markup.add(btn_addteacher)
    
    # 📤 បាញ់ចេញទៅកាន់អេក្រង់ Admin
    bot.send_message(chat_id, admin_msg, parse_mode='Markdown', reply_markup=markup)

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