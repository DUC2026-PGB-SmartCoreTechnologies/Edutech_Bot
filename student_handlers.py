from telebot import types
from config import supabase
from datetime import datetime
import helpers
import os

from telebot import types



def lang_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ភាសាខ្មែរ 🇰🇭", callback_data="lang_km"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")
    )
    return markup

def register_student_handlers(bot, supabase):
    # ========================================================
    # ១. មុខងារចុះឈ្មោះ (Register)
    # ========================================================
    @bot.message_handler(commands=['register'])
    def student_registration_start(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # ឆែកមើលក្រែងលោគាត់ធ្លាប់ចុះឈ្មោះរួចហើយ
        user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
        if user_res.data and user_res.data[0].get('student_id'):
            bot.send_message(chat_id, "ℹ️ **ប្អូនបានភ្ជាប់គណនីរួចរាល់ហើយ មិនបាច់ចុះឈ្មោះថ្មីទៀតទេបាទ!**")
            return
            
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

    # ========================================================
    # ២. មុខងារ Login ដោយវាយលេខកូដ (ឧ. DUC001)
        # ២. មុខងារ Login ដោយវាយលេខកូដ (ឧ. DUC001)
    @bot.message_handler(func=lambda message: message.text and message.text.upper().startswith("DUC"))
    def fast_login(message):
        student_id_input = message.text.strip().upper()
        telegram_id = str(message.from_user.id)
        chat_id = message.chat.id
        
        try:
            # ស្វែងរកលេខកូដសិស្សក្នុងតារាង students
            stu_res = supabase.table("students").select("*").eq("student_id", student_id_input).execute()
            
            if not stu_res.data:
                bot.reply_to(message, "❌ **លេខកូដនេះមិនត្រឹមត្រូវទេ!** សូមពិនិត្យម្តងទៀត។")
                return

            # Update ទៅតារាង users
            supabase.table("users").upsert({
                "telegram_id": telegram_id,
                "student_id": student_id_input,
                "status": "APPROVED",
                "role": "STUDENT"
            }, on_conflict="telegram_id").execute()
            
            # 🚀 បង្ហាញសារជោគជ័យ និងហៅ Menu មកបង្ហាញ
            bot.reply_to(
                message, 
                f"✅ **Login ជោគជ័យ!**\nស្វាគមន៍សិស្សកូដ `{student_id_input}`។",
                parse_mode='Markdown',
                reply_markup=helpers.main_menu('km') # ហៅ Menu មកបង្ហាញភ្លាមៗ
            )
            
        except Exception as e:
            bot.reply_to(message, f"❌ កំហុសបច្ចេកទេស៖ `{e}`")
    # 📝 មុខងារ៖ ស្ទាក់ចាប់ការចុចប៊ូតុង សុំច្បាប់
    # ========================================================
    @bot.message_handler(func=lambda m: m.text in ["📝 Submit Leave Request", "Submit Leave Request"])
    def parent_leave_request_start(message):
        user_id = message.from_user.id
        user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
        
        user_role = user_res.data[0].get('role') if user_res.data else 'PARENT'
        user_status = user_res.data[0].get('status') if user_res.data else ''
        
        if user_role == 'ADMIN' or user_status == 'APPROVED':
            supabase.table("users").update({"status": "LEAVE_MODE"}).eq("telegram_id", user_id).execute()
            bot.send_message(message.chat.id, "📝 **សូមបំពេញព័ត៌មានសុំច្បាប់តាមទម្រង់ខាងក្រោម៖**\n\n👉 **វាយបញ្ជូន៖** `ID_សិស្ស,មូលហេតុ` \n💡 *ឧទាហរណ៍៖* `DUC001,ឈឺក្បាលក្តៅខ្លួន`")
        else:
            bot.send_message(message.chat.id, "⚠️ **គណនីរបស់អ្នកមិនទាន់ត្រូវបានអនុម័ត (Approved) ឱ្យប្រើប្រាស់មុខងារនេះឡើយ!**")

    # ========================================================
    # 👁️ មុខងារ៖ ស្ទាក់ចាប់ការចុចប៊ូតុង Read Receipts & Digital Signature
    # ========================================================
    @bot.callback_query_handler(func=lambda call: call.data.startswith('readnotice_') or call.data.startswith('signnotice_'))
    def handle_notice_interactions(call):
        parent_id = call.from_user.id
        action, notice_id = call.data.split('_')
        notice_id = int(notice_id)
        
        if action == "readnotice":
            supabase.table("notice_engagements").update({"is_seen": True, "seen_at": "now()"}).eq("notice_id", notice_id).eq("parent_telegram_id", parent_id).execute()
            notice_res = supabase.table("school_notices").select("title, content").eq("id", notice_id).execute()
            bot.send_message(call.message.chat.id, f"📖 **{notice_res.data[0]['title']}**\n\n{notice_res.data[0]['content']}", parse_mode='Markdown')
            bot.answer_callback_query(call.id, "បានកត់ត្រាការអានរួចរាល់ (Seen)")

        elif action == "signnotice":
            supabase.table("notice_engagements").update({"is_acknowledged": True, "acknowledged_at": "now()"}).eq("notice_id", notice_id).eq("parent_telegram_id", parent_id).execute()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=call.message.text + "\n\n✍️ **ស្ថានភាព៖ អ្នកបានចុចយល់ព្រម (Digital Signed) រួចរាល់។**"
            )
            bot.answer_callback_query(call.id, "✅ បានចុះហត្ថលេខាឌីជីថលជោគជ័យ", show_alert=True)

    # ========================================================
    # 🔄 ដំណើរការស្ទាក់ចាប់អត្ថបទវាយចូលរបស់សិស្ស (REG_MODE / LEAVE_MODE / LOGIN)
    # ========================================================
    @bot.message_handler(func=lambda message: message.chat.type == 'private' and message.text and not message.text.startswith('/'))
    def handle_text(message):
        chat_id = message.chat.id
        user_id = message.from_user.id  
        text = message.text.strip()
        
        try:
            # ទាញទិន្នន័យអ្នកប្រើប្រាស់មកឆែក Status និង Role
            user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
            user = user_res.data[0] if user_res.data else None
            lang = user['language'] if user and user.get('language') else 'km'
            user_role = user.get('role') if user else 'PARENT'
            
            # 🔒 ----------------------------------------------------
            # 📚 មុខងារ៖ មើលកិច្ចការផ្ទះ (Homework)
            if text in ["📚 Homework", "btn_hw", "Homework"]:
                stu_id = user.get('student_id') if user else None
                
                # 🟢 ករណីទី ១៖ សម្រាប់គណនី Admin ឬគណនីតេស្ត
                if not stu_id or user_role == 'ADMIN':
                    hw_res = supabase.table("homework").select("*").order("id", desc=True).limit(5).execute()
                    if not hw_res.data:
                        bot.send_message(chat_id, "ℹ️ មិនមានទិន្នន័យកិច្ចការផ្ទះទេ។")
                        return
                    
                    for hw in hw_res.data:
                        cls = hw.get('class_level') or "មិនកំណត់"
                        hw_report = (
                            f"📋 **មុខវិជ្ជា៖ {hw.get('subject_name', 'ទូទៅ')}**\n"
                            f"🏫 **ថ្នាក់៖** `{cls}`\n"
                            f"📝 **ការណែនាំ៖** _{hw.get('description', 'គ្មាន')}_\n"
                            f"--------------------------------------------------"
                        )
                        bot.send_message(chat_id, hw_report, parse_mode='Markdown')
                
                # 🔵 ករណីទី ២៖ សម្រាប់សិស្ស (បង្ហាញតែមេរៀនចំថ្នាក់របស់គាត់)
                else:
                    stu_data = supabase.table("students").select("class_level, name").eq("student_id", stu_id).execute()
                    if not stu_data.data:
                        bot.send_message(chat_id, "⚠️ រកមិនឃើញថ្នាក់រៀនរបស់អ្នកទេ។")
                        return
                    
                    class_lvl = stu_data.data[0]['class_level']
                    stu_name = stu_data.data[0]['name']
                    
                    hw_res = supabase.table("homework").select("*").eq("class_level", class_lvl).order("id", desc=True).execute()
                    if not hw_res.data:
                        bot.send_message(chat_id, f"ℹ️ មិនមានកិច្ចការផ្ទះសម្រាប់ថ្នាក់ `{class_lvl}` ទេ។")
                        return
                    
                    bot.send_message(chat_id, f"📚 **[ កិច្ចការផ្ទះសម្រាប់៖ {stu_name} ]**\n🏫 ថ្នាក់៖ `{class_lvl}`\n--------------------------------------------------")
                    for hw in hw_res.data:
                        hw_report = (
                            f"📋 **មុខវិជ្ជា៖ {hw.get('subject_name')}**\n"
                            f"📝 **ការណែនាំ៖** _{hw.get('description', 'គ្មាន')}_\n"
                            f"📅 **ឈប់ទទួល៖** `{hw.get('deadline_at', 'មិនកំណត់')}`\n"
                            f"--------------------------------------------------"
                        )
                        bot.send_message(chat_id, hw_report, parse_mode='Markdown')
                return
                
                # 🔵 ករណីទី ២៖ សម្រាប់គណនីសិស្ស/អាណាព្យាបាលពិតប្រាកដ (ទាញទិន្នន័យចំថ្នាក់រៀន)
                stu_data = supabase.table("students").select("class_level, name").eq("student_id", stu_id).execute()
                if not stu_data.data:
                    bot.send_message(chat_id, "⚠️ រកមិនឃើញទិន្នន័យថ្នាក់រៀនរបស់សិស្សឡើយ!")
                    return
                
                class_lvl = stu_data.data[0]['class_level']
                stu_name = stu_data.data[0]['name']
                
                hw_res = supabase.table("homework").select("*").eq("class_level", class_lvl).order("id", desc=True).execute()
                if not hw_res.data:
                    bot.send_message(chat_id, f"ℹ️ **មិនទាន់មានកិច្ចការផ្ទះសម្រាប់ថ្នាក់ `{class_lvl}` នៅឡើយទេបាទ។**")
                    return
                
                bot.send_message(chat_id, f"📚 **[ របាយការណ៍កិច្ចការផ្ទះរបស់សិស្ស៖ {stu_name} ]**\n🏫 ថ្នាក់រៀន៖ `{class_lvl}`\n--------------------------------------------------\n", parse_mode='Markdown')
                
                for hw in hw_res.data:
                    hw_id = hw['id']
                    # 🟢 ៤. Insert ទិន្នន័យចូលតារាង student_submissions
                    sub_res = supabase.table("student_submissions").insert({
                        "homework_id": latest_hw['id'],       # ត្រូវគ្នាជាមួយ Column ក្នុងតារាងបង
                        "student_id": user['student_id'], 
                        "class_level": student_class,         # ទាញបានពីតារាង students ជោគជ័យ
                        "submitted_file": filename,
                        "status": "Submitted"
                        # "submitted_at" មិនចាំបាច់ដាក់ទេ បើ Supabase ដាក់ Default value ជា now()
                    }).execute()
                    
                    status_emoji = "🔴"
                    status_text = "Not Started (មិនទាន់ធ្វើ)"
                    grading_feedback = ""
                    
                    if sub_res.data:
                        submission = sub_res.data[0]
                        status_emoji = "🟢"
                        status_text = "Submitted (បានប្រគល់រួចរាល់)"
                        grade = submission.get('grade_score') 
                        feedback = submission.get('teacher_feedback') 
                        if grade is not None:
                            grading_feedback = f"\n✍️ **ពិន្ទុ៖** `{grade}/{hw.get('max_points', 100)}` \n💡 **មតិវាយតម្លៃ៖** _{feedback if feedback else 'គ្មាន'}_"
                    else:
                        try:
                            dl_time = datetime.fromisoformat(hw['deadline_at'].replace('+00:00', ''))
                            if datetime.now() > dl_time:
                                status_emoji = "❌"
                                status_text = "Overdue (ហួសកាលកំណត់)"
                        except: pass
                    
                    hw_report = (
                        f"{status_emoji} **មុខវិជ្ជា៖ {hw.get('subject_name', 'ទូទៅ')}**\n"
                        f"📝 **ការណែនាំ៖** _{hw.get('description', 'គ្មានខ្លឹមសារពិពណ៌នា')}_\n"
                        f"💯 **ពិន្ទុអតិបរមា៖** `{hw.get('max_points', 100)}`\n"
                        f"📅 **ឈប់ទទួល៖** `{hw.get('deadline_at', 'មិនកំណត់')}`\n"
                        f"📊 **ស្ថានភាព៖** *{status_text}*{grading_feedback}\n"
                        f"--------------------------------------------------"
                    )
                    bot.send_message(chat_id, hw_report, parse_mode='Markdown')
                    
                    file_url = hw.get('attachment_file')
                    file_type = hw.get('attachment_type')
                    if file_url and file_url != 'NULL':
                        try:
                            if file_type == 'photo':
                                bot.send_photo(chat_id, file_url, caption=f"🖼️ រូបភាពមេរៀនភ្ជាប់មកជាមួយ")
                            else:
                                bot.send_document(chat_id, file_url, caption=f"📄 ឯកសារ PDF កិច្ចការផ្ទះសាលា")
                        except Exception as file_err:
                            print(f"⚠️ មិនអាចទាញឯកសារមេរៀនបាន៖ {file_err}")
                return

            # 🔒 ----------------------------------------------------
            # 🏖️ មុខងារ៖ មើលថ្ងៃឈប់សម្រាក (School Holidays)
            # ----------------------------------------------------
            elif text in ["🏖️ School Holidays", "btn_hol"]:
                try:
                    hol_res = supabase.table("holidays").select("*").order("holiday_date", desc=False).execute()
                    if not hol_res.data:
                        bot.send_message(chat_id, "ℹ️ **មិនទាន់មានទិន្នន័យថ្ងៃឈប់សម្រាកនៅក្នុងប្រព័ន្ធឡើយបាទ។**")
                        return
                    
                    bot.send_message(chat_id, "🏖️ **[ សេចក្តីជូនដំណឹងអំពីថ្ងៃឈប់សម្រាកសាលា ]**\n--------------------------------------------------", parse_mode='Markdown')
                    for hol in hol_res.data:
                        event_name = hol['event_name_km'] if lang == 'km' else hol.get('event_name_en', hol['event_name_km'])
                        hol_msg = (
                            f"📅 **កាលបរិច្ឆេទ៖** `{hol['holiday_date']}`\n"
                            f"🎉 **កម្មវិធីឈប់សម្រាក៖** *{event_name}*\n"
                            f"--------------------------------------------------"
                        )
                        if hol.get('holiday_image'):
                            try:
                                bot.send_photo(chat_id, hol['holiday_image'], caption=hol_msg, parse_mode='Markdown')
                            except:
                                bot.send_message(chat_id, hol_msg, parse_mode='Markdown')
                        else:
                            bot.send_message(chat_id, hol_msg, parse_mode='Markdown')
                except Exception as e:
                    bot.send_message(chat_id, f"⚠️ Error: {e}")
                return

            # 🔒 ----------------------------------------------------
            # 📅 មុខងារ៖ មើលតារាងរៀន (Class Schedule)
            # ----------------------------------------------------
            elif text in ["📅 Class Schedule", "btn_schedule"]:
                if user_role == 'ADMIN' and not user.get('student_id'):
                    bot.send_message(chat_id, "ℹ️ **[ Admin Test Mode ]**\nប៊ូតុងតារាងរៀនដំណើរការប្រក្រតីបាទ!")
                    return
                
                stu_id = user.get('student_id')
                stu_data = supabase.table("students").select("class_level").eq("student_id", stu_id).execute()
                if not stu_data.data:
                    bot.send_message(chat_id, "⚠️ គណនីរបស់អ្នកមិនទាន់បានភ្ជាប់ជាមួយទិន្នន័យសិស្សទេ។")
                    return
                
                class_lvl = stu_data.data[0]['class_level']
                sch_res = supabase.table("schedules").select("*").eq("class_level", class_lvl).order("start_time", desc=False).execute()
                
                if not sch_res.data:
                    bot.send_message(chat_id, f"ℹ️ **មិនទាន់មានតារាងរៀនសម្រាប់ថ្នាក់ `{class_lvl}` ឡើយបាទ។**")
                    return
                
                sch_msg = f"📅 **[ តារាងរៀនប្រចាំសប្ដាហ៍ - ថ្នាក់៖ {class_lvl} ]**\n--------------------------------------------------\n"
                for sch in sch_res.data:
                    sch_msg += (
                        f"🔹 **ថ្ងៃសិក្សា៖** `{sch['study_day']}`\n"
                        f"📖 **មុខវិជ្ជា៖** *{sch['subject_name']}*\n"
                        f"⏰ **ម៉ោងសិក្សា៖** `{sch['start_time']} - {sch['end_time']}`\n"
                        f"--------------------------------------------------\n"
                    )
                bot.send_message(chat_id, sch_msg, parse_mode='Markdown')
                return

            # 🔒 ----------------------------------------------------
            # 📤 មុខងារ៖ បើក Mode ត្រៀមប្រគល់កិច្ចការផ្ទះ (Upload Homework Mode)
            # ----------------------------------------------------
            elif text in ["📤 Upload Homework", "Upload Homework"]:
                if user_role == 'ADMIN' and not user.get('student_id'):
                    bot.send_message(chat_id, "ℹ️ **[ Admin Test Mode ]**\nប៊ូតុងប្រគល់កិច្ចការដំណើរការប្រក្រតីបាទ!")
                    return
                
                supabase.table("users").update({"status": "UPLOAD_MODE"}).eq("telegram_id", user_id).execute()
                bot.send_message(chat_id, "📤 **[ របៀបប្រគល់កិច្ចការផ្ទះអនឡាញ ]**\n--------------------------------------------------\n👉 ផ្ញើកិច្ចការជាប្រភេទ **រូបភាព (Picture)** ឬឯកសារ **PDF (Document)** ផ្ទាល់ចូលក្នុងនេះភ្លាមៗបានបាទ។")
                return

            # 🔒 ----------------------------------------------------
            # 🛡️ ករណីពិសេស៖ សម្រាប់ Admin ចុចចាកចេញ ឬប្តូរភាសា (Admin Bypass)
            # ----------------------------------------------------
            if user_role == 'ADMIN':
                if text in ["🌐 Change Language (ប្តូរភាសា)", "btn_lang"]:
                    bot.send_message(chat_id, f"ℹ️ **លោកគ្រូ/Admin កំពុងចុចតេស្តប៊ូតុង៖** `{text}`")
                    return
                elif text in ["🔙 Logout (ចាកចេញពីប្រព័ន្ធ)", "btn_logout"]:
                    bot.send_message(chat_id, "🔙 **បានចាកចេញពីផ្ទាំងសិស្ស! ត្រឡប់មកកាន់ផ្ទាំងគ្រប់គ្រង Admin វិញ។**")
                    helpers.send_admin_panel(bot, chat_id)
                    return

            # ឆែកមើលក្រែងលោជា Admin កំពុងចុចតេស្តប៊ូតុងផ្សេងៗ (Logic ដើមរបស់បង)
            if text in ["📚 Homework (កិច្ចការផ្ទះ)", "btn_hw", "🏖️ School Holidays (ថ្ងៃឈប់សម្រាក)", "btn_hol", "📅 Class Schedule (តារាងរៀន)", "btn_schedule", "🌐 Change Language (ប្តូរភាសា)", "btn_lang"]:
                bot.send_message(chat_id, f"ℹ️ លោកគ្រូ/Admin កំពុងចុចតេស្តប៊ូតុង៖ `{text}` (មុខងារនេះដំណើរការប្រក្រតី)")
                return
            
            # ----------------------------------------------------
            # 🔥 លំដាប់ទី ១៖ ករណីសិស្សថ្មីកំពុងបំពេញព័ត៌មានចុះឈ្មោះ (REG_MODE)
            # ----------------------------------------------------
            if user and user['status'] == 'REG_MODE':
                try:
                    parts = text.split(',')
                    if len(parts) < 3:
                        raise ValueError("ទិន្នន័យមិនគ្រប់គ្រាន់")
                        
                    s_name, s_gender, s_class = parts[0].strip(), parts[1].strip().upper(), parts[2].strip().upper()
                    temp_id = f"PENDING_{user_id}"
                    
                    supabase.table("students").upsert({
                        "student_id": temp_id, 
                        "name": s_name, 
                        "gender": s_gender, 
                        "class_level": s_class,
                        "parent_telegram_id": user_id
                    }, on_conflict="student_id").execute()
                    
                    supabase.table("users").update({"status": "WAIT_APPROVE"}).eq("telegram_id", user_id).execute()
                    bot.send_message(chat_id, "✅ **ការស្នើសុំចុះឈ្មោះត្រូវបានបញ្ជូនជោគជ័យ!**\nសូមរង់ចាំការពិនិត្យ និងអនុម័ត (Approve) ពីលោកគ្រូ/Admin ជាមុនសិនបាទ।")
                    
                    try:
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
                    class_lvl = stu_res.data[0]['class_level'] if stu_res.data else 'UNKNOWN'
                    
                    supabase.table("attendance").insert({
                        "student_id": sid, 
                        "class_level": class_lvl, 
                        "status": "EXCUSED", 
                        "leave_requested_online": True, 
                        "leave_approval_status": "PENDING", 
                        "reason": reason
                    }).execute()
                    
                    supabase.table("users").update({"status": "APPROVED"}).eq("telegram_id", user_id).execute()
                    
                    bot.send_message(chat_id, "✅ **លិខិតសុំច្បាប់អនឡាញត្រូវបានបញ្ជូនទៅកាន់លោកគ្រូហើយ**", reply_markup=helpers.main_menu(lang))
                    helpers.notify_all_admins(bot, f"🔔 **មានលិខិតសុំច្បាប់អនឡាញថ្មី៖**\n🆔 ID សិស្ស៖ `{sid}`\n📝 មូលហេតុ៖ _{reason}_")
                except Exception as leave_err:
                    print(f"Leave Request Error: {leave_err}")
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

    # ========================================================
    # 📥 មុខងារ៖ ទទួលឯកសារ UPLOAD កិច្ចការផ្ទះ (🔐 ដេកនៅកម្រិតស្មើគ្នាជាមួយ handle_text ក្នុង register_student_handlers)
    # ========================================================
    # 📥 មុខងារទទួលឯកសារ UPLOAD កិច្ចការផ្ទះ (ជួសជុល៖ ទាញ Class Level ពីតារាង students)
  # ========================================================
    # 📥 មុខងារទទួលឯកសារ UPLOAD កិច្ចការផ្ទះ (ជួសជុលការទាញ Class Level ពីតារាង students)
    # ========================================================
    @bot.message_handler(content_types=['photo', 'document'])
    def handle_homework_upload(message):
        user_id = message.from_user.id
        print("DEBUG: កំពុងដំណើរការ Upload homework...")
        chat_id = message.chat.id
        
        try:
            # ១. ឆែកមើល User និងទាញ student_id
            user_res = supabase.table("users").select("student_id").eq("telegram_id", user_id).execute()
            user = user_res.data[0] if user_res.data else None
            
            if user and user.get('student_id'):
                # ២. ទាញយក class_level ផ្ទាល់ពីតារាង students របស់សិស្សម្នាក់នោះ
                stu_res = supabase.table("students").select("class_level").eq("student_id", user['student_id']).execute()
                if not stu_res.data:
                    bot.send_message(chat_id, "⚠️ រកមិនឃើញទិន្នន័យថ្នាក់រៀនរបស់សិស្ស។")
                    return
                
                student_class = stu_res.data[0]['class_level']
                
                # ៣. ទាញយក Homework ID ចុងក្រោយបង្អស់ (ដោយមិនហៅ class_level ពី homework ទៀតទេ)
                hw_res = supabase.table("homework").select("id").order("id", desc=True).limit(1).execute()
                
                if hw_res.data:
                    latest_hw_id = hw_res.data[0]['id']
                    
                    # ៤. ដំណើរការ File
                    file_id = message.photo[-1].file_id if message.content_type == 'photo' else message.document.file_id
                    ext = "jpg" if message.content_type == 'photo' else message.document.file_name.split('.')[-1]
                    filename = f"stu_{user['student_id']}_{message.message_id}.{ext}"
                    full_path = f"student_assignments/{filename}"
                    
                    if not os.path.exists('student_assignments'): os.makedirs('student_assignments')
                    file_info = bot.get_file(file_id)
                    downloaded = bot.download_file(file_info.file_path)
                    with open(full_path, 'wb') as f: f.write(downloaded)
                    
                    # ៥. Insert ចូល student_submissions ដោយប្រើ student_class ដែលទាញបានពីតារាង students
                    supabase.table("student_submissions").insert({
                        "homework_id": latest_hw_id, 
                        "student_id": user['student_id'], 
                        "class_level": student_class, # យកពីតារាង students មកប្រើ
                        "submitted_file": filename,
                        "status": "Submitted"
                    }).execute()
                    
                    bot.reply_to(message, f"📥 ប្រគល់កិច្ចការជោគជ័យ! (ថ្នាក់៖ {student_class})")
                else:
                    bot.reply_to(message, "ℹ️ មិនមានកិច្ចការផ្ទះណាមួយក្នុងប្រព័ន្ធ។")
            else:
                bot.reply_to(message, "⚠️ សូមភ្ជាប់គណនីសិស្សជាមុនសិន។")
        except Exception as e:
            print(f"❌ API Error: {e}")
            bot.reply_to(message, f"❌ កំហុស៖ {e}")
            # 🚪 ----------------------------------------------------
            # 🚀 មុខងារ LOGOUT (ចាកចេញពីប្រព័ន្ធ)
            # ----------------------------------------------------
            input_text = text.strip() if text else ""
            if text in ["Logout", "btn_logout", "Logout", "ចាកចេញពីប្រព័ន្ធ"]:
                if user and user.get('student_id'):
                    # កែប្រែទិន្នន័យក្នុងតារាង users ឱ្យទៅជាទទេវិញ
                    supabase.table("users").update({
                        "student_id": None,
                        "status": "NEW",
                        "role": "PARENT"
                    }).eq("telegram_id", user_id).execute()
                    
                    # លុបផ្ទាំងប៊ូតុង Menu ចាស់ចោល កុំឱ្យគាត់ចុចទៀត
                    remove_keyboard = types.ReplyKeyboardRemove()
                    bot.send_message(
                        chat_id, 
                        "🔒 **លោកអ្នកបានចាកចេញពីប្រព័ន្ធជោគជ័យហើយ!**\n\n👉 ប្រសិនបើចង់ចូលប្រើប្រាស់ឡើងវិញ សូមវាយបញ្ចូល **លេខកូដសិស្ស** ម្តងទៀត (ឧទាហរណ៍៖ `DUC001`)។", 
                        parse_mode='Markdown',
                        reply_markup=remove_keyboard
                    )
                else:
                    bot.send_message(chat_id, "ℹ️ គណនីរបស់អ្នកមិនទាន់បានចូលប្រើប្រាស់ក្នុងប្រព័ន្ធនៅឡើយទេ។")
                return
