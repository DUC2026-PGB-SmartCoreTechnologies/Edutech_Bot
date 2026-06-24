import telebot
from telebot import types
from datetime import datetime
import threading
# បង្កើតអថេរជាសកលសម្រាប់ងាយស្រួលទាញទិន្នន័យ
_bot = None
_supabase = None

# ========================================================
# 👑 មុខងារ៖ Admin វាយ /login
# ========================================================
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
                    bot.reply_to(message, "❌ **សុំទោស!** ប្រព័ន្ធគ្រប់គ្រងសាលា DUC មាន Admin មេរួចរាល់ហើយ។")
                    return
        except Exception as e:
            print(f"❌ Supabase Admin Lock Check Error: {e}")
            bot.reply_to(message, "❌ មានបញ្ហាបច្ចេកទេសក្នុងការឆែកមើលសិទ្ធិ។")
            return

        text_input = message.text.strip()[6:].strip()
        ADMIN_MASTER_PASSWORD = "DUC_Admin@2026"
        
        if not text_input:
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ Admin!**\nសូមវាយ៖ `/login លេខសម្ងាត់មេ`", parse_mode='Markdown')
            return
            
        if text_input != ADMIN_MASTER_PASSWORD:
            bot.reply_to(message, "❌ **លេខសម្ងាត់ Admin មិនត្រឹមត្រូវទេ!**")
            return
            
        try:
            supabase.table("users").upsert({
                "telegram_id": user_id,
                "role": "ADMIN",
                "status": "APPROVED",
                "language": "km"
            }, on_conflict="telegram_id").execute()
            
            admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            admin_menu.add("➕ បង្កើតគណនីគ្រូ", "📋 មើលបញ្ជីគ្រូ","👁️ ផ្ទាំងសិស្ស (Student Panel)", "🔙 ចាកចេញ (Logout)")
            
            bot.send_message(chat_id, "🟢 **ផ្ទៀងផ្ទាត់សិទ្ធិ Admin មេជោគជ័យ!**", parse_mode='Markdown')
            
            import helpers
            helpers.send_admin_panel(bot, chat_id)
            
            bot.send_message(chat_id, "👑 **លោកអ្នកក៏អាចប្រើប្រាស់ ប៊ូតុង Menu ខាងក្រោម នេះបានផងដែរ៖**", reply_markup=admin_menu, parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❌ មិនអាចបើកផ្ទាំង Admin Panel បានទេ៖ `{e}`")
# ===================================================================================
    # 🎛️ មុខងារ៖ ស្ទាក់ចាប់ការចុចប៊ូតុង Inline Dashboard ទាំងអស់
    # ===================================================================================
    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_system_inline_clicks(call):
        chat_id = call.message.chat.id
        action = call.data
        user_id = call.from_user.id

        try:
            bot.answer_callback_query(call.id)
        except:
            pass

        try:
            # 🟢 បើជាប៊ូតុងសកម្មភាពរហ័សរបស់សិស្ស/គ្រូ
            if action.startswith('view_students:'):
                callback_view_students(call)
                return
            elif action.startswith('view_dept:'):
                callback_view_dept(call)
                return
            elif action.startswith('view_teacher:'):
                callback_view_teacher(call)
                return
            elif action.startswith('grh_'):
                handle_grade_button_click(call)
                return
            elif action.startswith('ack_'):
                bot.answer_callback_query(call.id, "✅ លោកអ្នកបានចុចទទួលដឹងឮរួចរាល់!", show_alert=True)
                return

            # 🔒 បញ្ជីគ្រាប់ចុច Admin
            admin_buttons = ["school_stats", "hw_analytics", "list_classes", "list_teachers", "list_depts", "checkreq", "approve", "addstu", "addteacher", "adddiscipline", "grade", "addnotice","addholiday"]

            if action in admin_buttons:
                is_valid_admin = False
                
                # 🔄 ដំណោះស្រាយ៖ បំប្លែង user_id ទៅជាលេខ (int) ឱ្យស៊ីគ្នាជាមួយប្រភេទដាតាបេស Supabase
                try:
                    db_user_id = int(user_id) 
                except:
                    db_user_id = user_id

                # 🔄 ជំហានទី ១៖ ឆែកក្នុងតារាង "admins"
                try:
                    admin_check = supabase.table("admins").select("role").eq("telegram_id", db_user_id).execute()
                    if admin_check.data and str(admin_check.data[0].get('role')).upper() in ['SUPER_ADMIN', 'ADMIN']:
                        is_valid_admin = True
                except:
                    pass

                # 🔄 ជំហានទី ២៖ បើមិនឃើញ ឆែកក្នុងតារាង "users"
                if not is_valid_admin:
                    try:
                        user_check = supabase.table("users").select("role").eq("telegram_id", db_user_id).execute()
                        if user_check.data and str(user_check.data[0].get('role')).upper() in ['SUPER_ADMIN', 'ADMIN']:
                            is_valid_admin = True
                    except:
                        pass

                # ❌ បើរកមិនឃើញសិទ្ធិ Admin ទេ គឺបដិសេធ
                if not is_valid_admin:
                    bot.answer_callback_query(call.id, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិប្រើប្រាស់មុខងារនេះឡើយ។", show_alert=True)
                    return

                # 📊 ហៅមុខងារបញ្ជា (លែងគាំង លែងលោតសារក្រហម)
                if action == "school_stats": school_stats_command(call.message)
                elif action == "hw_analytics": hw_analytics_command(call.message)
                elif action == "list_classes": list_classes_command(call.message)
                elif action == "list_teachers": list_teachers_command(call.message)
                elif action == "list_depts": list_depts_command(call.message)
                elif action == "checkreq": check_requests_command(call.message)
                elif action == "approve":
                    bot.send_message(chat_id, "🟢 **[ របៀបអនុម័ត / Approve សិស្ស ]**\nសូមវាយបញ្ចូល៖ `/approve លេខTelegramID, លេខIDសិស្ស`", parse_mode='Markdown')
                elif action == "addstu": add_student_wizard(call.message)
                elif action == "addteacher": add_teacher_wizard(call.message)
                elif action == "adddiscipline": add_discipline_wizard(call.message)
                elif action == "grade": grade_homework_wizard(call.message)
                elif action == "addnotice": add_notice_wizard(call.message)
                elif action == "addholiday": add_holiday_wizard(call.message)

        except Exception as e:
            print(f"❌ Error inside callback handler: {e}")

    # ========================================================
    # 👩‍🏫 មុខងារ៖ គ្រូ Login
    # ========================================================
    @bot.message_handler(commands=['tlogin'])
    def teacher_login_by_id_and_password(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text.strip()[7:].strip()
        
        if not text or len(text.split(',')) < 2:
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយលោកគ្រូ!**\nសូមវាយ៖ `/tlogin ID_គ្រូ,លេខសម្ងាត់`", parse_mode='Markdown')
            return
            
        try:
            parts = text.split(',')
            teacher_id_input = parts[0].strip()
            password_input = parts[1].strip()
            
            t_res = supabase.table("teachers").select("*").eq("teacher_id", teacher_id_input).execute()
            if not t_res.data:
                bot.reply_to(message, f"❌ **រកមិនឃើញ ID `{teacher_id_input}` ឡើយ។**")
                return
                
            teacher_data = t_res.data[0]
            if password_input != teacher_data.get('password'):
                bot.reply_to(message, "❌ **លេខសម្ងាត់គ្រូបង្រៀន មិនត្រឹមត្រូវទេ!**")
                return
                
            supabase.table("teachers").update({"telegram_id": user_id}).eq("teacher_id", teacher_id_input).execute()
            supabase.table("users").upsert({"telegram_id": user_id, "status": "APPROVED", "role": "TEACHER", "language": "km"}, on_conflict="telegram_id").execute()
            
            teacher_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            teacher_menu.add("📚 ដាក់កិច្ចការផ្ទះ (Add HW)", "📊 មើលវត្តមានសិស្ស", "✍️ ដាក់ពិន្ទុសិស្ស (Grade)", "🔙 ចាកចេញ (Logout)")
            bot.send_message(chat_id, f"👩‍🏫 **ស្វាគមន៍លោកគ្រូ-អ្នកគ្រូ ចូលកាន់ប្រព័ន្ធ DUC**", reply_markup=teacher_menu)
        except Exception as e:
            print(f"❌ Teacher Login Error: {e}")

    # ========================================================
    # 🎛️ មុខងារ៖ ស្ទាក់ចាប់ពេលចុចប៊ូតុង Menu ធំៗរបស់គ្រូ/Admin
    # ========================================================
    @bot.message_handler(func=lambda message: message.text in ["📚 ដាក់កិច្ចការផ្ទះ (Add HW)", "📊 មើលវត្តមានសិស្ស", "✍️ ដាក់ពិន្ទុសិស្ស (Grade)", "🔙 ចាកចេញ (Logout)", "➕ បង្កើតគណនីគ្រូ", "📋 មើលបញ្ជីគ្រូ"])
    def handle_teacher_and_admin_menu_clicks(message):
        chat_id = message.chat.id
        user_text = message.text
        
        if user_text == "📚 ដាក់កិច្ចការផ្ទះ (Add HW)": add_homework_wizard_start(message)
        elif user_text == "📊 មើលវត្តមានសិស្ស": bot.send_message(chat_id, "📊 **[ ពិនិត្យវត្តមាន ]**\nសូមវាយ៖ `/ld ឈ្មោះថ្នាក់`", parse_mode='Markdown')
        elif user_text == "✍️ ដាក់ពិន្ទុសិស្ស (Grade)": bot.send_message(chat_id, "✍️ **[ ដាក់ពិន្ទុកិច្ចការ ]**\nសូមវាយ៖ `/lh ឈ្មោះថ្នាក់`", parse_mode='Markdown')
        elif user_text == "➕ បង្កើតគណនីគ្រូ": add_teacher_wizard(message)
        elif user_text == "📋 មើលបញ្ជីគ្រូ":
            try:
                t_list = supabase.table("teachers").select("teacher_id, name").execute()
                if t_list.data:
                    msg = "📋 **[ បញ្ជីឈ្មោះលោកគ្រូ-អ្នកគ្រូ ]**\n-----------------------------------\n"
                    for t in t_list.data: msg += f"🆔 `{t['teacher_id']}` 👉 *{t['name']}*\n"
                    bot.send_message(chat_id, msg, parse_mode='Markdown')
                else:
                    bot.send_message(chat_id, "📭 មិនទាន់មានទិន្នន័យគ្រូឡើយ។")
            except Exception as e:
                bot.reply_to(message, f"❌ ទាញទិន្នន័យមិនបាន៖ {e}")
        elif user_text == "🔙 ចាកចេញ (Logout)":
            try:
                logout_id = message.from_user.id
                supabase.table("users").update({"status": "NEW", "role": "USER"}).eq("telegram_id", logout_id).execute()
                supabase.table("teachers").update({"telegram_id": None}).eq("telegram_id", logout_id).execute()
                bot.send_message(chat_id, "👋 **ចាកចេញជោគជ័យ!**", reply_markup=types.ReplyKeyboardRemove())
            except Exception as e:
                bot.reply_to(message, f"❌ Logout Error: {e}")

    # ========================================================
    # 📚 មុខងារ៖ គ្រូដាក់កិច្ចការផ្ទះ (/addhw)
    # ========================================================
    @bot.message_handler(commands=['addhw'])
    def add_homework_wizard_start(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "📚 **[ដាក់កិច្ចការផ្ទះ - ជំហាន ១/៤]**\nសូមបំពេញ **ឈ្មោះថ្នាក់** (ឧទាហរណ៍៖ GRADE12_A)៖")
        bot.register_next_step_handler(sent_msg, process_hw_class)

    def process_hw_class(message):
        chat_id = message.chat.id
        class_input = message.text.strip().upper()
        try:
            student_check = supabase.table("students").select("class_level").eq("class_level", class_input).limit(1).execute()
            if not student_check.data:
                bot.send_message(chat_id, f"⚠️ រកមិនឃើញថ្នាក់ `{class_input}` ទេ។ សូមចាប់ផ្ដើមឡើងវិញបាទBound")
                return
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")
            return
        sent_msg = bot.send_message(chat_id, f"🏫 ថ្នាក់៖ `{class_input}`\n\n👉 **[ជំហាន ២/៤]** សូមបំពេញ **ឈ្មោះមុខវិជ្ជា** ៖")
        bot.register_next_step_handler(sent_msg, process_hw_subject, class_input)

    def process_hw_subject(message, class_input):
        chat_id = message.chat.id
        subject_name = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🏫 ថ្នាក់៖ `{class_input}`\n📚 មុខវិជ្ជា៖ `*{subject_name}*`\n\n👉 **[ជំហាន ៣/៤]** សូមបំពេញ **ខ្លឹមសារកិច្ចការ** ៖")
        bot.register_next_step_handler(sent_msg, process_hw_desc, class_input, subject_name)

    def process_hw_desc(message, class_input, subject_name):
        chat_id = message.chat.id
        description = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🏫 ថ្នាក់៖ `{class_input}`\n📚 មុខវិជ្ជា៖ `*{subject_name}*`\n📝 ខ្លឹមសារ៖ `{description}`\n\n👉 **[ជំហាន ៤/៤]** សូមបំពេញ **Deadline** (លំនាំ៖ `2026-06-15 23:59`)៖")
        bot.register_next_step_handler(sent_msg, process_hw_final_save, class_input, subject_name, description)

    def process_hw_final_save(message, class_input, subject_name, description):
        chat_id = message.chat.id
        user_id = message.from_user.id
        deadline_string = message.text.strip()
        try:
            formatted_deadline = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").isoformat()
            t_check = supabase.table("teachers").select("teacher_id").eq("telegram_id", user_id).execute()
            t_id = t_check.data[0]['teacher_id'] if t_check.data else str(user_id)
            
            supabase.table("homework").insert({"class_level": class_input, "subject_name": subject_name, "description": description, "deadline_at": formatted_deadline, "teacher_id": t_id}).execute()
            bot.send_message(chat_id, "🎯 **បង្ហោះកិច្ចការផ្ទះជោគជ័យ!**")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")

    # ========================================================
    # 👤 មុខងារ៖ ថែមសិស្សថ្មី (/addstu)
    # ========================================================
    @bot.message_handler(commands=['addstu'])
    def add_student_wizard(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "👉 **[ថែមសិស្ស - ជំហាន ១/៤]** សូមបំពេញ **ID សិស្ស** (ឧទាហរណ៍៖ STU001)៖")
        bot.register_next_step_handler(sent_msg, process_stu_id)

    def process_stu_id(message):
        chat_id = message.chat.id
        stu_id = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🆔 ID សិស្ស៖ `{stu_id}`\n\n👉 **[ជំហាន ២/៤]** សូមបំពេញ **ឈ្មោះសិស្ស** ៖")
        bot.register_next_step_handler(sent_msg, process_stu_name, stu_id)

    def process_stu_name(message, stu_id):
        chat_id = message.chat.id
        stu_name = message.text.strip()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("ប្រុស (M)", "ស្រី (F)")
        sent_msg = bot.send_message(chat_id, f"🆔 ID សិស្ស៖ `{stu_id}`\n👤 ឈ្មោះ៖ `{stu_name}`\n\n👉 **[ជំហាន ៣/៤]** សូមជ្រើសរើស **ភេទ**៖", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, process_stu_gender, stu_id, stu_name)

    def process_stu_gender(message, stu_id, stu_name):
        chat_id = message.chat.id
        gender_raw = message.text.strip().upper()
        gender = "M" if "ប្រុស" in gender_raw or "M" in gender_raw else "F"
        sent_msg = bot.send_message(chat_id, f"🆔 ID សិស្ស៖ `{stu_id}`\n👤 ឈ្មោះ៖ `{stu_name}`\n🚻 ភេទ៖ `{gender}`\n\n👉 **[ជំហាន ៤/៤]** សូមបំពេញ **ឈ្មោះថ្នាក់** (ឧទាហរណ៍៖ GRADE12_A)៖", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent_msg, process_stu_final_save, stu_id, stu_name, gender)

    def process_stu_final_save(message, stu_id, stu_name, gender):
        chat_id = message.chat.id
        class_level = message.text.strip().upper()
        try:
            supabase.table("students").insert({"student_id": stu_id, "name": stu_name, "gender": gender, "class_level": class_level}).execute()
            bot.send_message(chat_id, f"🟢 **ថែមសិស្សជោគជ័យ!** ថ្នាក់ {class_level}")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")

    # ===================================================================================
    # ⚖️ មុខងារ៖ កត់ត្រាវិន័យសិស្ស (/adddiscipline)
    # ===================================================================================
    @bot.message_handler(commands=['adddiscipline'])
    def add_discipline_wizard(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "⚖️ **[កត់ត្រាវិន័យ - ជំហាន ១/៣]** សូមបំពេញ **ID សិស្ស** ៖")
        bot.register_next_step_handler(sent_msg, process_disc_id)

    def process_disc_id(message):
        chat_id = message.chat.id
        stu_id = message.text.strip().upper()
        sent_msg = bot.send_message(chat_id, "👉 **[ជំហាន ២/៣]** សូមរៀបរាប់ **បញ្ហាវិន័យ** ៖")
        bot.register_next_step_handler(sent_msg, process_disc_issue, stu_id)

    def process_disc_issue(message, stu_id):
        chat_id = message.chat.id
        incident_desc = message.text.strip()
        sent_msg = bot.send_message(chat_id, "👉 **[ជំហាន ៣/៣]** សូមបំពេញ **វិធានការកែប្រែ** ៖")
        bot.register_next_step_handler(sent_msg, process_disc_final, stu_id, incident_desc)

    def process_disc_final(message, stu_id, incident_desc):
        chat_id = message.chat.id
        corrective_act = message.text.strip()
        try:
            supabase.table("discipline_records").insert({"student_id": stu_id, "incident_description": incident_desc, "corrective_action": corrective_act}).execute()
            bot.send_message(chat_id, f"🟢 **កត់ត្រាវិន័យសិស្សជោគជ័យ!** ID: `{stu_id}`")
        except Exception as e: 
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")

    # ========================================================
    # 📅 មុខងារ៖ ថែមកាលវិភាគ (/addschedule)
    # ========================================================
    @bot.message_handler(commands=['addschedule'])
    def add_schedule_wizard(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "📅 **[ថែមកាលវិភាគ - ជំហាន ១/៦]** សូមបំពេញ **ឈ្មោះថ្នាក់** ៖")
        bot.register_next_step_handler(sent_msg, process_sch_class)

    def process_sch_class(message):
        chat_id = message.chat.id
        class_level = message.text.strip().upper()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៦]** សូមបំពេញ **ឈ្មោះមុខវិជ្ជា** ៖")
        bot.register_next_step_handler(sent_msg, process_sch_subject, class_level)

    def process_sch_subject(message, class_level):
        chat_id = message.chat.id
        subject = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៦]** សូមបំពេញ **ID គ្រូ** ៖")
        bot.register_next_step_handler(sent_msg, process_sch_teacher, class_level, subject)

    def process_sch_teacher(message, class_level, subject):
        chat_id = message.chat.id
        teacher_id = message.text.strip()
        if teacher_id.upper() == "NULL" or teacher_id == "": teacher_id = None
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៤/៦]** សូមជ្រើសរើស **ថ្ងៃសិក្សា** ៖", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, process_sch_day, class_level, subject, teacher_id)

    def process_sch_day(message, class_level, subject, teacher_id):
        chat_id = message.chat.id
        day = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៥/៦]** សូមបំពេញ **ម៉ោងដើម** ៖", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent_msg, process_sch_start, class_level, subject, teacher_id, day)

    def process_sch_start(message, class_level, subject, teacher_id, day):
        chat_id = message.chat.id
        start_time = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៦/៦]** សូមបំពេញ **ម៉ោងបញ្ចប់** ៖")
        bot.register_next_step_handler(sent_msg, process_sch_final, class_level, subject, teacher_id, day, start_time)

    def process_sch_final(message, class_level, subject, teacher_id, day, start_time):
        chat_id = message.chat.id
        end_time = message.text.strip()
        try:
            supabase.table("schedules").insert({"class_level": class_level, "subject_name": subject, "teacher_id": teacher_id, "study_day": day, "start_time": start_time, "end_time": end_time}).execute()
            bot.send_message(chat_id, f"🟢 **បន្ថែមព័ត៌មានកាលវិភាគជោគជ័យ!** ថ្នាក់ {class_level}")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")
    def broadcast_message(bot, chat_ids, message_text):
        def send_task():
            for chat_id in chat_ids:
                try:
                    bot.send_message(int(chat_id), message_text, parse_mode='Markdown')
                except Exception as e:
                    print(f"Error sending to {chat_id}: {e}")

    # ========================================================
    # ✍️ មុខងារ៖ ដាក់ពិន្ទុ & Feedback ឱ្យសិស្ស (/grade)
    # ========================================================
    @bot.message_handler(commands=['grade'])
    def grade_homework_wizard(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "✍️ **[ដាក់ពិន្ទុ - ជំហាន ១/៣]** សូមបំពេញ **ID Submission** របស់សិស្ស៖")
        bot.register_next_step_handler(sent_msg, process_grade_sub_id)

    def process_grade_sub_id(message):
        chat_id = message.chat.id
        sub_id = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៣]** សូមបំពេញ **ពិន្ទុ** ៖")
        bot.register_next_step_handler(sent_msg, process_grade_score, sub_id)

    def process_grade_score(message, sub_id):
        chat_id = message.chat.id
        score = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៣]** សូមបំពេញ **មតិយោបល់** ៖")
        bot.register_next_step_handler(sent_msg, process_grade_final, sub_id, score)

    def process_grade_final(message, sub_id, score):
        chat_id = message.chat.id
        feedback = message.text.strip()
        try:
            supabase.table("student_submissions").update({"score": score, "teacher_comment": feedback, "status": "GRADED"}).eq("id", int(sub_id)).execute()
            bot.send_message(chat_id, f"✅ **ដាក់ពិន្ទុជោគជ័យ!** កិច្ចការលេខ៖ `{sub_id}`")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")
    # ========================================================
    # 📢 មុខងារ៖ ថែមសេចក្ដីប្រកាស (/addnotice) - ប្រព័ន្ធបាញ់សារ (Broadcast)
    # ========================================================
    @bot.message_handler(commands=['addnotice'])
    def add_notice_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # 🔒 របាំងការពារ៖ ឆែកសិទ្ធិ Admin
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return
        except Exception as e:
            print(f"⚠️ Check admin error: {e}")
            return

        sent_msg = bot.send_message(
            chat_id, 
            "📢 **[ថែមសេចក្ដីប្រកាស - ជំហាន ១/៣]**\n\n👉 សូមបំពេញ **គោលដៅ (Target)** ដែលត្រូវបាញ់សារទៅកាន់៖\n"
            "• វាយពាក្យ `ALL` (ផ្ញើទៅកាន់គ្រូ អាណាព្យាបាល និងគ្រប់គ្រុបថ្នាក់)\n"
            "• វាយពាក្យ `TEACHER` (ផ្ញើទៅកាន់លោកគ្រូ-អ្នកគ្រូទាំងអស់)\n"
            "• វាយពាក្យ `STUDENT` (ផ្ញើទៅកាន់អាណាព្យាបាល/សិស្ស និងគ្រប់គ្រុបថ្នាក់)\n"
            "• ឬវាយឈ្មោះថ្នាក់ជាក់លាក់ (ឧទាហរណ៍៖ `GRADE12_A`):"
        )
        bot.register_next_step_handler(sent_msg, process_notice_target)

    def process_notice_target(message):
        chat_id = message.chat.id
        target = message.text.strip().upper()
        
        if not target:
            sent_msg = bot.send_message(chat_id, "⚠️ គោលដៅមិនអាចទទេបានទេ! សូមវាយបញ្ចូលម្ដងទៀត៖")
            bot.register_next_step_handler(sent_msg, process_notice_target)
            return
            
        sent_msg = bot.send_message(chat_id, f"🎯 គោលដៅបាញ់សារ៖ `{target}`\n\n👉 **[ជំហាន ២/៣]** សូមបំពេញ **ចំណងជើង (Title)** នៃសេចក្ដីប្រកាស៖")
        bot.register_next_step_handler(sent_msg, process_notice_title, target)

    def process_notice_title(message, target):
        chat_id = message.chat.id
        title = message.text.strip()
        
        if not title:
            sent_msg = bot.send_message(chat_id, "⚠️ ចំណងជើងមិនអាចទទេបានទេ! សូមវាយបញ្ចូលម្ដងទៀត៖")
            bot.register_next_step_handler(sent_msg, process_notice_title, target)
            return
            
        sent_msg = bot.send_message(chat_id, f"📌 ចំណងជើង៖ *{title}*\n\n👉 **[ជំហាន ៣/៣]** សូមបំពេញ **ខ្លឹមសារព័ត៌មានលម្អិត** ដែលត្រូវប្រកាស៖")
        bot.register_next_step_handler(sent_msg, process_notice_final_broadcast, target, title)

    def process_notice_final_broadcast(message, target, title):
        chat_id = message.chat.id
        user_id = message.from_user.id
        content = message.text.strip()
        
        if not content:
            sent_msg = bot.send_message(chat_id, "⚠️ ខ្លឹមសារមិនអាចទទេបានទេ! សូមវាយបញ្ចូលម្ដងទៀត៖")
            bot.register_next_step_handler(sent_msg, process_notice_final_broadcast, target, title)
            return
            
        loading_msg = bot.send_message(chat_id, "⏳ កំពុងរក្សាទុក និងរៀបចំប្រព័ន្ធបាញ់សាររួមសាលា...")
        
        try:
            # 🎯 ១. រក្សាទុកព័ត៌មានចូលទៅកាន់តារាង "school_notices" ក្នុង Supabase
            notice_res = supabase.table("school_notices").insert({
                "title": title, 
                "content": content, 
                "notice_type": target, 
                "created_by_telegram_id": int(user_id) 
            }).select().execute()

            notice_id = notice_res.data[0]['id'] if notice_res.data else None
            
            # ២. បង្កើតទម្រង់សារអត្ថបទសម្រាប់ Broadcast
            broadcast_msg = (
                f"📢 **[ សេចក្ដីជូនដំណឹងថ្មីពីសាលា DUC ]**\n"
                f"📌 **ចំណងជើង៖** *{title}*\n"
                f"----------------------------------------\n\n"
                f"📝 **ខ្លឹមសារព័ត៌មាន៖**\n{content}\n\n"
                f"----------------------------------------\n"
                f"✨ _សូមលោកគ្រូ-អ្នកគ្រូ និងសិស្សានុសិស្សមេត្តាជ្រាបជាព័ត៌មាន_"
            )

            # 🎛️ បង្កើតប៊ូតុង Inline ចុច "ទទួលដឹងឮ" អមជាមួយសារ
            markup_ack = types.InlineKeyboardMarkup()
            markup_ack.add(types.InlineKeyboardButton("✅ ខ្ញុំបានអាន និងទទួលដឹងឮ (Acknowledge)", callback_data=f"ack_{notice_id}"))

            # បង្កើត Set ទប់ស្កាត់ការផ្ញើសារស្ទួន (ទិន្នន័យមិនស្ទួន chat_id)
            teacher_chats = set()
            student_parent_chats = set()
            group_chats = set()

            # 🔍 កាត់សេចក្តីឆែកស្វែងរក ID ឆាតពីដាតាបេសតាមជម្រើស Target
            if target == "STUDENT" or target == "ALL":
                students_res = supabase.table("students").select("parent_telegram_id", "group_chat_id").execute()
                if students_res.data:
                    for s in students_res.data:
                        if s.get('parent_telegram_id'): 
                            student_parent_chats.add(str(s['parent_telegram_id']))
                        if s.get('group_chat_id') and str(s['group_chat_id']).strip() not in ["", "null", "None"]: 
                            group_chats.add(str(s['group_chat_id']).strip())
            
            if target == "TEACHER" or target == "ALL":
                teachers_res = supabase.table("teachers").select("telegram_id").execute()
                if teachers_res.data:
                    for t in teachers_res.data:
                        if t.get('telegram_id'): 
                            teacher_chats.add(str(t['telegram_id']))
                        
            if target not in ["ALL", "STUDENT", "TEACHER"]: # លក្ខខណ្ឌ៖ បាញ់ចូលចំថ្នាក់ជាក់លាក់
                students_res = supabase.table("students").select("parent_telegram_id", "group_chat_id").eq("class_level", target).execute()
                if students_res.data:
                    for s in students_res.data:
                        if s.get('parent_telegram_id'): 
                            student_parent_chats.add(str(s['parent_telegram_id']))
                        if s.get('group_chat_id') and str(s['group_chat_id']).strip() not in ["", "null", "None"]: 
                            group_chats.add(str(s['group_chat_id']).strip())

            # 📡 ៣. ចាប់ផ្ដើមយុទ្ធនាការបាញ់សារចេញ (Broadcast Execution)
            count_teacher = count_student_parent = count_group = 0
            
            # បាញ់ទៅលោកគ្រូ-អ្នកគ្រូ (ឆាតឯកជន)
            for t_id in teacher_chats:
                try:
                    bot.send_message(int(t_id), broadcast_msg, reply_markup=markup_ack, parse_mode='Markdown')
                    count_teacher += 1
                except Exception: pass
                
            # ផ្ញើទៅសិស្ស/អាណាព្យាបាល (ឆាតឯកជន)
            for sp_id in student_parent_chats:
                try:
                    bot.send_message(int(sp_id), broadcast_msg, reply_markup=markup_ack, parse_mode='Markdown')
                    count_student_parent += 1
                except Exception: pass
                
            # បាញ់ចូល Telegram Groups ថ្នាក់រៀនសាលា DUC
            for g_id in group_chats:
                try:
                    bot.send_message(int(g_id), broadcast_msg, parse_mode='Markdown')
                    count_group += 1
                except Exception: pass

            # លុបសាររង់ចាំ (Loading) ចេញ
            try: bot.delete_message(chat_id, loading_msg.message_id)
            except: pass

            # 🎉 ប្រកាសលទ្ធផលជោគជ័យជូន Admin
            final_report = (
                f"🟢 **[ រក្សាទុកដាតាបេស និងផ្សព្វផ្សាយរួមរួចរាល់! ]**\n"
                f"--------------------------------------------------\n"
                f"🎯 **គោលដៅផ្សាយ៖** `{target}`\n"
                f"📬 **ផ្ញើទៅឆាតគ្រូ៖** `{count_teacher}` នាក់\n"
                f"📲 **ផ្ញើទៅឆាតសិស្ស/អាណាព្យាបាល៖** `{count_student_parent}` នាក់\n"
                f"🏫 **បាញ់ចូល Groups ថ្នាក់រៀន៖** `{count_group}` គ្រុប\n"
                f"--------------------------------------------------\n"
                f"💡 _សារត្រូវបានបញ្ជូនទៅកាន់សមាជិកដែលបានផ្ទៀងផ្ទាត់_"
            )
            bot.send_message(chat_id, final_report, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ Broadcast process error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេសក្នុងការបាញ់សារ៖** `{e}`")
            # ========================================================
    # 🏖️ មុខងារ៖ ថែមថ្ងៃឈប់សម្រាកសាលា (/addholiday) - (លុបការឆែកសិទ្ធិចោល ១០០%)
    # ========================================================
    @bot.message_handler(commands=['addholiday'])
    def add_holiday_wizard(message):
        chat_id = message.chat.id
        
        # 🟢 បើកចំហរ៖ មិនបាច់ឆែកសិទ្ធិអ្វីទាំងអស់ រត់ទៅជំហានទី ១ ភ្លាមៗ
        sent_msg = bot.send_message(
            chat_id, 
            "🏖️ **[ថែមថ្ងៃឈប់សម្រាក - ជំហាន ១/៣]**\n\n👉 សូមបំពេញ **ឈ្មោះថ្ងៃឈប់សម្រាកជាភាសាខ្មែរ** ៖\n*(ឧទាហរណ៍៖ ពិធីបុណ្យអុំទូក)*"
        )
        bot.register_next_step_handler(sent_msg, process_hol_kh)

    def process_hol_kh(message):
        chat_id = message.chat.id
        name_kh = message.text.strip()
        
        if not name_kh:
            sent_msg = bot.send_message(chat_id, "⚠️ **ឈ្មោះបុណ្យមិនអាចទទេបានទេ!** សូមវាយបញ្ចូលម្ដងទៀត៖")
            bot.register_next_step_handler(sent_msg, process_hol_kh)
            return
            
        sent_msg = bot.send_message(
            chat_id, 
            f"🇰🇭 ឈ្មោះពិធីបុណ្យ៖ `{name_kh}`\n\n👉 **[ជំហាន ២/៣]** សូមបំពេញ **ឈ្មោះថ្ងៃឈប់សម្រាកជាភាសាអង់គ្លេស** ៖\n*(ឧទាហរណ៍៖ Water Festival)*"
        )
        bot.register_next_step_handler(sent_msg, process_hol_en, name_kh)

    def process_hol_en(message, name_kh):
        chat_id = message.chat.id
        name_en = message.text.strip()
        
        if not name_en:
            sent_msg = bot.send_message(chat_id, "⚠️ **ឈ្មោះភាសាអង់គ្លេសមិនអាចទទេបានទេ!** សូមវាយបញ្ចូលម្ដងទៀត៖")
            bot.register_next_step_handler(sent_msg, process_hol_en, name_kh)
            return
            
        sent_msg = bot.send_message(
            chat_id, 
            f"🇰🇭 ខ្មែរ៖ `{name_kh}`\n🇬🇧 អង់គ្លេស៖ `{name_en}`\n\n👉 **[ជំហាន ៣/៣]** សូមបំពេញ **កាលបរិច្ឆេទឈប់សម្រាក** ៖\n*(លំនាំ៖ ឆ្នាំ-ខែ-ថ្ងៃ ឧទាហរណ៍៖ 2026-11-24)*"
        )
        @bot.register_next_step_handler(sent_msg, process_hol_final, name_kh, name_en)
        def process_hol_final(message, name_kh, name_en):
        if not message.text: return
        chat_id = message.chat.id
        raw_date = message.text.strip()
        
        # បំប្លែងលេខខ្មែរទៅអង់គ្លេស
        khmer_digits = "០១២៣៤៥៦៧៨៩"
        english_digits = "0123456789"
        holiday_date = "".join([english_digits[khmer_digits.index(c)] if c in khmer_digits else c for c in raw_date])

        loading_msg = bot.send_message(chat_id, "⏳ កំពុងកត់ត្រា និងកំពុងបាញ់ដំណឹងទៅគ្រប់សមាជិក...")
        
        try:
            # ១. Insert ចូល Database
            supabase.table("holidays").insert({
                "event_name_km": name_kh, 
                "event_name_en": name_en, 
                "holiday_date": holiday_date, 
                "announcement_sent": 1
            }).execute()

            # ២. រៀបចំសារសម្រាប់បាញ់ចេញ
            announcement_msg = (
                f"🚨 **[ សេចក្ដីជូនដំណឹង៖ ថ្ងៃឈប់សម្រាកសាលា DUC ]**\n\n"
                f"🇰🇭 **{name_kh}**\n🇬🇧 **{name_en}**\n"
                f"📅 **កាលបរិច្ឆេទ៖** `{holiday_date}`\n\n"
                "✨ *សូមជូនពរឱ្យទទួលបានការសម្រាកលំហែកាយយ៉ាងសប្បាយរីករាយ!*"
            )

            # ៣. ទាញយក ID ទាំងអស់ដើម្បីបាញ់សារ
            target_ids = set()
            # ទាញយកគ្រូ
            t_res = supabase.table("teachers").select("telegram_id").execute()
            for t in t_res.data:
                if t.get('telegram_id'): target_ids.add(t['telegram_id'])
            
            # ទាញយកសិស្ស/អាណាព្យាបាល និង Group ID
            s_res = supabase.table("students").select("parent_telegram_id", "group_chat_id").execute()
            for s in s_res.data:
                if s.get('parent_telegram_id'): target_ids.add(s['parent_telegram_id'])
                if s.get('group_chat_id'): target_ids.add(s['group_chat_id'])

            # ៤. ហៅមុខងារ Broadcast ដែលប្រើ Threading (មិនធ្វើឱ្យ Bot គាំង)
            broadcast_message(bot, list(target_ids), announcement_msg)

            bot.send_message(chat_id, f"✅ រក្សាទុកជោគជ័យ និងបានបាញ់សារទៅកាន់ {len(target_ids)} គោលដៅ!")
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ {e}")
        finally:
            try: bot.delete_message(chat_id, loading_msg.message_id)
            except: pass
    # ===================================================================================
    # 👨‍🏫 មុខងារ៖ បង្កើតគណនីគ្រូថ្មី (/addteacher)
    # ===================================================================================
    @bot.message_handler(commands=['addteacher'])
    def add_teacher_wizard(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "➕ **[បង្កើតគណនីគ្រូ - ជំហាន ១/៣]** សូមបំពេញ **ID គ្រូ** (ឧទាហរណ៍៖ TCH001)៖")
        bot.register_next_step_handler(sent_msg, process_tch_id)

    def process_tch_id(message):
        chat_id = message.chat.id
        tch_id = message.text.strip().upper()
        sent_msg = bot.send_message(chat_id, f"🆔 ID គ្រូ៖ `{tch_id}`\n\n👉 **[ជំហាន ២/៣]** សូមបំពេញ **ឈ្មោះគ្រូ** ៖")
        bot.register_next_step_handler(sent_msg, process_tch_name, tch_id)

    def process_tch_name(message, tch_id):
        chat_id = message.chat.id
        tch_name = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🆔 ID គ្រូ៖ `{tch_id}`\n👤 ឈ្មោះ៖ `{tch_name}`\n\n👉 **[ជំហាន ៣/៣]** សូមកំណត់ **Password** ៖")
        bot.register_next_step_handler(sent_msg, process_tch_final, tch_id, tch_name)

    def process_tch_final(message, tch_id, tch_name):
        chat_id = message.chat.id
        pwd = message.text.strip()
        try:
            supabase.table("teachers").insert({"teacher_id": tch_id, "name": tch_name, "password": pwd}).execute()
            bot.send_message(chat_id, f"🟢 **បង្កើតគណនីគ្រូថ្មីជោគជ័យ!** ID: `{tch_id}`")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")

    # ========================================================
    # 🏢 មុខងារ៖ ថែមផ្នែកឱ្យគ្រូ (/adddept)
    # ========================================================
    @bot.message_handler(commands=['adddept'])
    def add_dept_wizard(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "🏢 **[ថែមផ្នែកឱ្យគ្រូ - ជំហាន ១/២]** សូមបំពេញ **ID គ្រូ** ៖")
        bot.register_next_step_handler(sent_msg, process_dept_teacher)

    def process_dept_teacher(message):
        chat_id = message.chat.id
        t_id = message.text.strip()
        try:
            teacher_check = supabase.table("teachers").select("name").eq("teacher_id", t_id).execute()
            if not teacher_check.data:
                bot.send_message(chat_id, f"❌ រកមិនឃើញគ្រូ ID `{t_id}` ទេ។")
                return
            t_name = teacher_check.data[0]['name']
            sent_msg = bot.send_message(chat_id, f"👤 គ្រូ៖ `{t_name}`\n\n👉 **[ជំហាន ២/២]** សូមបំពេញ **ឈ្មោះផ្នែក/ដេប៉ាតឺម៉ង់** ៖")
            bot.register_next_step_handler(sent_msg, process_dept_final, t_id, t_name)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

    def process_dept_final(message, t_id, t_name):
        chat_id = message.chat.id
        dept_name = message.text.strip()
        try:
            dept_res = supabase.table("departments").upsert({"department_name": dept_name}, on_conflict="department_name").execute()
            dept_id = dept_res.data[0]['id']
            supabase.table("teachers").update({"department_id": dept_id}).eq("teacher_id", t_id).execute()
            bot.send_message(chat_id, f"🟢 **រៀបចំផ្នែកគ្រូជោគជ័យ!** ផ្នែក៖ `{dept_name}`")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")

    # ========================================================
    # 🎓 មុខងារ៖ ថែមជំនាញឱ្យគ្រូ (/addmajor)
    # ========================================================
    @bot.message_handler(commands=['addmajor'])
    def add_major_wizard(message):
        chat_id = message.chat.id
        sent_msg = bot.send_message(chat_id, "🎓 **[ថែមជំនាញឱ្យគ្រូ - ជំហាន ១/៣]** សូមបំពេញ **ID គ្រូ** ៖")
        bot.register_next_step_handler(sent_msg, process_major_teacher)

    def process_major_teacher(message):
        chat_id = message.chat.id
        t_id = message.text.strip()
        try:
            teacher_check = supabase.table("teachers").select("name").eq("teacher_id", t_id).execute()
            if not teacher_check.data:
                bot.send_message(chat_id, f"❌ រកមិនឃើញគ្រូ ID `{t_id}` ទេ។")
                return
            t_name = teacher_check.data[0]['name']
            sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៣]** សូមបំពេញ **ឈ្មោះផ្នែក/ដេប៉ាតឺម៉ង់** ៖")
            bot.register_next_step_handler(sent_msg, process_major_dept, t_id, t_name)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

    def process_major_dept(message, t_id, t_name):
        chat_id = message.chat.id
        dept_name = message.text.strip()
        try:
            dept_res = supabase.table("departments").select("id").eq("department_name", dept_name).execute()
            if not dept_res.data:
                bot.send_message(chat_id, f"❌ រកមិនឃើញផ្នែកឈ្មោះ `{dept_name}` ទេ។")
                return
            dept_id = dept_res.data[0]['id']
            sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៣]** សូមបំពេញ **ឈ្មោះជំនាញថ្មី (Major)** ៖")
            bot.register_next_step_handler(sent_msg, process_major_final, t_id, t_name, dept_name, dept_id)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

    def process_major_final(message, t_id, t_name, dept_name, dept_id):
        chat_id = message.chat.id
        major_name = message.text.strip()
        try:
            major_res = supabase.table("majors").upsert({"department_id": dept_id, "major_name": major_name}, on_conflict="department_id, major_name").execute()
            major_id = major_res.data[0]['id']
            supabase.table("teachers").update({"major_id": major_id}).eq("teacher_id", t_id).execute()
            bot.send_message(chat_id, f"🟢 **ភ្ជាប់ជំនាញគ្រូរួចរាល់!** ជំនាញ៖ `{major_name}`")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុស៖ `{e}`")

    # ========================================================
    # 🔍 មុខងារ៖ មើលបញ្ជីសិស្សចុះឈ្មោះថ្មី (/checkreq)
    # ========================================================
    def check_requests_command(msg_obj):
        try:
            students_res = supabase.table("students").select("*").ilike("student_id", "PENDING%").execute()
            if not students_res.data:
                bot.send_message(msg_obj.chat.id, "✨ **លទ្ធផល៖** មិនមានសិស្សណាម្នាក់កំពុងរង់ចាំការអនុម័តទេ។")
                return
            response_msg = f"📋 **[ បញ្ជីសិស្សកំពុងរង់ចាំការអនុម័ត៖ {len(students_res.data)} នាក់ ]**\n-----------------------------------\n"
            for index, student in enumerate(students_res.data, start=1):
                parent_tg = student.get('parent_telegram_id', 'គ្មាន ID')
                response_msg += f"{index}. 👤 ឈ្មោះ៖ {student.get('name')} | 🏫 ថ្នាក់៖ {student.get('class_level')}\n👉 បញ្ជាអនុម័ត៖ `/approve {parent_tg}, DUC{index:03d}`\n\n"
            bot.send_message(msg_obj.chat.id, response_msg)
        except Exception as e:
            bot.send_message(msg_obj.chat.id, f"❌ Error: {e}")
            # ===================================================================================
