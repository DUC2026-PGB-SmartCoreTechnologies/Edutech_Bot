from telebot import types
from config import supabase
import helpers
def lang_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ភាសាខ្មែរ 🇰🇭", callback_data="lang_km"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")
    )
    return markup
def register_student_handlers(bot):
    @bot.message_handler(commands=['register'])
    def student_registration_start(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # ឆែកមើលក្រែងលោគាត់ធ្លាប់ចុះឈ្មោះរួចហើយ
        user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
        if user_res.data and user_res.data[0].get('student_id'):
            bot.send_message(chat_id, "ℹ️ **ប្អូនបានភ្ជាប់គណនីរួចរាល់ហើយ មិនបាច់ចុះឈ្មោះថ្មីទៀតទេបាទ!**")
            return
            
        # ប្ដូរ Status គាត់ទៅជាវគ្គបំពេញព័ត៌មានចុះឈ្មោះ
        try:
            supabase.table("users").upsert({"telegram_id": user_id, "status": "REG_MODE", "language": "km"}, on_conflict="telegram_id").execute()
            
            reg_msg = (
                "📝 **[ ទម្រង់ស្នើសុំចុះឈ្មោះចូលរៀនអនឡាញ ]**\n"
                "--------------------------------------------------\n"
                "សូមប្អូនបំពេញព័ត៌មានផ្ទាល់ខ្លួន តាមទម្រង់ខាងក្រោមឱ្យបានត្រឹមត្រូវ៖\n\n"
                "👉 **សូមវាយបញ្ជូន៖** `ឈ្មោះសិស្ស,ភេទ(M ឬ F),ថ្នាក់រៀន`\n"
                "✍️ គំរូត្រឹមត្រូវ៖ `សុខ ភារម្យ,M,Grade12_A`"
            )
            bot.send_message(chat_id, reg_msg, parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Error: {e}")
        

    # 📝 អាណាព្យាបាលចុចទម្រង់សុំច្បាប់អនឡាញ (API Status Update)
    @bot.message_handler(func=lambda m: m.text == "📝 Submit Leave Request (សុំច្បាប់)")
    def parent_leave_request_start(message):
        user_id = message.from_user.id
        user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
        if user_res.data and user_res.data[0]['status'] == 'APPROVED':
            supabase.table("users").update({"status": "LEAVE_MODE"}).eq("telegram_id", user_id).execute()
            bot.send_message(message.chat.id, "📝 **សូមបំពេញព័ត៌មានសុំច្បាប់តាមទម្រង់ខាងក្រោម៖**\n\n👉 វាយបញ្ជូន៖ `ID_សិស្ស,មូលហេតុ` ")

    # 👁️ ស្ទាក់ចាប់ការចុចប៊ូតុង Read Receipts & Digital Signature (API version)
    @bot.callback_query_handler(func=lambda call: call.data.startswith('readnotice_') or call.data.startswith('signnotice_'))
    def handle_notice_interactions(call):
        parent_id = call.from_user.id
        action, notice_id = call.data.split('_')
        notice_id = int(notice_id)
        
        if action == "readnotice":
            # 🔗 API Update: កត់ត្រាការបើកអាន (Seen Status)
            supabase.table("notice_engagements").update({"is_seen": True, "seen_at": "now()"}).eq("notice_id", notice_id).eq("parent_telegram_id", parent_id).execute()
            notice_res = supabase.table("school_notices").select("title, content").eq("id", notice_id).execute()
            bot.send_message(call.message.chat.id, f"📖 **{notice_res.data[0]['title']}**\n\n{notice_res.data[0]['content']}", parse_mode='Markdown')
            bot.answer_callback_query(call.id, "បានកត់ត្រាការអានរួចរាល់ (Seen)")

        elif action == "signnotice":
            # 🔗 API Update: កត់ត្រាហត្ថលេខាឌីជីថល (Digital Signature)
            supabase.table("notice_engagements").update({"is_acknowledged": True, "acknowledged_at": "now()"}).eq("notice_id", notice_id).eq("parent_telegram_id", parent_id).execute()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=call.message.text + "\n\n✍️ **ស្ថានភាព៖ អ្នកបានចុចយល់ព្រម (Digital Signed) រួចរាល់។**"
            )
            bot.answer_callback_query(call.id, "✅ បានចុះហត្ថលេខាឌីជីថលជោគជ័យ", show_alert=True)

   # ========================================================
    # 🔄 ដំណើរការស្ទាក់ចាប់អត្ថបទរបស់សិស្ស និងអាណាព្យាបាល (API Processing)
    # ========================================================
    @bot.message_handler(func=lambda message: message.chat.type == 'private' and message.text and not message.text.startswith('/'))
    def handle_text(message):
        chat_id = message.chat.id
        user_id = message.from_user.id  
        text = message.text.strip()
        
        try:
            # ទាញទិន្នន័យអ្នកប្រើប្រាស់មកឆែក Status
            user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
            user = user_res.data[0] if user_res.data else None
            lang = user['language'] if user else 'km'
            
            # ----------------------------------------------------
            # 🔥 លំដាប់ទី ១៖ ករណីសិស្សថ្មីកំពុងបំពេញព័ត៌មានចុះឈ្មោះ (REG_MODE) -> ត្រូវដេកលើគេបង្អស់!
            # ----------------------------------------------------
           # 🔵 ករណីសិស្សថ្មីកំពុងបំពេញព័ត៌មានចុះឈ្មោះ (REG_MODE)
           # 🔵 ករណីសិស្សថ្មីកំពុងបំពេញព័ត៌មានចុះឈ្មោះ (REG_MODE)
            if user and user['status'] == 'REG_MODE':
                try:
                    parts = text.split(',')
                    if len(parts) < 3:
                        raise ValueError("ទិន្នន័យមិនគ្រប់គ្រាន់")
                        
                    s_name, s_gender, s_class = parts[0].strip(), parts[1].strip().upper(), parts[2].strip().upper()
                    
                    # បង្កើតលេខ ID បណ្ដោះអាសន្នជូនគាត់
                    temp_id = f"PENDING_{user_id}"
                    
                    # ១. កត់ត្រាចូលតារាង students លើ Supabase (ដំណើរការជោគជ័យហើយ)
                    supabase.table("students").upsert({
                        "student_id": temp_id, 
                        "name": s_name, 
                        "gender": s_gender, 
                        "class_level": s_class,
                        "parent_telegram_id": user_id
                    }, on_conflict="student_id").execute()
                    
                    # ២. អាប់ដេត Status ក្នុងតារាង users (ដក "name": s_name ចេញរួចរាល់)
                    supabase.table("users").update({"status": "WAIT_APPROVE"}).eq("telegram_id", user_id).execute()
                    
                    # 📤 ៣. ផ្ញើសារប្រាប់សិស្សវិញភ្លាមៗ (កូដរត់មកដល់ទីនេះដឹងតែឆ្លើយតបជោគជ័យ ១00%)
                    bot.send_message(chat_id, "✅ **ការស្នើសុំចុះឈ្មោះត្រូវបានបញ្ជូនជោគជ័យ!**\nសូមរង់ចាំការពិនិត្យ និងអនុម័ត (Approve) ពីលោកគ្រូ/Admin ជាមុនសិនបាទ។")
                    
                    # 🔔 ៤. បាញ់សារ Alert ទៅកាន់គ្រប់ Admin (ដាក់ក្នុង try/except មួយទៀត ការពារវាធ្វើឱ្យកូដគាំង)
                    # 🔔 ៤. បាញ់សារ Alert ទៅកាន់គ្រប់ Admin (បន្ថែមប៊ូតុងចុច Approve អូតូ)
                    try:
                        # បង្កើតប៊ូតុង Inline ផ្ញើទៅជាមួយសារ Admin
                        markup_admin = types.InlineKeyboardMarkup()
                        markup_admin.add(
                            types.InlineKeyboardButton("✅ APPROVE", callback_data=f"appr_{user_id}_{s_class}"),
                            types.InlineKeyboardButton("❌ REJECT", callback_data=f"reje_{user_id}")
                        )
                        
                        admin_alert = (
                            "🚨 **មានសិស្សស្នើសុំចុះឈ្មោះថ្មី (Pending Approval)៖**\n"
                            "--------------------------------------------------\n"
                            f"👤 ឈ្មោះ៖ *{s_name}*\n"
                            f"👫 ភេទ៖ `{s_gender}`\n"
                            f"🏫 ថ្នាក់រៀន៖ *{s_class}*\n"
                            f"🆔 Telegram ID៖ `{user_id}`\n"
                            "--------------------------------------------------\n"
                            "👉 លោកគ្រូអាចចុចប៊ូតុងខាងក្រោម ដើម្បីអនុម័តឱ្យសិស្សចូលរៀនភ្លាមៗ៖"
                        )
                        # ផ្ញើសារ Alert ទៅ Admin ព្រមទាំងភ្ជាប់ប៊ូតុងបញ្ជា
                        helpers.notify_all_admins(bot, admin_alert, reply_markup=markup_admin)
                    except Exception as admin_err:
                        print(f"⚠️ មិនអាចផ្ញើ Alert ទៅ Admin បានទេដោយសារ៖ {admin_err}")
                        
                except Exception as e:
                    print(f"❌ Error រួម៖ {e}")
                    bot.send_message(chat_id, "⚠️ ទម្រង់បំពេញខុសហើយប្អូន! គំរូ៖ `ឈ្មោះសិស្ស,M,Grade12_A`")
                return
            # ----------------------------------------------------
            # 🟢 លំដាប់ទី ២៖ អាណាព្យាបាលកំពុងបំពេញច្បាប់អនឡាញ (LEAVE_MODE)
            # ----------------------------------------------------
            if user and user['status'] == 'LEAVE_MODE':
                try:
                    parts = text.split(',')
                    sid, reason = parts[0].strip().upper(), parts[1].strip()
                    
                    stu_res = supabase.table("students").select("class_level").eq("student_id", sid).execute()
                    class_lvl = stu_res.data[0]['class_level']
                    
                    supabase.table("attendance").insert({"student_id": sid, "class_level": class_lvl, "status": "EXCUSED", "leave_requested_online": True, "leave_approval_status": "PENDING", "reason": reason}).execute()
                    supabase.table("users").update({"status": "APPROVED"}).eq("telegram_id", user_id).execute()
                    
                    bot.send_message(chat_id, "✅ **លិខិតសុំច្បាប់អនឡាញត្រូវបានបញ្ជូនទៅកាន់លោកគ្រូហើយ**", reply_markup=helpers.main_menu(lang))
                    helpers.notify_all_admins(bot, f"🔔 **មានលិខិតសុំច្បាប់អនឡាញថ្មី៖**\n🆔 ID សិស្ស៖ `{sid}`\n📝 មូលហេតុ៖ _{reason}_")
                except:
                    bot.send_message(chat_id, "⚠️ ទម្រង់ខុស! គំរូ៖ `ID_សិស្ស,មូលហេតុ`")
                return

            # ----------------------------------------------------
            # 🔴 លំដាប់ទី ៣៖ គណនីទទេស្អាត (NEW) វាយលេខ ID សិស្ស ដើម្បី LOGIN ភ្ជាប់ប្រព័ន្ធ
            # ----------------------------------------------------
            if not user or not user.get('student_id'):
                stu_check = supabase.table("students").select("*").eq("student_id", text.upper()).execute()
                if stu_check.data:
                    supabase.table("users").update({"student_id": text.upper(), "status": "APPROVED", "app_installed": 1}).eq("telegram_id", user_id).execute()
                    supabase.table("students").update({"parent_telegram_id": user_id}).eq("student_id", text.upper()).execute()
                    bot.send_message(chat_id, f"✅ ភ្ជាប់ទំនាក់ទំនងជាមួយសិស្សឈ្មោះ៖ *{stu_check.data[0]['name']}* ជោគជ័យ!", parse_mode='Markdown', reply_markup=helpers.main_menu(lang))
                else:
                    bot.reply_to(message, "❌ រកមិនឃើញលេខសម្គាល់សិស្សនេះទេ!")
                    
        except Exception as e:
            print(f"Text Handler Error: {e}")