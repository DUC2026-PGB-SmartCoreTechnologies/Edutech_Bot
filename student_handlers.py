import os
import logging
from telebot import types
from datetime import datetime
import helpers

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
        
        user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
        if user_res.data and user_res.data[0].get('student_id'):
            bot.send_message(chat_id, "ℹ️ **ប្អូនបានភ្ជាប់គណនីរួចរាល់ហើយ មិនបាច់ចុះឈ្មោះថ្មីទៀតទេបាទ!**")
            return
            
        try:
            supabase.table("users").upsert({"telegram_id": user_id, "status": "REG_MODE", "language": "km"}, on_conflict="telegram_id").execute()
            reg_msg = (
                "📝 **[ ទម្រង់ស្នើសុំចុះឈ្មោះចូលរៀនអនឡាញ ]**\n"
                "--------------------------------------------------\n"
                "Commercial៖ សូមប្អូនបំពេញព័ត៌មានផ្ទាល់ខ្លួន តាមទម្រង់ខាងក្រោមឱ្យបានត្រឹមត្រូវ៖\n\n"
                "👉 **សូមវាយបញ្ជូន៖** `ឈ្មោះសិស្ស,ភេទ(M ឬ F),ថ្នាក់រៀន`\n"
                "✍️ គំរូត្រឹមត្រូវ៖ `សុខ ភារម្យ,M,Grade12_A`"
            )
            bot.send_message(chat_id, reg_msg, parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Error: {e}")

    # ========================================================
    # ២. មុខងារ Login ដោយវាយលេខកូដលឿន (ឧ. DUC001)
    # ========================================================
    @bot.message_handler(func=lambda message: message.text and message.text.upper().startswith("DUC"))
    def fast_login(message):
        student_id_input = message.text.strip().upper()
        telegram_id = message.from_user.id
        chat_id = message.chat.id
        
        try:
            stu_res = supabase.table("students").select("*").eq("student_id", student_id_input).execute()
            
            if not stu_res.data:
                bot.reply_to(message, "❌ **លេខកូដនេះមិនត្រឹមត្រូវទេ!** សូមពិនិត្យម្តងទៀត។")
                return

            supabase.table("users").upsert({
                "telegram_id": telegram_id,
                "student_id": student_id_input,
                "status": "APPROVED",
                "role": "STUDENT"
            }, on_conflict="telegram_id").execute()
            
            bot.reply_to(
                message, 
                f"✅ **Login ជោគជ័យ!**\nស្វាគមន៍សិស្សកូដ `{student_id_input}`។",
                parse_mode='Markdown',
                reply_markup=helpers.main_menu('km')
            )
            
        except Exception as e:
            bot.reply_to(message, f"❌ កំហុសបច្ចេកទេស៖ `{e}`")

    # ========================================================
    # ៣. មុខងារសុំច្បាប់ (Leave Request)
    # ========================================================
    @bot.message_handler(func=lambda m: m.text in ["📝 Submit Leave Request (សុំច្បាប់)", "Submit Leave Request (សុំច្បាប់)"])
    def parent_leave_request_start(message):
        user_id = message.from_user.id
        user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
        
        user_role = user_res.data[0].get('role') if user_res.data else 'PARENT'
        user_status = user_res.data[0].get('status') if user_res.data else ''
        
        if user_role == 'ADMIN' or user_status == 'APPROVED':
            supabase.table("users").update({"status": "LEAVE_MODE"}).eq("telegram_id", user_id).execute()
            bot.send_message(message.chat.id, "📝 **សូមបំពេញព័ត៌មានសុំច្បាប់តាមទម្រង់ខាងក្រោម៖**\n\n👉 **\nវាយបញ្ជូន៖** `ID_សិស្ស,មូលហេតុ` \n💡 *ឧទាហរណ៍៖* `DUC001,ឈឺក្បាលក្តៅខ្លួន`")
        else:
            bot.send_message(message.chat.id, "⚠️ **គណនីរបស់អ្នកមិនទាន់ត្រូវបានអនុម័ត (Approved) ឱ្យប្រើប្រាស់មុខងារនេះឡើយ!**")

    # ========================================================
    # ៤. មុខងារអានសេចក្តីជូនដំណឹង (Notice Interactions)
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
    # ៥. ដំណើរការស្ទាក់ចាប់អត្ថបទវាយចូលរបស់សិស្ស (Text Handler)
    # ========================================================
    @bot.message_handler(func=lambda message: message.chat.type == 'private' and message.text and not message.text.startswith('/'))
    def handle_text(message):
        chat_id = message.chat.id
        user_id = message.from_user.id  
        text = message.text.strip()
        
        try:
            user_res = supabase.table("users").select("*").eq("telegram_id", user_id).execute()
            user = user_res.data[0] if user_res.data else None
            lang = user['language'] if user and user.get('language') else 'km'
            user_role = user.get('role') if user else 'PARENT'
            
            # 🔒 [ មុខងារ៖ មើលកិច្ចការផ្ទះ (Homework View) ]
            if text in ["📚 Homework (កិច្ចការផ្ទះ)", "btn_hw", "Homework (កិច្ចការផ្ទះ)"]:
                stu_id = user.get('student_id') if user else None
                
                # 🟢 ករណី៖ Admin ចូលមកមើលតេស្ត
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
                
                # 🔵 ករណី៖ សិស្សពិតប្រាកដចូលមើលកិច្ចការផ្ទះ
                else:
                    stu_data = supabase.table("students").select("class_level, name").eq("student_id", stu_id).execute()
                    if not stu_data.data:
                        bot.send_message(chat_id, "⚠️ រកមិនឃើញថ្នាក់រៀនរបស់អ្នកទេ។")
                        return
                    
                    class_lvl = stu_data.data[0]['class_level']
                    stu_name = stu_data.data[0]['name']
                    
                    hw_res = supabase.table("homework").select("*").eq("class_level", class_lvl).order("id", desc=True).execute()
                    if not hw_res.data:
                        bot.send_message(chat_id, f"ℹ️ **មិនទាន់មានកិច្ចការផ្ទះសម្រាប់ថ្នាក់ `{class_lvl}` នៅឡើយទេបាទ។**")
                        return
                    
                    bot.send_message(chat_id, f"📚 **[ របាយការណ៍កិច្ចការផ្ទះរបស់សិស្ស៖ {stu_name} ]**\n🏫 ថ្នាក់រៀន៖ `{class_lvl}`\n--------------------------------------------------")
                    
                    for hw in hw_res.data:
                        # ឆែកស្ថានភាពប្រគល់កិច្ចការពីតារាង student_submissions របស់សិស្សម្នាក់នេះ
                        sub_check = supabase.table("student_submissions").select("*").eq("homework_id", hw['id']).eq("student_id", stu_id).execute()
                        
                        status_emoji = "🔴"
                        status_text = "Not Started (មិនទាន់ធ្វើ)"
                        grading_feedback = ""
                        
                        if sub_check.data:
                            submission = sub_check.data[0]
                            status_emoji = "🟢"
                            status_text = "Submitted (បានប្រគល់រួចរាល់)"
                            grade = submission.get('grade_score') 
                            feedback = submission.get('teacher_feedback') 
                            if grade is not None:
                                grading_feedback = f"\n✍️ **ពិន្ទុ៖** `{grade}/{hw.get('max_points', 100)}` \n💡 **មតិវាយតម្លៃ៖** _{feedback if feedback else 'គ្មាន'}_"
                        else:
                            if hw.get('deadline_at'):
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
                        
                        # ទាញផ្ញើឯកសារមេរៀនភ្ជាប់មកជាមួយ (បើមាន)
                        file_url = hw.get('attachment_file')
                        file_type = hw.get('attachment_type')
                        if file_url and file_url != 'NULL' and file_url.startswith('http'):
                            try:
                                if file_type == 'photo':
                                    bot.send_photo(chat_id, file_url, caption=f"🖼️ រូបភាពមេរៀនភ្ជាប់មកជាមួយ")
                                else:
                                    bot.send_document(chat_id, file_url, caption=f"📄 ឯកសារ PDF កិច្ចការផ្ទះសាលា")
                            except Exception as file_err:
                                print(f"⚠️ មិនអាចទាញឯកសារមេរៀនបាន៖ {file_err}")
                return

            # 🔒 [ មុខងារ៖ មើលថ្ងៃឈប់សម្រាក (School Holidays) ]
            elif text in ["🏖️ School Holidays (ថ្ងៃឈប់សម្រាក)", "btn_hol"]:
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
                        if hol.get('holiday_image') and hol['holiday_image'].startswith('http'):
                            try:
                                bot.send_photo(chat_id, hol['holiday_image'], caption=hol_msg, parse_mode='Markdown')
                            except:
                                bot.send_message(chat_id, hol_msg, parse_mode='Markdown')
                        else:
                            bot.send_message(chat_id, hol_msg, parse_mode='Markdown')
                except Exception as e:
                    bot.send_message(chat_id, f"⚠️ Error: {e}")
                return

            # 🔒 [ មុខងារ៖ មើលតារាងរៀន (Class Schedule) ]
            elif text in ["📅 Class Schedule (តារាងរៀន)", "btn_schedule"]:
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

            # 🔒 [ មុខងារ៖ បើក Mode ត្រៀមប្រគល់កិច្ចការផ្ទះ ]
            elif text in ["📤 Upload Homework (ប្រគល់កិច្ចការ)", "Upload Homework (ប្រគល់កិច្ចការ)"]:
                if user_role == 'ADMIN' and not user.get('student_id'):
                    bot.send_message(chat_id, "ℹ️ **[ Admin Test Mode ]**\nប៊ូតុងប្រគល់កិច្ចការដំណើរការប្រក្រតីបាទ!")
                    return
                
                supabase.table("users").update({"status": "UPLOAD_MODE"}).eq("telegram_id", user_id).execute()
                bot.send_message(chat_id, "📤 **[ របៀបប្រគល់កិច្ចការផ្ទះអនឡាញ ]**\n--------------------------------------------------\n👉 សូមផ្ញើកិច្ចការជាប្រភេទ **រូបភាព (Picture)** ឬឯកសារ **PDF (Document)** ផ្ទាល់ចូលក្នុងនេះភ្លាមៗបានបាទ។")
                return

            # 🔒 [ ករណីពិសេស៖ Admin Bypass ]
            if user_role == 'ADMIN':
                if text in ["🌐 Change Language (ប្តូរភាសា)", "btn_lang"]:
                    bot.send_message(chat_id, f"ℹ️ **លោកគ្រូ/Admin កំពុងចុចតេស្តប៊ូតុង៖** `{text}`")
                    return
                elif text in ["🔙 Logout (ចាកចេញពីប្រព័ន្ធ)", "btn_logout"]:
                    bot.send_message(chat_id, "🔙 **បានចាកចេញពីផ្ទាំងសិស្ស! ត្រឡប់មកកាន់ផ្ទាំងគ្រប់គ្រង Admin វិញ biographies។**")
                    helpers.send_admin_panel(bot, chat_id)
                    return

            # ----------------------------------------------------
            # 🔥 លំដាប់ទី ១៖ ករណីសិស្សថ្មីបំពេញព័ត៌មានចុះឈ្មោះ (REG_MODE)
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
                    bot.send_message(chat_id, "✅ **ការស្នើសុំចុះឈ្មោះត្រូវបានបញ្ជូនជោគជ័យ!**\nសូមរង់ចាំការពិនិត្យ និងអនុម័ត (Approve) ពីលោកគ្រូ/Admin ជាមុនសិនបាទ។")
                    
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
                    bot.send_message(chat_id, "⚠️ ទម្រង់បំពេញខុសហើយប្អូន! គំរូ៖ `ឈ្មោះសិស្ស,M,Grade12_A`")
                return

            # ----------------------------------------------------
            # 🟢 លំដាប់ទី ២៖ ការបំពេញច្បាប់អនឡាញ (LEAVE_MODE)
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
                    bot.send_message(chat_id, "⚠️ ទម្រង់ខុស! គំរូ៖ `ID_សិស្ស,មូលហេតុ`")
                return

            # ----------------------------------------------------
            # 🔴 លំដាប់ទី ៣៖ គណនីទទេស្អាត (NEW) វាយ ID សិស្ស ដើម្បី LOGIN ភ្ជាប់ប្រព័ន្ធ
            # ----------------------------------------------------
            if not user or not user.get('student_id'):
                stu_check = supabase.table("students").select("*").eq("student_id", text.upper()).execute()
                if stu_check.data:
                    supabase.table("users").update({"student_id": text.upper(), "status": "APPROVED", "app_installed": 1}).eq("telegram_id", user_id).execute()
                    supabase.table("students").update({"parent_telegram_id": user_id}).eq("student_id", text.upper()).execute()
                    bot.send_message(chat_id, f"✅ ភ្ជាប់ទំនាក់ទំនងជាមួយសិស្សឈ្មោះ៖ *{stu_check.data[0]['name']}* ជោគជ័យ!", parse_mode='Markdown', reply_markup=helpers.main_menu(lang))
                else:
                    bot.reply_to(message, "❌ រកមិនឃើញលេខសម្គាល់សិស្សនេះទេ! សូមវាយបញ្ជា `/register` បើចង់ចុះឈ្មោះថ្មី។")
                    
        except Exception as e:
            print(f"Text Handler Error: {e}")

    # ========================================================
    # 📥 ៦. មុខងារទទួលឯកសារ UPLOAD កិច្ចការផ្ទះ
    # ========================================================
    @bot.message_handler(content_types=['photo', 'document'])
    def handle_homework_upload(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        try:
            user_res = supabase.table("users").select("student_id, language").eq("telegram_id", user_id).execute()
            user = user_res.data[0] if user_res.data else None
            lang = user['language'] if user and user.get('language') else 'km'
            
            if user and user.get('student_id'):
                stu_res = supabase.table("students").select("class_level, name").eq("student_id", user['student_id']).execute()
                if not stu_res.data:
                    bot.send_message(chat_id, "⚠️ រកមិនឃើញទិន្នន័យថ្នាក់រៀនរបស់សិស្ស។")
                    return
                
                student_class = stu_res.data[0]['class_level']
                student_name = stu_res.data[0]['name']
                
                # ទាញយក Homework ID ចុងក្រោយបង្អស់ដែលត្រូវនឹងថ្នាក់របស់សិស្សម្នាក់នោះ
                hw_res = supabase.table("homework").select("id, deadline_at").eq("class_level", student_class).order("id", desc=True).limit(1).execute()
                
                if hw_res.data:
                    latest_hw = hw_res.data[0]
                    latest_hw_id = latest_hw['id']
                    
                    # ឆែកមើលក្រែងលោហួស Deadline_at របស់មេរៀននោះ
                    if latest_hw.get('deadline_at'):
                        try:
                            dl_time = datetime.fromisoformat(latest_hw['deadline_at'].replace('+00:00', ''))
                            if datetime.now() > dl_time:
                                supabase.table("users").update({"status": "APPROVED"}).eq("telegram_id", user_id).execute()
                                bot.reply_to(message, "❌ **មិនអាចប្រគល់បានទេ!** កិច្ចការផ្ទះនេះបានហួសកាលកំណត់ (Overdue) ហើយ។", reply_markup=helpers.main_menu(lang))
                                return
                        except: pass
                    
                    # ដំណើរការ File Download
                    file_id = message.photo[-1].file_id if message.content_type == 'photo' else message.document.file_id
                    ext = "jpg" if message.content_type == 'photo' else message.document.file_name.split('.')[-1]
                    filename = f"stu_{user['student_id']}_{message.message_id}.{ext}"
                    full_path = f"student_assignments/{filename}"
                    
                    if not os.path.exists('student_assignments'): 
                        os.makedirs('student_assignments')
                        
                    file_info = bot.get_file(file_id)
                    downloaded = bot.download_file(file_info.file_path)
                    with open(full_path, 'wb') as f: 
                        f.write(downloaded)
                    
                    # Insert ចូលតារាង student_submissions
                    sub_res = supabase.table("student_submissions").insert({
                        "homework_id": latest_hw_id, 
                        "student_id": user['student_id'], 
                        "class_level": student_class,
                        "submitted_file": filename,
                        "status": "Submitted"
                    }).execute()
                    
                    submission_id = sub_res.data[0]['id'] if sub_res.data else "N/A"
                    
                    # ត្រឡប់ Status អ្នកប្រើប្រាស់មកធម្មតាវិញ
                    supabase.table("users").update({"status": "APPROVED"}).eq("telegram_id", user_id).execute()
                    bot.reply_to(message, f"📥 **ប្រគល់កិច្ចការផ្ទះជោគជ័យ!**\n🆔 Submission ID: `{submission_id}`", reply_markup=helpers.main_menu(lang))
                    
                    # ផ្ញើសារដំណឹង (Alert) ទៅកាន់លោកគ្រូ/Admin ភ្លាមៗ
                    admin_alert = f"🔔 **សិស្សប្រគល់កិច្ចការផ្ទះថ្មី៖**\n👤 ឈ្មោះ៖ {student_name}\n🏫 ថ្នាក់៖ {student_class}\n🆔 Submission ID: `{submission_id}`\n\n👉 លោកគ្រូដាក់ពិន្ទុ៖ `/grade {submission_id},ពិន្ទុ,មតិវាយតម្លៃ`"
                    helpers.notify_all_admins(bot, admin_alert, attachment=full_path, is_photo=(message.content_type == 'photo'))
                else:
                    bot.reply_to(message, f"ℹ️ មិនមានកិច្ចការផ្ទះណាមួយដែលត្រូវប្រគល់សម្រាប់ថ្នាក់ `{student_class}` ឡើយបាទ។")
            else:
                bot.reply_to(message, "⚠️ សូមភ្ជាប់គណនីសិស្ស ឬវាយលេខ ID សិស្សជាមុនសិន។")
        except Exception as e:
            print(f"❌ API Upload Error: {e}")
            bot.reply_to(message, f"❌ កំហុសបច្ចេកទេស៖ {e}")