# 🏫 គ្រុបអនុគមន៍ដំណើរការទាញបញ្ជីរាយនាម (ស្ថិតនៅកម្រិតក្រៅដាច់ស្រឡះ គ្មានដកឃ្លាដើមជួរទេ)
# ===================================================================================
def list_classes_command(msg_obj):
    try:
        students_res = _supabase.table("students").select("class_level").execute()
        distinct_classes = set(s['class_level'].strip().upper() for s in students_res.data if s.get('class_level')) if students_res.data else set()
        if not distinct_classes:
            _bot.send_message(msg_obj.chat.id, "ℹ️ មិនទាន់មានទិន្នន័យថ្នាក់រៀនសកម្មឡើយបាទ។")
            return
        msg = "🏫 [ បញ្ជីឈ្មោះថ្នាក់រៀនសកម្ម ]\n=========================\n"
        for i, c in enumerate(sorted(distinct_classes), 1): 
            msg += f"{i}. ថ្នាក់៖ {c}\n"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*[types.InlineKeyboardButton(f"📖 ថ្នាក់ {c}", callback_data=f"view_students:{c}") for c in sorted(distinct_classes)])
        _bot.send_message(msg_obj.chat.id, msg, reply_markup=markup)
    except Exception as e: 
        _bot.send_message(msg_obj.chat.id, f"❌ Error: {e}")

def list_depts_command(msg_obj):
    try:
        dept_res = _supabase.table("departments").select("id", "department_name").execute()
        if not dept_res.data:
            _bot.send_message(msg_obj.chat.id, "ℹ️ មិនទាន់មានទិន្នន័យផ្នែកឡើយបាទ។")
            return
        msg = "🏢 [ បញ្ជីឈ្មោះផ្នែក/ដេប៉ាតាម៉ង់ ]\n=========================\n"
        for i, d in enumerate(dept_res.data, 1): 
            msg += f"{i}. ផ្នែក៖ {d.get('department_name')}\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*[types.InlineKeyboardButton(f"🏢 {d.get('department_name')}", callback_data=f"view_dept:{d.get('id')}") for d in dept_res.data])
        _bot.send_message(msg_obj.chat.id, msg, reply_markup=markup)
    except Exception as e: 
        _bot.send_message(msg_obj.chat.id, f"❌ Error: {e}")

def list_teachers_command(msg_obj):
    try:
        teachers_res = _supabase.table("teachers").select("teacher_id", "name").execute()
        if not teachers_res.data:
            _bot.send_message(msg_obj.chat.id, "ℹ️ មិនទាន់មានទិន្នន័យគ្រូឡើយបាទ។")
            return
        msg = "👨‍🏫 [ បញ្ជីឈ្មោះលោកគ្រូ-អ្នកគ្រូ ]\n=========================\n"
        for i, t in enumerate(teachers_res.data, 1): 
            msg += f"{i}. {t.get('name')}\n"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*[types.InlineKeyboardButton(f"👨‍🏫 {t.get('name')}", callback_data=f"view_teacher:{t.get('teacher_id')}") for t in teachers_res.data])
        _bot.send_message(msg_obj.chat.id, msg, reply_markup=markup)
    except Exception as e: 
        _bot.send_message(msg_obj.chat.id, f"❌ Error: {e}")

def school_stats_command(msg_obj):
    try:
        s_res = _supabase.table("students").select("student_id", count="exact").execute()
        t_res = _supabase.table("teachers").select("teacher_id", count="exact").execute()
        msg = f"📊 **[ របាយការណ៍ស្ថិតិរួម ]**\n-----------------------\n👨‍🎓 សិស្សសរុប៖ `{s_res.count if s_res.count else 0}` នាក់\n👨‍🏫 គ្រូសរុប៖ `{t_res.count if t_res.count else 0}` នាក់"
        _bot.send_message(msg_obj.chat.id, msg, parse_mode='Markdown')
    except Exception as e: 
        _bot.send_message(msg_obj.chat.id, f"❌ Error: {e}")

def hw_analytics_command(msg_obj):
    _bot.send_message(msg_obj.chat.id, "📈 **កំពុងវិភាគទិន្នន័យ Homework និងគណនាភាគរយអត្រាប្រគល់កិច្ចការ...**")

# ====================================================================================================
# 📡 គ្រុបអនុគមន៍ចុចមើលលម្អិត (Callback System Sub-functions)
# ====================================================================================================
def callback_view_students(call):
    try:
        target_class = call.data.split(':', 1)[1]
        students_res = _supabase.table("students").select("student_id", "name", "gender").eq("class_level", target_class).execute()
        if not students_res.data:
            _bot.send_message(call.message.chat.id, f"ℹ️ មិនមានសិស្សក្នុងថ្នាក់ {target_class} ទេ។")
            return
        msg = f"👨‍🎓 [ បញ្ជីឈ្មោះសិស្ស៖ ថ្នាក់ {target_class} ]\n=========================\n"
        for i, stu in enumerate(students_res.data, 1):
            g_kh = "ប្រុស" if stu.get('gender', '').upper() == 'M' else "ស្រី" if stu.get('gender', '').upper() == 'F' else "ចម្រុះ"
            msg += f"{i}. ID: {stu.get('student_id')} | {stu.get('name')} ({g_kh})\n"
        _bot.send_message(call.message.chat.id, msg)
    except Exception as e: 
        _bot.send_message(call.message.chat.id, f"❌ Error: {e}")

def callback_view_dept(call):
    try:
        hw_res = _supabase.table("schedules").select("subject_name").execute()
        msg = "🏢 [ បញ្ជីឈ្មោះមុខវិជ្ជាសកម្ម ]\n=========================\n"
        if hw_res.data:
            distinct_subjects = set(hw.get('subject_name').strip() for hw in hw_res.data if hw.get('subject_name'))
            for i, sub in enumerate(sorted(distinct_subjects), 1): 
                msg += f" └ {i}. មុខវិជ្ជា៖ {sub}\n"
        else: 
            msg += " └ (មិនទាន់មានមុខវិជ្ជាសកម្ម)\n"
        _bot.send_message(call.message.chat.id, msg)
    except Exception as e: 
        _bot.send_message(call.message.chat.id, f"❌ Error: {e}")

def callback_view_teacher(call):
    try:
        target_teacher_id = call.data.split(':', 1)[1]
        teacher_info = _supabase.table("teachers").select("*").eq("teacher_id", target_teacher_id).execute()
        if not teacher_info.data: 
            return
        t_data = teacher_info.data[0]
        msg = f"📋 [ ប្រវត្តិគ្រូ ID: {target_teacher_id} ]\n=========================\n👤 ឈ្មោះ៖ {t_data.get('name')}\n🔑 លេខសម្ងាត់៖ {t_data.get('password')}"
        _bot.send_message(call.message.chat.id, msg)
    except Exception as e: 
        _bot.send_message(call.message.chat.id, f"❌ Error: {e}")
