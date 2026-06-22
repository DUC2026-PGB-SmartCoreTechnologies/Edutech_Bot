import telebot
from telebot import types
from datetime import datetime

# 💡 register_admin_teacher_handlers ទទួល bot និង supabase ពី main.py រួចជាស្រេច
def register_admin_teacher_handlers(bot, supabase):
    
    # ========================================================
    # 👑 មុខងារ៖ Admin វាយ /login (🔐 ប្រព័ន្ធចាក់សោរស្វ័យប្រវត្តិ បើមាន Admin រួចហើយ ហាមអ្នកផ្សេងលួចចូល)
    # ========================================================
    @bot.message_handler(commands=['login'])
    def admin_secret_login(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔍 ជំហានទី ១៖ រត់ទៅឆែកមើលក្នុងដាតាបេស Supabase ថាមាន Admin រួចហើយឬនៅ?
            admin_check = supabase.table("users").select("telegram_id").eq("role", "ADMIN").execute()
            
            # 🔒 លក្ខខណ្ឌការពារ៖ បើមាន Admin ក្នុងប្រព័ន្ធរួចហើយ និងមិនមែនជាលេខ ID របស់ Admin ចាស់
            if admin_check.data:
                existing_admin_id = admin_check.data[0].get('telegram_id')
                
                # បើអ្នកដែលកំពុងវាយនេះ មិនមែនជា Admin ចាស់ទេ គឺចាក់សោរបដិសេធភ្លាម!
                if str(user_id) != str(existing_admin_id):
                    bot.reply_to(message, "❌ **សុំទោស!** ប្រព័ន្ធគ្រប់គ្រងសាលា DUC មាន Admin មេរួចរាល់ហើយ。 លោកអ្នកមិនអាច Login ចូលបានឡើយ។")
                    print(f"⚠️ [SECURITY BLOCK] ID {user_id} ព្យាយាមលួច Login ត្រួតលើ Admin ចាស់ ID {existing_admin_id}!")
                    return
            
        except Exception as e:
            print(f"❌ Supabase Admin Lock Check Error: {e}")
            bot.reply_to(message, "❌ 有បញ្ហាបច្ចេកទេសក្នុងការឆែកមើលសិទ្ធិ។")
            return

        # 🔄 កាត់យកពាក្យសម្ងាត់ដែលវាយបន្ទាប់ពី /login
        text_input = message.text.strip()[6:].strip()
        ADMIN_MASTER_PASSWORD = "DUC_Admin@2026"
        
        if not text_input:
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ Admin!**\nសូមវាយ៖ `/login លេខសម្ងាត់មេ`", parse_mode='Markdown')
            return
            
        if text_input != ADMIN_MASTER_PASSWORD:
            bot.reply_to(message, "❌ **លេខសម្ងាត់ Admin មិនត្រឹមត្រូវទេ!** សូមព្យាយាមម្ដងទៀត។")
            return
            
        try:
            # 🔄 អាប់ដេត ឬរក្សាទុកសិទ្ធិ Admin ចូល Supabase ករណីឆ្លងផុតរបាំងការពារខាងលើ
            supabase.table("users").upsert({
                "telegram_id": user_id,
                "role": "ADMIN",
                "status": "APPROVED",
                "language": "km"
            }, on_conflict="telegram_id").execute()
            
            # 🎛️ បង្កើតផ្ទាំងប៊ូតុង Menu ពណ៌ប្រផេះធំៗ (លោតពីក្រោមអេក្រង់) សម្រាប់ Admin
            admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            admin_menu.add("➕ បង្កើតគណនីគ្រូ", "📋 មើលបញ្ជីគ្រូ","👁️ ផ្ទាំងសិស្ស (Student Panel)", "🔙 ចាកចេញ (Logout)")
            
            # 📢 ផ្ញើសារប្រកាសជោគជ័យ
            bot.send_message(chat_id, "🟢 **ផ្ទៀងផ្ទាត់សិទ្ធិ Admin មេជោគជ័យ!**", parse_mode='Markdown')
            
            # 💡 ហៅផ្ទាំងរូបភាព Panel Dashboard ពី helpers.py
            import helpers
            helpers.send_admin_panel(bot, chat_id)
            
            # 📤 បាញ់បញ្ចេញប៊ូតុង Menu ជូន Admin
            bot.send_message(
                chat_id, 
                "👑 **លោកអ្នកក៏អាចប្រើប្រាស់ ប៊ូតុង Menu ខាងក្រោម នេះបានផងដែរ៖**", 
                reply_markup=admin_menu,
                parse_mode='Markdown'
            )
            print(f"👑 [ADMIN LOGIN LIVE] Admin Telegram ID: {user_id} Verified and Saved.")
                
        except Exception as e:
            print(f"❌ Admin Login Error: {e}")
            bot.reply_to(message, f"❌ មិនអាចបើកផ្ទាំង Admin Panel បានទេ៖ `{e}`")


    # ========================================================
    # 🎛️ មុខងារ៖ ស្ទាក់ចាប់ការចុចប៊ូតុង Inline លើ Admin Dashboard (កែសម្រួលឱ្យហៅ Wizard)
    # ========================================================
    @bot.callback_query_handler(func=lambda call: call.data.startswith('adm_guide_'))
    def handle_admin_panel_inline_clicks(call):
        chat_id = call.message.chat.id
        action = call.data
        
        if action == "adm_guide_stats":
            school_stats_command(call.message)
        elif action == "adm_guide_analytics":
            hw_analytics_command(call.message)
        elif action == "adm_guide_addstu":
            add_student_wizard(call.message)
        elif action == "adm_guide_discipline":
            add_discipline_wizard(call.message)
        elif action == "adm_guide_grade":
            grade_homework_wizard(call.message)
        elif action == "adm_guide_notice":
            add_notice_wizard(call.message)
        elif action == "adm_guide_addteacher":
            add_teacher_wizard(call.message)
        elif action == "adm_guide_checkreq":
            check_requests_command(call.message)
        elif action == "adm_guide_approve":
            bot.send_message(chat_id, "🟢 **[ របៀបអនុម័ត / Approve សិស្ស ]**\nសូមវាយបញ្ជា៖ `/approve លេខTelegramID, លេខIDសិស្ស`", parse_mode='Markdown')
            
        bot.answer_callback_query(call.id)


    # ========================================================
    # 👩‍🏫 មុខងារ៖ គ្រូ Login ផ្ទៀងផ្ទាត់ជាមួយ ID & Password
    # ========================================================
    @bot.message_handler(commands=['tlogin'])
    def teacher_login_by_id_and_password(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text.strip()[7:].strip() # កាត់ពាក្យ /tlogin ចេញ
        
        if not text or len(text.split(',')) < 2:
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយលោកគ្រូ!**\nសូមវាយ៖ `/tlogin ID_គ្រូ,លេខសម្ងាត់`\n\n💡 *ឧទាហរណ៍៖* `/tlogin TCH001,Naron@2026`", parse_mode='Markdown')
            return
            
        try:
            parts = text.split(',')
            teacher_id_input = parts[0].strip()
            password_input = parts[1].strip()
            
            # 🎯 ឆែកមើលទាំង ID ក្នុងតារាង teachers
            t_res = supabase.table("teachers").select("*").eq("teacher_id", teacher_id_input).execute()
            
            if not t_res.data:
                bot.reply_to(message, f"❌ **រកមិនឃើញ ID `{teacher_id_input}` នេះក្នុងប្រព័ន្ធទេ!**")
                return
                
            teacher_data = t_res.data[0]
            db_password = teacher_data.get('password') 
            teacher_real_name = teacher_data['name']
            
            # 🔑 ផ្ទៀងផ្ទាត់លេខសម្ងាត់
            if password_input != db_password:
                bot.reply_to(message, "❌ **លេខសម្ងាត់គ្រូបង្រៀន មិនត្រឹមត្រូវទេ!**")
                return
                
            # 🔄 ភ្ជាប់ ID Telegram របស់គ្រូ ចូលទៅក្នុងតារាង teachers ត្រង់ជួរ telegram_id
            supabase.table("teachers").update({
                "telegram_id": user_id 
            }).eq("teacher_id", teacher_id_input).execute()
            
            # 🔄 អាប់ដេតតួនាទីក្នុងតារាង users ទៅជា TEACHER
            supabase.table("users").upsert({
                "telegram_id": user_id, 
                "status": "APPROVED", 
                "role": "TEACHER", 
                "language": "km"
            }, on_conflict="telegram_id").execute()
            
            # 🎛️ បង្កើតផ្ទាំង Menu គ្រាប់ចុចពណ៌ប្រផេះធំៗជូនលោកគ្រូ
            teacher_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            teacher_menu.add("📚 ដាក់កិច្ចការផ្ទះ (Add HW)", "📊 មើលវត្តមានសិស្ស", "✍️ ដាក់ពិន្ទុសិស្ស (Grade)", "🔙 ចាកចេញ (Logout)")
            
            welcome_msg = (
                f"👩‍🏫 **[ ស្វាគមន៍ {teacher_real_name} ចូលកាន់ប្រព័ន្ធ DUC ]**\n"
                "--------------------------------------------------\n"
                f"🆔 **ID គ្រូបង្រៀន៖** `{teacher_id_input}`\n"
                "🔐 **ស្ថានភាព៖** ផ្ទៀងផ្ទាត់អត្តសញ្ញាណជោគជ័យ!\n"
                "--------------------------------------------------\n"
                "🤖 លោកគ្រូអាចប្រើប្រាស់ **ប៊ូតុង Menu ខាងក្រោម** ដើម្បីគ្រប់គ្រងការងារសាលាបានហើយបាទ"
            )
            bot.send_message(chat_id, welcome_msg, parse_mode='Markdown', reply_markup=teacher_menu)
            print(f"✅ [TEACHER LOGIN SUCCESS] លោកគ្រូ {teacher_real_name} ចូលប្រព័ន្ធជោគជ័យ!")
            
        except Exception as e:
            print(f"❌ Teacher Login Error: {e}")
            bot.reply_to(message, f"❌ ប្រព័ន្ធជួបបញ្ហាបច្ចេកទេស៖ `{e}`")


    # ========================================================
    # 🎛️ មុខងារ៖ ស្ទាក់ចាប់រាល់ពេលគ្រូ ឬ Admin ចុចប៊ូតុង Menu ធំៗ
    # ========================================================
    @bot.message_handler(func=lambda message: message.text in [
        "📚 ដាក់កិច្ចការផ្ទះ (Add HW)", 
        "📊 មើលវត្តមានសិស្ស", 
        "✍️ ដាក់ពិន្ទុសិស្ស (Grade)", 
        "🔙 ចាកចេញ (Logout)",
        "➕ បង្កើតគណនីគ្រូ",
        "📋 មើលបញ្ជីគ្រូ"
    ])
    def handle_teacher_and_admin_menu_clicks(message):
        chat_id = message.chat.id
        user_text = message.text
        
        if user_text == "📚 ដាក់កិច្ចការផ្ទះ (Add HW)":
            add_homework_wizard_start(message)
            
        elif user_text == "📊 មើលវត្តមានសិស្ស":
            bot.send_message(chat_id, "📊 **[ ពិនិត្យវត្តមាន ]**\nសូមវាយ៖ `/ld ឈ្មោះថ្នាក់` (ឧទាហរណ៍៖ `/ld GRADE12_A`)", parse_mode='Markdown')
            
        elif user_text == "✍️ ដាក់ពិន្ទុសិស្ស (Grade)":
            bot.send_message(chat_id, "✍️ **[ ដាក់ពិន្ទុកិច្ចការ ]**\nសូមវាយ៖ `/lh ឈ្មោះថ្នាក់` ដើម្បីមើលកិច្ចការដែលសិស្សផ្ញើមក (ឧទាហរណ៍៖ `/lh GRADE12_A`)", parse_mode='Markdown')

        elif user_text == "➕ បង្កើតគណនីគ្រូ":
            add_teacher_wizard(message)

        elif user_text == "📋 មើលបញ្ជីគ្រូ":
            try:
                t_list = supabase.table("teachers").select("teacher_id, name").execute()
                if t_list.data:
                    msg = "📋 **[ បញ្ជីឈ្មោះលោកគ្រូ-អ្នកគ្រូ ]**\n--------------------------------------------------\n"
                    for t in t_list.data:
                        msg += f"🆔 `{t['teacher_id']}` 👉 *{t['name']}*\n"
                    bot.send_message(chat_id, msg, parse_mode='Markdown')
                else:
                    bot.send_message(chat_id, "📭 មិនទាន់មានទិន្នន័យគ្រូបង្រៀននៅក្នុងប្រព័ន្ធឡើយ។")
            except Exception as e:
                bot.reply_to(message, f"❌ មិនអាចទាញបញ្ជីគ្រូបានទេ៖ {e}")

        elif user_text == "🔙 ចាកចេញ (Logout)":
            try:
                user_id = message.from_user.id
                supabase.table("users").update({"status": "NEW", "role": "USER"}).eq("telegram_id", user_id).execute()
                supabase.table("teachers").update({"telegram_id": None}).eq("telegram_id", user_id).execute()
                remove_markup = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(chat_id, "👋 **ចាកចេញពីគណនីជោគជ័យ!** សូមវាយ `/start` ដើម្បីចូលគណនីផ្សេងទៀតបាទ។", reply_markup=remove_markup)
            except Exception as e:
                bot.reply_to(message, f"❌ Logout ជួបបញ្ហា៖ `{e}`")


    # ========================================================
    # 📚 មុខងារ៖ គ្រូដាក់កិច្ចការផ្ទះ (/addhw) - ទម្រង់ Wizard Steps
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
            # 🔍 ប្រព័ន្ធស្កែនឆែករកឈ្មោះថ្នាក់ពីតារាងសិស្ស (CHECK FIRST តាមកូដចាស់បង)
            student_check = supabase.table("students").select("class_level").eq("class_level", class_input).limit(1).execute()
            
            if not student_check.data:
                all_stud = supabase.table("students").select("class_level").execute()
                class_list_str = "មិនទាន់មានថ្នាក់ចុះឈ្មោះ"
                if all_stud.data:
                    unique_classes = list(set([row.get('class_level') for row in all_stud.data if row.get('class_level')]))
                    class_list_str = ", ".join([f"`{c}`" for c in unique_classes])
                
                bot.send_message(chat_id, f"⚠️ **សូមលោកគ្រូជួយ Check Class ឡើងវិញ៖**\nរកមិនឃើញសិស្សក្នុងថ្នាក់ `{class_input}` នេះក្នុងតារាងសិស្សទេបាទ!\n📋 **ឈ្មោះថ្នាក់ដែលមានសិស្សពិតប្រាកដគឺ៖** {class_list_str}\n\n👉 សូមចុចប៊ូតុង Menu ដើម្បីចាប់ផ្ដើមឡើងវិញបាទ។")
                return
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេសឆែកថ្នាក់៖ {e}")
            return

        sent_msg = bot.send_message(chat_id, f"🏫 ថ្នាក់៖ `{class_input}`\n\n👉 **[ជំហាន ២/៤]** សូមបំពេញ **ឈ្មោះមុខវិជ្ជា** (ឧទាហរណ៍៖ ភាសាខ្មែរ)៖")
        bot.register_next_step_handler(sent_msg, process_hw_subject, class_input)

    def process_hw_subject(message, class_input):
        chat_id = message.chat.id
        subject_name = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🏫 ថ្នាក់៖ `{class_input}`\n📚 មុខវិជ្ជា៖ `*{subject_name}*`\n\n👉 **[ជំហាន ៣/៤]** សូមបំពេញ **ខ្លឹមសារ/ការពិពណ៌នាកិច្ចការផ្ទះ**៖")
        bot.register_next_step_handler(sent_msg, process_hw_desc, class_input, subject_name)

    def process_hw_desc(message, class_input, subject_name):
        chat_id = message.chat.id
        description = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🏫 ថ្នាក់៖ `{class_input}`\n📚 មុខវិជ្ជា៖ `*{subject_name}*`\n📝 ខ្លឹមសារ៖ `{description}`\n\n👉 **[ជំហាន ៤/៤]** សូមបំពេញ **កាលបរិច្ឆេទឈប់ទទួល (Deadline)**\n(លំនាំ៖ `ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី` ឧទាហរណ៍៖ `2026-06-15 23:59`)៖")
        bot.register_next_step_handler(sent_msg, process_hw_final_save, class_input, subject_name, description)

    def process_hw_final_save(message, class_input, subject_name, description):
        chat_id = message.chat.id
        user_id = message.from_user.id
        deadline_string = message.text.strip()
        
        try:
            formatted_deadline = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").isoformat()
        except ValueError:
            bot.send_message(chat_id, "⚠️ **ទម្រង់ថ្ងៃខែខុសហើយ!** លំនាំ៖ `ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី` (ឧទាហរណ៍៖ `2026-06-15 17:00`)។ សូមចាប់ផ្ដើមឡើងវិញ។")
            return
            
        try:
            t_check = supabase.table("teachers").select("teacher_id").eq("telegram_id", user_id).execute()
            t_id = t_check.data[0]['teacher_id'] if t_check.data else str(user_id)
            
            supabase.table("homework").insert({
                "class_level": class_input,
                "subject_name": subject_name,
                "description": description,
                "deadline_at": formatted_deadline, 
                "teacher_id": t_id,
                "attachment_file": None,   
                "attachment_type": None
            }).execute()
            
            display_date = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").strftime("%d-%b-%Y ម៉ោង %I:%M %p")
            success_msg = (
                "🎯 **[ បង្ហោះកិច្ចការផ្ទះជោគជ័យ! ]**\n"
                "--------------------------------------------------\n"
                f"🏫 **សម្រាប់ថ្នាក់៖** `{class_input}`\n"
                f"📚 **មុខវិជ្ជា៖** *{subject_name}*\n"
                f"📝 **ខ្លឹមសារ៖** _{description}_\n"
                f"⏳ **Deadline៖** `📅 {display_date}`\n"
                "--------------------------------------------------\n"
                "🟢 *ប្រព័ន្ធបានឆែកឃើញមានសិស្សក្នុងថ្នាក់នេះរួចរាល់ហើយ លោកគ្រូ!*"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"❌ មិនអាចរក្សាទុកកិច្ចការផ្ទះបានទេ៖ `{e}`")


    # ========================================================
    # 👤 មុខងារ៖ ថែមសិស្សថ្មី (/addstu) - ទម្រង់ Wizard Steps
    # ========================================================
    @bot.message_handler(commands=['addstu'])
    def add_student_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិឡើយ។")
            return

        sent_msg = bot.send_message(chat_id, "👉 **[ថែមសិស្ស - ជំហាន ១/៤]** សូមបំពេញ **លេខសម្គាល់ ID សិស្ស** (ឧទាហរណ៍៖ STU001)៖")
        bot.register_next_step_handler(sent_msg, process_stu_id)

    def process_stu_id(message):
        chat_id = message.chat.id
        stu_id = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🆔 ID សិស្ស៖ `{stu_id}`\n\n👉 **[ជំហាន ២/៤]** សូមបំពេញ **ឈ្មោះសិស្ស** (ឧទាហរណ៍៖ សុខ ជា)៖")
        bot.register_next_step_handler(sent_msg, process_stu_name, stu_id)

    def process_stu_name(message, stu_id):
        chat_id = message.chat.id
        stu_name = message.text.strip()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("ประុស (M)", "ស្រី (F)")
        sent_msg = bot.send_message(chat_id, f"🆔 ID សិស្ស៖ `{stu_id}`\n👤 ឈ្មោះ៖ `{stu_name}`\n\n👉 **[ជំហាន ៣/៤]** សូមជ្រើសរើស **ភេទសិស្ស**៖", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, process_stu_gender, stu_id, stu_name)

    def process_stu_gender(message, stu_id, stu_name):
        chat_id = message.chat.id
        gender_raw = message.text.strip().upper()
        gender = "M" if "ប្រុស" in gender_raw or "M" in gender_raw else "F"
        sent_msg = bot.send_message(chat_id, f"🆔 ID សិស្ស៖ `{stu_id}`\n👤 ឈ្មោះ៖ `{stu_name}`\n🚻 ភេទ៖ `{gender}`\n\n👉 **[ជំហាន ៤/៤]** សូមបំពេញ **ឈ្មោះថ្នាក់រៀន** (ឧទាហរណ៍៖ GRADE12_A)៖", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent_msg, process_stu_final_save, stu_id, stu_name, gender)

    def process_stu_final_save(message, stu_id, stu_name, gender):
        chat_id = message.chat.id
        class_level = message.text.strip().upper()
        try:
            res = supabase.table("students").insert({"student_id": stu_id, "name": stu_name, "gender": gender, "class_level": class_level}).execute()
            if res.data:
                bot.send_message(chat_id, f"🟢 **ថែមសិស្សជោគជ័យ!**\n🆔 ID: {stu_id}\n👤 ឈ្មោះ: {stu_name}\n🚻 ភេទ: {gender}\n🏫 ថ្នាក់: {class_level}")
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេស៖ `{e}`")


   # ===================================================================================
    # ⚖️ មុខងារ៖ កត់ត្រាវិន័យសិស្ស (/adddiscipline) - ទម្រង់ Wizard Steps (Sync Columns DB ១០០%)
    # ===================================================================================
    @bot.message_handler(commands=['adddiscipline'])
    def add_discipline_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិឡើយ។")
            return

        sent_msg = bot.send_message(chat_id, "⚖️ **[កត់ត្រាវិន័យ - ជំហាន ១/៣]** សូមបំពេញ **លេខសម្គាល់ ID សិស្ស** (ឧទាហរណ៍៖ STU001)៖")
        bot.register_next_step_handler(sent_msg, process_disc_id)

    def process_disc_id(message):
        chat_id = message.chat.id
        stu_id = message.text.strip().upper()
        sent_msg = bot.send_message(chat_id, "👉 **[ជំហាន ២/៣]** សូមរៀបរាប់ **បញ្ហាវិន័យ/កំហុសដែលកើតឡើង** ៖")
        bot.register_next_step_handler(sent_msg, process_disc_issue, stu_id)

    def process_disc_issue(message, stu_id):
        chat_id = message.chat.id
        incident_desc = message.text.strip()
        sent_msg = bot.send_message(chat_id, "👉 **[ជំហាន ៣/៣]** សូមបំពេញ **វិធានការកែប្រែ/វិន័យ** ៖")
        bot.register_next_step_handler(sent_msg, process_disc_final, stu_id, incident_desc)

    def process_disc_final(message, stu_id, incident_desc):
        chat_id = message.chat.id
        corrective_act = message.text.strip()
        try:
            # 🟢 💡 កែតម្រូវចំៗ៖ ប្រើ 'incident_description' និង 'corrective_action' ឱ្យត្រូវតាម Supabase របស់បងបេះបិទ
            res = supabase.table("discipline_records").insert({
                "student_id": stu_id, 
                "incident_description": incident_desc, 
                "corrective_action": corrective_act
            }).execute()
            
            if res.data: 
                bot.send_message(chat_id, f"🟢 **កត់ត្រាវិន័យសិស្សចូលដាតាបេសជោគជ័យ!**\n--------------------------------------------------\n🆔 **ID សិស្ស៖** `{stu_id}`\n📝 **កំហុស/បញ្ហា៖** _{incident_desc}_\n⚖️ **វិធានការកែប្រែ៖** *{corrective_act}*")
            else:
                bot.send_message(chat_id, "❌ បរាជ័យ៖ ដាតាបេសបដិសេធការរក្សាទុកទិន្នន័យ។")
        except Exception as e: 
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេសដាតាបេស៖** `{e}`")


    # ========================================================
    # 📅 មុខងារ៖ ថែមតារាងកាលវិភាគ (/addschedule) - ទម្រង់ Wizard Steps
    # ========================================================
    @bot.message_handler(commands=['addschedule'])
    def add_schedule_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
            return

        sent_msg = bot.send_message(chat_id, "📅 **[ថែមកាលវិភាគ - ជំហាន ១/៦]** សូមបំពេញ **ឈ្មោះថ្នាក់** (ឧទាហរណ៍៖ GRADE12_A)៖")
        bot.register_next_step_handler(sent_msg, process_sch_class)

    def process_sch_class(message):
        chat_id = message.chat.id
        class_level = message.text.strip().upper()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៦]** សូមបំពេញ **ឈ្មោះមុខវិជ្ជា** (ឧទាហរណ៍៖ គណិតវិទ្យា)៖")
        bot.register_next_step_handler(sent_msg, process_sch_subject, class_level)

    def process_sch_subject(message, class_level):
        chat_id = message.chat.id
        subject = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៦]** សូមបំពេញ **ID គ្រូបង្រៀន** (បើគ្មានវាយពាក្យ NULL)៖")
        bot.register_next_step_handler(sent_msg, process_sch_teacher, class_level, subject)

    def process_sch_teacher(message, class_level, subject):
        chat_id = message.chat.id
        teacher_id = message.text.strip()
        if teacher_id.upper() == "NULL" or teacher_id == "":
            teacher_id = None
            
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៤/៦]** សូមជ្រើសរើស **ថ្ងៃសិក្សា (Day)**៖", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, process_sch_day, class_level, subject, teacher_id)

    def process_sch_day(message, class_level, subject, teacher_id):
        chat_id = message.chat.id
        day = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៥/៦]** សូមបំពេញ **ម៉ោងដើម** (ឧទាហរណ៍៖ 08:00)៖", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent_msg, process_sch_start, class_level, subject, teacher_id, day)

    def process_sch_start(message, class_level, subject, teacher_id, day):
        chat_id = message.chat.id
        start_time = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៦/៦]** សូមបំពេញ **ម៉ោងបញ្ចប់** (ឧទាហរណ៍៖ 09:30)៖")
        bot.register_next_step_handler(sent_msg, process_sch_final, class_level, subject, teacher_id, day, start_time)

    def process_sch_final(message, class_level, subject, teacher_id, day, start_time):
        chat_id = message.chat.id
        end_time = message.text.strip()
        try:
            res = supabase.table("schedules").insert({
                "class_level": class_level, "subject_name": subject, "teacher_id": teacher_id,
                "study_day": day, "start_time": start_time, "end_time": end_time
            }).execute()
            if res.data:
                bot.send_message(chat_id, f"🟢 **បន្ថែមព័ត៌មានកាលវិភាគជោគជ័យ!**\n🏫 ថ្នាក់៖ {class_level}\n📖 មុខវិជ្ជា៖ {subject}\n📅 ថ្ងៃ៖ {day} ({start_time} - {end_time})")
        except Exception as e:
            if "unique_class_schedule" in str(e):
                bot.send_message(chat_id, "❌ **មិនអាចបន្ថែមបានទេ!** ដោយសារថ្នាក់នេះមានកាលវិភាគរៀនចំម៉ោង និងថ្ងៃនេះរួចរាល់ហើយបាទ។")
            else:
                bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`")


    # ========================================================
    # ✍️ មុខងារ៖ ដាក់ពិន្ទុ & Feedback ឱ្យសិស្ស (/grade) - ទម្រង់ Wizard Steps
    # ========================================================
    @bot.message_handler(commands=['grade'])
    def grade_homework_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិឡើយ។")
            return

        sent_msg = bot.send_message(chat_id, "✍️ **[ដាក់ពិន្ទុ - ជំហាន ១/៣]** សូមបំពេញ **ID Submission** របស់សិស្ស៖")
        bot.register_next_step_handler(sent_msg, process_grade_sub_id)

    def process_grade_sub_id(message):
        chat_id = message.chat.id
        sub_id = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៣]** សូមបំពេញ **ពិន្ទុ (Score)** ៖")
        bot.register_next_step_handler(sent_msg, process_grade_score, sub_id)

    def process_grade_score(message, sub_id):
        chat_id = message.chat.id
        score = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៣]** សូមបំពេញ **មតិយោបល់ (Feedback)** ៖")
        bot.register_next_step_handler(sent_msg, process_grade_final, sub_id, score)

    def process_grade_final(message, sub_id, score):
        chat_id = message.chat.id
        feedback = message.text.strip()
        try:
            res = supabase.table("student_submissions").update({
                "score": score, "teacher_comment": feedback, "status": "GRADED"
            }).eq("id", int(sub_id)).execute()
            if res.data:
                bot.send_message(chat_id, f"✅ **ដាក់ពិន្ទុជោគជ័យ!**\n📂 កិច្ចការលេខ៖ `{sub_id}`\n💯 ពិន្ទុ៖ *{score}* 🌟\n💬 មតិគ្រូ៖ `{feedback}`")
        except Exception as e:
            bot.send_message(chat_id, f"❌ មិនអាចរក្សាទុកការដាក់ពិន្ទុបានទេ៖ `{e}`")


    # ========================================================
    # 📢 មុខងារ៖ ថែមសេចក្ដីប្រកាស (/addnotice) - ទម្រង់ Wizard + ប្រព័ន្ធបាញ់សាររួមសាលាអមប៊ូតុង
    # ========================================================
    @bot.message_handler(commands=['addnotice'])
    def add_notice_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!**")
            return

        sent_msg = bot.send_message(chat_id, "📢 **[ថែមសេចក្ដីប្រកាស - ជំហាន ១/៣]** សូមបំពេញ **គោលដៅ (Target)** \n(ជ្រើសរើស៖ ALL, STUDENT, TEACHER ឬឈ្មោះថ្នាក់ជាក់លាក់ ដូចជា 5_SPD)៖")
        bot.register_next_step_handler(sent_msg, process_notice_target)

    def process_notice_target(message):
        chat_id = message.chat.id
        target = message.text.strip().upper()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៣]** សូមបំពេញ **ចំណងជើង (Title)** នៃសេចក្ដីប្រកាស៖")
        bot.register_next_step_handler(sent_msg, process_notice_title, target)

    def process_notice_title(message, target):
        chat_id = message.chat.id
        title = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៣]** សូមបំពេញ **ខ្លឹមសារព័ត៌មានលម្អិត** ៖")
        bot.register_next_step_handler(sent_msg, process_notice_final_broadcast, target, title)

    def process_notice_final_broadcast(message, target, title):
        chat_id = message.chat.id
        user_id = message.from_user.id
        content = message.text.strip()
        
        try:
            # 🎯 រក្សាទុកចូលតារាង school_notices តាមទម្រង់ចាស់របស់បង
            notice_res = supabase.table("school_notices").insert({
                "title": title, "content": content, "notice_type": target, "created_by_telegram_id": int(user_id) 
            }).select().execute()

            notice_id = notice_res.data[0]['id'] if notice_res.data else None
            broadcast_msg = f"📢 **[ សេចក្ដីជូនដំណឹងថ្មីពីសាលា ]**\n📌 **ចំណងជើង៖** {title}\n----------------------------------------\n\n📝 **ខ្លឹមសារ៖** {content}"

            # 🎛️ បង្កើតប៊ូតុង Inline Keyboard សម្រាប់ឱ្យចុច "ទទួលដឹងឮ"
            markup_ack = types.InlineKeyboardMarkup()
            markup_ack.add(types.InlineKeyboardButton("✅ ខ្ញុំបានអាន និងទទួលដឹងឮ (Acknowledge)", callback_data=f"ack_{notice_id}"))

            teacher_chats, student_parent_chats, group_chats = set(), set(), set()

            if target == "STUDENT" or target == "ALL":
                students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id").execute()
                if students_res.data:
                    for s in students_res.data:
                        if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
                        if s.get('group_chat_id') and str(s['group_chat_id']).strip() not in ["", "null"]: group_chats.add(str(s['group_chat_id']).strip())
            
            if target == "TEACHER" or target == "ALL":
                teachers_res = supabase.table("teachers").select("telegram_id").execute()
                if teachers_res.data:
                    for t in teachers_res.data:
                        if t.get('telegram_id'): teacher_chats.add(str(t['telegram_id']))
                        
            if target not in ["ALL", "STUDENT", "TEACHER"]: # បាញ់ចំថ្នាក់ជាក់លាក់
                students_res = supabase.table("students").select("parent_telegram_id", "group_chat_id").eq("class_level", target).execute()
                if students_res.data:
                    for s in students_res.data:
                        if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
                        if s.get('group_chat_id') and str(s['group_chat_id']).strip() not in ["", "null"]: group_chats.add(str(s['group_chat_id']).strip())

            count_teacher = count_student_parent = count_group = 0
            for t_id in teacher_chats:
                try:
                    bot.send_message(int(t_id), broadcast_msg, reply_markup=markup_ack, parse_mode='Markdown')
                    count_teacher += 1
                except Exception: pass
            for sp_id in student_parent_chats:
                try:
                    bot.send_message(int(sp_id), broadcast_msg, reply_markup=markup_ack, parse_mode='Markdown')
                    count_student_parent += 1
                except Exception: pass
            for g_id in group_chats:
                try:
                    bot.send_message(int(g_id), broadcast_msg, parse_mode='Markdown')
                    count_group += 1
                except Exception: pass

            bot.send_message(chat_id, f"🟢 **រក្សាទុកដាតាបេស និងផ្សព្វផ្សាយជោគជ័យ!**\n🎯 គោលដៅ៖ `{target}`\n👨‍🏫 ផ្ញើទៅគ្រូ៖ `{count_teacher}` នាក់\n📲 ផ្ញើទៅសិស្ស៖ `{count_student_parent}` នាក់\n🏫 ចូល Group ថ្នាក់៖ `{count_group}` គ្រុប")
        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`")


    # ========================================================
    # 🏖️ មុខងារ៖ ថែមថ្ងៃឈប់សម្រាកសាលា (/addholiday) - ទម្រង់ Wizard Steps + Broadcast
    # ========================================================
    @bot.message_handler(commands=['addholiday'])
    def add_holiday_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
            return

        sent_msg = bot.send_message(chat_id, "🏖️ **[ថែមថ្ងៃឈប់សម្រាក - ជំហាន ១/៣]** សូមបំពេញ **ឈ្មោះបុណ្យជាភាសាខ្មែរ** ៖")
        bot.register_next_step_handler(sent_msg, process_hol_kh)

    def process_hol_kh(message):
        chat_id = message.chat.id
        name_kh = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៣]** សូមបំពេញ **ឈ្មោះបុណ្យជាភាសាអង់គ្លេស** ៖")
        bot.register_next_step_handler(sent_msg, process_hol_en, name_kh)

    def process_hol_en(message, name_kh):
        chat_id = message.chat.id
        name_en = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៣]** សូមបំពេញ **ឆ្នាំ-ខែ-ថ្ងៃ ឈប់សម្រាក** (ឧទាហរណ៍៖ 2026-11-24)៖")
        bot.register_next_step_handler(sent_msg, process_hol_final, name_kh, name_en)

    def process_hol_final(message, name_kh, name_en):
        chat_id = message.chat.id
        holiday_date = message.text.strip()
        
        try:
            supabase.table("holidays").insert({
                "event_name_km": name_kh, "event_name_en": name_en, "holiday_date": holiday_date, "announcement_sent": 1 
            }).execute()
            
            announcement_msg = (
                "🚨 **[ សេចក្ដីជូនដំណឹង៖ ថ្ងៃឈប់សម្រាកសាលា ]**\n\n"
                "សូមជម្រាបជូនលោកគ្រូ អ្នកគ្រូ សិស្សានុសិស្ស និងអាណាព្យាបាលទាំងអស់មេត្តាជ្រាបថា សាលានឹងមានការ**ឈប់សម្រាក**ក្នុងឱកាស៖\n\n"
                f"🇰🇭 **{name_kh}**\n"
                f"🇬🇧 **{name_en}**\n"
                f"📅 **កាលបរិច្ឆេទ៖** {holiday_date}\n\n"
                "✨ *សូមជូនពរឱ្យទទួលបានការសម្រាកលំហែកាយយ៉ាងសប្បាយរីករាយ និងសុវត្ថិភាព!*"
            )

            teachers_res = supabase.table("teachers").select("telegram_id").execute()
            students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id").execute()

            target_chats, target_groups = set(), set()
            if teachers_res.data:
                for t in teachers_res.data:
                    if t.get('telegram_id'): target_chats.add(str(t['telegram_id']))
            if students_res.data:
                for s in students_res.data:
                    if s.get('parent_telegram_id'): target_chats.add(str(s['parent_telegram_id']))
                    if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "": target_groups.add(str(s['group_chat_id']).strip())

            count_private = count_group = 0
            for p_id in target_chats:
                try:
                    bot.send_message(p_id, announcement_msg, parse_mode='Markdown')
                    count_private += 1
                except Exception: pass
            for g_id in target_groups:
                try:
                    bot.send_message(g_id, announcement_msg, parse_mode='Markdown')
                    count_group += 1
                except Exception: pass

            bot.send_message(chat_id, f"🟢 **បន្ថែមថ្ងៃឈប់សម្រាកជោគជ័យ!**\n🎉 ឱកាស៖ `{name_kh}`\n📲 ផ្ញើទៅសមាជិក (Private)៖ `{count_private}` នាក់\n🏫 បាញ់ចូលគ្រុបថ្នាក់៖ `{count_group}` គ្រុប")
        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`")
 # ===================================================================================
    # 👨‍🏫 មុខងារ៖ បង្កើតគណនីគ្រូថ្មី (/addteacher) - ទម្រង់ Wizard Steps ពេញលេញ
    # ===================================================================================
    @bot.message_handler(commands=['addteacher'])
    def add_teacher_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិឡើយ។")
            return

        sent_msg = bot.send_message(chat_id, "➕ **[បង្កើតគណនីគ្រូ - ជំហាន ១/៣]** សូមបំពេញ **ID គ្រូ** (ឧទាហរណ៍៖ TCH001)៖")
        bot.register_next_step_handler(sent_msg, process_tch_id)

    def process_tch_id(message):
        chat_id = message.chat.id
        tch_id = message.text.strip().upper()
        
        try:
            # 🔍 🔒 របាំងការពារជាន់គ្នាទី ១
            check_exist = supabase.table("teachers").select("teacher_id").eq("teacher_id", tch_id).execute()
            if check_exist.data:
                bot.send_message(chat_id, f"❌ **ID គ្រូ `{tch_id}` នេះមានក្នុងប្រព័ន្ធរួចរាល់ហើយ!** សូមវាយ `/addteacher` ដើម្បីចាប់ផ្ដើមឡើងវិញ។")
                return
        except Exception: pass

        sent_msg = bot.send_message(chat_id, f"🆔 ID គ្រូ៖ `{tch_id}`\n\n👉 **[ជំហាន ២/៣]** សូមបំពេញ **ឈ្មោះលោកគ្រូ-អ្នកគ្រូ** ៖")
        bot.register_next_step_handler(sent_msg, process_tch_name, tch_id)

    def process_tch_name(message, tch_id):
        chat_id = message.chat.id
        tch_name = message.text.strip()
        sent_msg = bot.send_message(chat_id, f"🆔 ID គ្រូ៖ `{tch_id}`\n👤 ឈ្មោះ៖ `{tch_name}`\n\n👉 **[ជំហាន ៣/៣]** សូមកំណត់ **លេខសម្ងាត់ (Password)** សម្រាប់គ្រូ៖")
        bot.register_next_step_handler(sent_msg, process_tch_final, tch_id, tch_name)

    def process_tch_final(message, tch_id, tch_name):
        chat_id = message.chat.id
        pwd = message.text.strip()
        
        try:
            # 🔍 🔒 ជាន់ការពារ៖ ឆែកមើល ID គ្រូម្ដងទៀត ការពារការជាន់គ្នា
            check_exist = supabase.table("teachers").select("teacher_id").eq("teacher_id", tch_id).execute()
            if check_exist.data:
                bot.send_message(chat_id, f"❌ **ការបង្កើតត្រូវបានបដិសេធ៖** ID គ្រូ `{tch_id}` នេះមានក្នុងប្រព័ន្ធរួចរាល់ហើយ លោកនាយក! សូមវាយ `/addteacher` ដើម្បីចាប់ផ្ដើមឡើងវិញ។")
                return
                
            # 📥 រក្សាទុកទិន្នន័យចូលតារាង teachers តែមួយគត់ (ត្រូវតាម Schema DB បង ១០០%)
            res_tch = supabase.table("teachers").insert({
                "teacher_id": tch_id, 
                "name": tch_name, 
                "password": pwd
            }).execute()
            
            # ❌ (សម្អាតដាច់ខាត) លុបប្លុក supabase.table("users").insert(...) ចាស់ចោលទាំងស្រុង លែងឱ្យមានក្នុងកូដទៀតហើយ
            
            if res_tch.data:
                success_text = (
                    "🟢 **[ បង្កើតគណនីគ្រូថ្មីជោគជ័យ! ]**\n"
                    "--------------------------------------------------\n"
                    f"🆔 **ID គ្រូបង្រៀន៖** `{tch_id}`\n"
                    f"👤 **នាមនិងគោត្តនាម៖** *{tch_name}*\n"
                    f"🔑 **លេខសម្ងាត់មេ៖** `{pwd}`\n"
                    "--------------------------------------------------\n"
                    "🤖 *លោកគ្រូ-អ្នកគ្រូអាចប្រើប្រាស់ ID និង Password នេះ ទៅវាយបញ្ជា `/tlogin` ដើម្បីចូលប្រព័ន្ធបានហើយបាទ!*"
                )
                bot.send_message(chat_id, success_text, parse_mode='Markdown')
            else:
                bot.send_message(chat_id, "❌ បរាជ័យ៖ ដាតាបេសបដិសេធការរក្សាទុក។")
                
        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេសដាតាបេស៖** `{e}`")
# ========================================================
    # 🏢 មុខងារ៖ ថែមផ្នែកឱ្យគ្រូ (/adddept) - ទម្រង់ Wizard Steps
    # ========================================================
    @bot.message_handler(commands=['adddept'])
    def add_dept_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
            return

        sent_msg = bot.send_message(chat_id, "🏢 **[ថែមផ្នែកឱ្យគ្រូ - ជំហាន ១/២]** សូមបំពេញ **ID គ្រូ** (ឧទាហរណ៍៖ TCH001)៖")
        bot.register_next_step_handler(sent_msg, process_dept_teacher)

    def process_dept_teacher(message):
        chat_id = message.chat.id
        t_id = message.text.strip()
        
        try:
            teacher_check = supabase.table("teachers").select("name").eq("teacher_id", t_id).execute()
            if not teacher_check.data:
                bot.send_message(chat_id, f"❌ **រកមិនឃើញគ្រូដែលមាន ID `{t_id}` ទេ!** សូមពិនិត្យមើល ID គ្រូឡើងវិញ។")
                return
            t_name = teacher_check.data[0]['name']
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")
            return

        sent_msg = bot.send_message(chat_id, f"👤 គ្រូ៖ `{t_name}` (ID: {t_id})\n\n👉 **[ជំហាន ២/២]** សូមបំពេញ **ឈ្មោះដេប៉ាតឺម៉ង់/ផ្នែក** ៖")
        bot.register_next_step_handler(sent_msg, process_dept_final, t_id, t_name)

    def process_dept_final(message, t_id, t_name):
        chat_id = message.chat.id
        dept_name = message.text.strip()
        try:
            dept_res = supabase.table("departments").upsert({"department_name": dept_name}, on_conflict="department_name").execute()
            dept_id = dept_res.data[0]['id']
            supabase.table("teachers").update({"department_id": dept_id}).eq("teacher_id", t_id).execute()
            bot.send_message(chat_id, f"🟢 **រៀបចំរចនាសម្ព័ន្ធគ្រូជោគជ័យ!**\n🏢 ផ្នែក៖ `{dept_name}` (ID: {dept_id})\n👤 គ្រូ៖ `{t_name}`")
        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`")


    # ========================================================
    # 🎓 មុខងារ៖ ថែមជំនាញឱ្យគ្រូ (/addmajor) - ទម្រង់ Wizard Steps
    # ========================================================
    @bot.message_handler(commands=['addmajor'])
    def add_major_wizard(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
        if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
            bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!**")
            return

        sent_msg = bot.send_message(chat_id, "🎓 **[ថែមជំនាញឱ្យគ្រូ - ជំហាន ១/៣]** សូមបំពេញ **ID គ្រូ** (ឧទាហរណ៍៖ TCH001)៖")
        bot.register_next_step_handler(sent_msg, process_major_teacher)

    def process_major_teacher(message):
        chat_id = message.chat.id
        t_id = message.text.strip()
        try:
            teacher_check = supabase.table("teachers").select("name").eq("teacher_id", t_id).execute()
            if not teacher_check.data:
                bot.send_message(chat_id, f"❌ **រកមិនឃើញគ្រូដែលមាន ID `{t_id}` ទេ!**")
                return
            t_name = teacher_check.data[0]['name']
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")
            return
            
        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ២/៣]** សូមបំពេញ **ឈ្មោះផ្នែក/ដេប៉ាតឺម៉ង់** ៖")
        bot.register_next_step_handler(sent_msg, process_major_dept, t_id, t_name)

    def process_major_dept(message, t_id, t_name):
        chat_id = message.chat.id
        dept_name = message.text.strip()
        try:
            dept_res = supabase.table("departments").select("id").eq("department_name", dept_name).execute()
            if not dept_res.data:
                bot.send_message(chat_id, f"❌ **រកមិនឃើញផ្នែកឈ្មោះ `{dept_name}` ទេ!** សូមបង្កើតផ្នែកនេះជាមួយ `/adddept` មុនសិន។")
                return
            dept_id = dept_res.data[0]['id']
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")
            return

        sent_msg = bot.send_message(chat_id, f"👉 **[ជំហាន ៣/៣]** សូមបំពេញ **ឈ្មោះជំនាញថ្មី (Major)** ៖")
        bot.register_next_step_handler(sent_msg, process_major_final, t_id, t_name, dept_name, dept_id)

    def process_major_final(message, t_id, t_name, dept_name, dept_id):
        chat_id = message.chat.id
        major_name = message.text.strip()
        try:
            major_res = supabase.table("majors").upsert({"department_id": dept_id, "major_name": major_name}, on_conflict="department_id, major_name").execute()
            major_id = major_res.data[0]['id']
            supabase.table("teachers").update({"major_id": major_id}).eq("teacher_id", t_id).execute()
            bot.send_message(chat_id, f"🟢 **ភ្ជាប់ជំនាញសិក្សាជូនគ្រូរួចរាល់!**\n🏢 ផ្នែក៖ `{dept_name}`\n🎓 ជំនាញ៖ `{major_name}`\n👤 គ្រូ៖ `{t_name}`")
        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`")


    # ========================================================
    # 📊 មុខងារ៖ /ld មើលវត្តមានសិស្សទាំងអស់ក្នុងថ្នាក់
    # ========================================================
    @bot.message_handler(commands=['ld'])
    def teacher_view_attendance_report(message):
        chat_id = message.chat.id
        text = message.text.strip()
        parts = text.split(' ')
        
        if len(parts) < 2 or parts[1].strip() == "":
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយលោកគ្រូ!** សូមវាយ៖ `/ld ឈ្មោះថ្នាក់`", parse_mode='Markdown')
            return
            
        class_target = parts[1].strip()
        
        try:
            bot.send_message(chat_id, f"🔍 កំពុងទាញយកទិន្នន័យវត្តមានថ្នាក់ *{class_target}*...", parse_mode='Markdown')
            att_res = supabase.table("attendance").select("*").eq("class_level", class_target).order("date", descending=True).execute()
            
            if not att_res.data:
                bot.send_message(chat_id, f"❌ **មិនទាន់មានទិន្នន័យវត្តមាន** សម្រាប់ថ្នាក់ {class_target} ឡើយទេ។")
                return
                
            report_msg = f"📊 **[ របាយការណ៍វត្តមានសិស្ស៖ ថ្នាក់ {class_target} ]**\n--------------------------------------------------\n"
            for row in att_res.data:
                s_name = row.get('student_name', 'មិនស្គាល់ឈ្មោះ')
                status = row.get('status', 'PENDING').upper()
                status_emoji = "🟢 មក" if status in ["PRESENT", "វត្តមាន", "មក"] else "🔴 អវត្តមាន" if status in ["ABSENT", "អវត្តមាន"] else "🟡 ច្បាប់"
                report_msg += f"🔹 {s_name}  👉  {status_emoji}\n"
                
            bot.send_message(chat_id, report_msg, parse_mode='Markdown')
            
        except Exception as e:
            bot.reply_to(message, f"❌ មិនអាចទាញរបាយការណ៍បានទេ៖ `{e}`")


    # ========================================================
    # 📝 មុខងារ៖ /lh ទាញយកកិច្ចការសិស្ស (PDF/Picture) មកមើល
    # ========================================================
    @bot.message_handler(commands=['lh'])
    def teacher_view_submissions(message):
        chat_id = message.chat.id
        text = message.text.strip()
        parts = text.split(' ')
        
        if len(parts) < 2 or parts[1].strip() == "":
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ!** សូមវាយ៖ `/lh ឈ្មោះថ្នាក់`", parse_mode='Markdown')
            return
            
        class_target = parts[1].strip()
        
        try:
            bot.send_message(chat_id, f"🔍 កំពុងស្វែងរកកិច្ចការផ្ទះរបស់ថ្នាក់ *{class_target}*...", parse_mode='Markdown')
            sub_res = supabase.table("student_submissions").select("*").eq("class_level", class_target).eq("status", "PENDING").execute()
            
            if not sub_res.data:
                bot.send_message(chat_id, f"✨ **មិនមានកិច្ចការដែលត្រូវដាក់ពិន្ទុទេ** សម្រាប់ថ្នាក់ {class_target}។")
                return
                
            for sub in sub_res.data:
                sub_id = sub['id']               
                s_id = sub['student_id']     
                file_telegram_id = sub['submitted_file']  
                f_type = sub.get('submitted_type', 'document')     
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(f"✍️ ដាក់ពិន្ទុឱ្យសិស្ស {s_id}", callback_data=f"grh_{sub_id}"))
                
                info_text = f"👤 **កូដសិស្ស៖** `{s_id}`\n🏫 **ថ្នាក់៖** `{class_target}`\n📂 ឯកសារភ្ជាប់៖ `{f_type.upper()}`"
                
                if 'photo' in f_type.lower():
                    bot.send_photo(chat_id, photo=file_telegram_id, caption=info_text, parse_mode='Markdown', reply_markup=markup)
                else:
                    bot.send_document(chat_id, document=file_telegram_id, caption=info_text, parse_mode='Markdown', reply_markup=markup)
                    
        except Exception as e:
            bot.reply_to(message, f"❌ មិនអាចទាញទិន្នន័យកិច្ចការសិស្សបានទេ៖ `{e}`")


    # ========================================================
    # 🎛️ មុខងារ៖ ស្ទាក់ចាប់ប៊ូតុង Inline "✍️ ដាក់ពិន្ទុឱ្យ..."
    # ========================================================
    @bot.callback_query_handler(func=lambda call: call.data.startswith('grh_'))
    def handle_grade_button_click(call):
        sub_id = call.data.split('_')[1]
        instruction = (
            f"✍️ **[ វគ្គបញ្ចូលពិន្ទុ ]**\n"
            f"លោកគ្រូអាចបញ្ចូលពិន្ទុឱ្យកិច្ចការលេខ `{sub_id}` បានដោយចុចប៊ូតុង ឬវាយ៖\n"
            f"👉 `/grade` រួចបំពេញតាមលំដាប់លំដោយបាទ។"
        )
        bot.send_message(call.message.chat.id, instruction, parse_mode='Markdown')
        bot.answer_callback_query(call.id)


    # ========================================================
    # 🔍 មុខងារ៖ មើលបញ្ជីសិស្សចុះឈ្មោះថ្មី (/checkreq)
    # ========================================================
    @bot.message_handler(commands=['checkreq'])
    def check_requests_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.send_message(chat_id, "❌ **សកម្មភាពត្រូវបានបដិសេធ!**")
                return

            bot.send_message(chat_id, "🔍 **កំពុងស្វែងរកសិស្សដែលទាមទារការអនុម័ត (Pending)...**")
            students_res = supabase.table("students").select("*").ilike("student_id", "PENDING%").execute()

            if not students_res.data:
                bot.send_message(chat_id, "✨ **លទ្ធផល៖** មិនមានសិស្សណាម្នាក់ដែលកំពុងរង់ចាំការអនុម័តទេ។")
                return

            response_msg = f"📋 **[ បញ្ជីសិស្សកំពុងរង់ចាំការអនុម័ត៖ {len(students_res.data)} នាក់ ]**\n"
            response_msg += "--------------------------------------------------\n\n"
            
            for index, student in enumerate(students_res.data, start=1):
                stu_id = student.get('student_id', '-')
                parent_tg = student.get('parent_telegram_id', 'គ្មាន ID')
                stu_name = student.get('name', 'មិនទាន់បំពេញ')
                stu_gender = student.get('gender', '-')
                stu_class = student.get('class_level', '-')
                
                response_msg += f"{index}. 👤 **ឈ្មោះ៖** *{stu_name}*\n"
                response_msg += f"🆔 **ID សិស្ស៖** `{stu_id}`\n"
                response_msg += f"🚻 **ភេទ៖** `{stu_gender}` | 🏫 **ថ្នាក់៖** `{stu_class}`\n"
                response_msg += f"📱 **Parent Telegram ID៖** `{parent_tg}`\n"
                response_msg += f"👉 **អនុម័ត៖** `/approve {parent_tg}, DUC{index:03d}`\n"
                response_msg += "--------------------------------------------------\n\n"
            
            bot.send_message(chat_id, response_msg, parse_mode='Markdown')

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: `{e}`")


    # ========================================================
    # 🟢 មុខងារ៖ Admin វាយ /approve ដើម្បីបើកសិទ្ធិឱ្យសិស្ស
    # ========================================================
    @bot.message_handler(commands=['approve'])
    def approve_user_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            input_text = message.text.strip()[8:].strip()
            if not input_text or "," not in input_text:
                bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ Admin!**\nសូមវាយ៖ `/approve លេខTelegramID, លេខIDសិស្ស`", parse_mode='Markdown')
                return

            parts = input_text.split(",")
            target_tg_id = parts[0].strip()
            new_student_id = parts[1].strip().upper() 

            bot.send_message(chat_id, f"⏳ **កំពុងអនុម័តគណនី Telegram ID: `{target_tg_id}`...**")

            target_user = supabase.table("users").select("*").eq("telegram_id", target_tg_id).execute()
            if not target_user.data:
                bot.reply_to(message, f"❌ រកមិនឃើញគណនី Telegram ID: `{target_tg_id}` នេះក្នុងតារាង users ទេ។")
                return
                
            supabase.table("users").update({
                "status": "APPROVED",
                "student_id": new_student_id
            }).eq("telegram_id", target_tg_id).execute()

            supabase.table("students").update({
                "student_id": new_student_id
            }).eq("parent_telegram_id", target_tg_id).execute()
            
            db_student_status = "✅ (បានអាប់ដេតលេខកូដសិស្សចូលតារាង students រួចរាល់)"

            try:
                alert_student = (
                    "🎉 **សូមអបអរសាទរ! គណនីរបស់អ្នកត្រូវបានអនុម័តហើយ**\n"
                    "--------------------------------------------------\n"
                    f"👑 **លេខកូដសិស្ស៖** `{new_student_id}`\n"
                    "🤖 ឥឡូវនេះ លោកអ្នកអាចប្រើប្រាស់មឺនុយសាលាអនឡាញ DUC បានហើយ!"
                )
                bot.send_message(target_tg_id, alert_student, parse_mode='Markdown')
                student_notified = "✅ (បានផ្ញើសារជូនដំណឹងទៅសិស្សរួចរាល់)"
            except Exception:
                student_notified = "❌ (មិនអាចផ្ញើសារទៅសិស្សបាន)"

            bot.send_message(chat_id, f"🟢 **អនុម័តជោគជ័យ!**\n\n🆔 **Telegram ID៖** `{target_tg_id}`\n👑 **ID សាលា៖** `{new_student_id}`\n📱 **Status:** `APPROVED`\n🗂️ {db_student_status}\n🔔 {student_notified}", parse_mode='Markdown')

        except Exception as e:
            bot.send_message(chat_id, f"❌ **Bot Error:** `{e}`", parse_mode='Markdown')


    # ========================================================
    # 🎚️ មុខងារ៖ /setclass ដើម្បីភ្ជាប់ ID គ្រុបទៅកាន់ថ្នាក់រៀន
    # ========================================================
    @bot.message_handler(commands=['setclass'])
    def set_class_group_id_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if message.chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "⚠️ **មុខងារនេះសម្រាប់ប្រើប្រាស់នៅក្នុង Group ថ្នាក់រៀនតែប៉ុណ្ណោះបាទ!**")
            return
            
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិជា Admin ឡើយ។")
                return

            class_name_input = message.text.strip()[9:].strip().upper()
            
            if not class_name_input:
                bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ Admin!**\nសូមវាយ៖ `/setclass ឈ្មោះថ្នាក់`")
                return

            bot.reply_to(message, f"⏳ **កំពុងភ្ជាប់ ID គ្រុបនេះ ទៅកាន់សិស្សថ្នាក់ `{class_name_input}` ទាំងអស់...**")

            update_res = supabase.table("students").update({"group_chat_id": str(chat_id)}).eq("class_level", class_name_input).execute()

            if update_res.data:
                success_msg = (
                    f"🎯 **ភ្ជាប់គ្រុបថ្នាក់រៀនអូតូជោគជ័យ!**\n\n"
                    f"🏫 **ថ្នាក់រៀន៖** `{class_name_input}`\n"
                    f"🆔 **ID គ្រុបដែលចាប់បាន៖** `{chat_id}`\n"
                    f"👥 **عددសិស្សដែលទទួលបាន៖** `{len(update_res.data)}` នាក់ត្រូវបានដាក់បញ្ចូល។"
                )
                bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            else:
                bot.send_message(chat_id, f"⚠️ **ធ្វើបច្ចុប្បន្នភាពបរាជ័យ!**\nរកមិនឃើញសិស្សក្នុងថ្នាក់ `{class_name_input}` ទេ។", parse_mode='Markdown')

        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')


    # ========================================================
    # 📊 មុខងារ៖ /school_stats ដើម្បីមើលស្ថិតិសរុបនៃសាលារៀន
    # ========================================================
    @bot.message_handler(commands=['school_stats'])
    def school_stats_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!**")
                return

            bot.send_message(chat_id, "⏳ **កំពុងប្រមូលទិន្នន័យ និងគណនាស្ថិតិរួមពី Supabase...**")

            students_res = supabase.table("students").select("student_id", count="exact").execute()
            total_students = students_res.count if students_res.count is not None else 0

            teachers_res = supabase.table("teachers").select("teacher_id", count="exact").execute()
            total_teachers = teachers_res.count if teachers_res.count is not None else 0

            schedules_res = supabase.table("schedules").select("class_level").execute()
            distinct_classes = set(sch['class_level'].strip().upper() for sch in schedules_res.data if sch.get('class_level')) if schedules_res.data else set()

            dept_res = supabase.table("departments").select("id", count="exact").execute()
            total_depts = dept_res.count if dept_res.count is not None else 0

            notices_res = supabase.table("school_notices").select("id", count="exact").execute()
            total_notices = notices_res.count if notices_res.count is not None else 0

            stats_msg = (
                "📊 **[ របាយការណ៍ស្ថិតិរួមរបស់សាលា DUC ]**\n"
                f"📆 *គិតត្រឹមថ្ងៃទី៖ {datetime.now().strftime('%d-%m-%Y')}*\n"
                f"----------------------------------------\n\n"
                f"👨‍🎓 **សិស្សានុសិស្សសរុប៖** `{total_students}` នាក់\n"
                f"👨‍🏫 **លោកគ្រូ-អ្នកគ្រូសរុប៖** `{total_teachers}` នាក់\n"
                f"🏫 **ថ្នាក់រៀនសកម្មសរុប៖** `{len(distinct_classes)}` ថ្នាក់\n"
                f"🏢 **ដេប៉ាតាម៉ង់/ផ្នែកសរុប៖** `{total_depts}` ផ្នែក\n"
                f"📢 **សេចក្ដីប្រកាសដែលបានផ្សាយ៖** `{total_notices}` លើក\n\n"
                f"----------------------------------------\n"
                "📈 _ទិន្នន័យត្រូវបានធ្វើបច្ចុប្បន្នភាពអូតូពីប្រព័ន្ធ API Core Engine_"
            )
            bot.send_message(chat_id, stats_msg, parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')


    # ========================================================
    # 📈 មុខងារ៖ /hw_analytics វិភាគភាគរយប្រគល់កិច្ចការ
    # ========================================================
    @bot.message_handler(commands=['hw_analytics'])
    def hw_analytics_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!**")
                return

            bot.send_message(chat_id, "⏳ **កំពុងវិភាគទិន្នន័យ Homework និងគណនាភាគរយ...**")

            hw_res = supabase.table("homework").select("id", "class_level").execute()
            submissions_res = supabase.table("student_submissions").select("homework_id", "status").execute()
            students_res = supabase.table("students").select("class_level").execute()

            if not hw_res.data:
                bot.send_message(chat_id, "ℹ️ **មិនទាន់មានទិន្នន័យកិច្ចការផ្ទះនៅក្នុងប្រព័ន្ធនៅឡើយទេ។**")
                return

            class_student_count = {}
            if students_res.data:
                for s in students_res.data:
                    c_level = s.get('class_level', '').strip().upper()
                    if c_level: class_student_count[c_level] = class_student_count.get(c_level, 0) + 1

            class_analytics = {}
            for hw in hw_res.data:
                c_level = hw.get('class_level', '').strip().upper()
                if not c_level: continue
                if c_level not in class_analytics:
                    class_analytics[c_level] = {"total_hw_assigned": 0, "expected_submissions": 0, "actual_submissions": 0}
                class_analytics[c_level]["total_hw_assigned"] += 1
                class_analytics[c_level]["expected_submissions"] += class_student_count.get(c_level, 0)

            if submissions_res.data:
                hw_to_class = {hw['id']: hw['class_level'].strip().upper() for hw in hw_res.data if hw.get('class_level')}
                for sub in submissions_res.data:
                    hw_id = sub.get('homework_id')
                    status = sub.get('status', '').upper()
                    if hw_id in hw_to_class and status in ['SUBMITTED', 'GRADED']:
                        c_level = hw_to_class[hw_id]
                        if c_level in class_analytics: class_analytics[c_level]["actual_submissions"] += 1

            report_msg = "📊 [ របាយការណ៍វិភាគកិច្ចការផ្ទះ (Homework Analytics) ]\n========================================\n\n"
            for c_level, data in sorted(class_analytics.items()):
                assigned = data["total_hw_assigned"]
                expected = data["expected_submissions"]
                actual = data["actual_submissions"]
                rate = (actual / expected * 100) if expected > 0 else 0.0
                emoji = "🟢" if rate >= 80 else "🟡" if rate >= 50 else "🔴"
                report_msg += f"{emoji} ថ្នាក់៖ {c_level}\n └ 📚 ចំនួនកិច្ចការ៖ {assigned} មេរៀន\n └ 📥 អត្រាប្រគល់៖ {actual}/{expected} ដង\n └ 📊 ភាគរយ៖ {rate:.1f}%\n\n"

            report_msg += "========================================\n🟢 ឧស្សាហ៍ (>=80%) | 🟡 មធ្យម (50-79%) | 🔴 ខ្ជិល (<50%)"
            bot.send_message(chat_id, report_msg)
        except Exception as e:
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`")


   # ===================================================================================
    # 🏫 បញ្ជីទី ១៖ /list_classes រាយឈ្មោះថ្នាក់ (ជួសជុលការមិនដើរ និងលុបថ្នាក់ឌុប)
    # ===================================================================================
    @bot.message_handler(commands=['list_classes'])
    def list_classes_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            students_res = supabase.table("students").select("class_level").execute()
            schedules_res = supabase.table("schedules").select("class_level").execute()
            
            distinct_classes = set()
            if students_res.data:
                for s in students_res.data:
                    if s.get('class_level'): distinct_classes.add(s['class_level'].strip().upper())
            if schedules_res.data:
                for sch in schedules_res.data:
                    if sch.get('class_level'): distinct_classes.add(sch['class_level'].strip().upper())

            if not distinct_classes:
                bot.send_message(chat_id, "ℹ️ មិនទាន់មានទិន្នន័យថ្នាក់រៀននៅក្នុងប្រព័ន្ធឡើយ។")
                return

            msg = f"🏫 [ បញ្ជីឈ្មោះថ្នាក់រៀនសកម្មសរុប៖ {len(distinct_classes)} ថ្នាក់ ]\n"
            msg += "========================================\n"
            for i, c_name in enumerate(sorted(distinct_classes), 1):
                msg += f"{i}. ថ្នាក់៖ {c_name}\n"
            msg += "========================================\n"
            msg += "👇 លោកអ្នកអាចចុចលើប៊ូតុងខាងក្រោម ដើម្បីមើលបញ្ជីឈ្មោះសិស្សភ្លាមៗ៖"

            markup = types.InlineKeyboardMarkup(row_width=2)
            # 💡 រៀបចំប៊ូតុងឱ្យស្អាត លុបបំបាត់ការឌុបថ្នាក់លើអេក្រង់
            btn_list = [types.InlineKeyboardButton(f"📖 ថ្នាក់ {c}", callback_data=f"view_students:{c}") for c in sorted(distinct_classes)]
            markup.add(*btn_list)
            
            bot.send_message(chat_id, msg, reply_markup=markup)
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេស៖ {e}")


    # ===================================================================================
    # 🏢 បញ្ជីទី ២៖ /list_depts រាយឈ្មោះផ្នែក (ដោះស្រាយ BUTTON_DATA_INVALID)
    # ===================================================================================
    @bot.message_handler(commands=['list_depts'])
    def list_depts_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            dept_res = supabase.table("departments").select("id", "department_name").execute()
            
            if not dept_res.data:
                bot.send_message(chat_id, "ℹ️ មិនទាន់មានទិន្នន័យដេប៉ាតាម៉ង់/ផ្នែកនៅក្នុងប្រព័ន្ធឡើយ។")
                return

            msg = f"🏢 [ បញ្ជីឈ្មោះដេប៉ាតាម៉ង់/ផ្នែកសរុប៖ {len(dept_res.data)} ផ្នែក ]\n"
            msg += "========================================\n"
            for i, d in enumerate(dept_res.data, 1):
                msg += f"{i}. ផ្នែក៖ {d.get('department_name', 'មិនមានឈ្មោះ')}\n"
            msg += "========================================\n"
            msg += "👇 លោកអ្នកអាចចុចលើប៊ូតុងខាងក្រោម ដើម្បីមើលមុខវិជ្ជាសកម្មក្នុងផ្នែកនីមួយៗ៖"

            markup = types.InlineKeyboardMarkup(row_width=1)
            # 💡 បោះទៅតែ ID សុទ្ធ ដើម្បីកុំឱ្យវែងហួសកំណត់ 64 Bytes ចៀសវាងការចុចមិនដើរ
            btn_list = [types.InlineKeyboardButton(f"🏢 {d.get('department_name')}", callback_data=f"view_dept:{d.get('id')}") for d in dept_res.data]
            markup.add(*btn_list)
            
            bot.send_message(chat_id, msg, reply_markup=markup)
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេស៖ {e}")


    # ===================================================================================
    # 👨‍🏫 បញ្ជីទី ៣៖ /list_teachers រាយឈ្មោះគ្រូ (ជួសជុលការចុចប៊ូតុងគាំង)
    # ===================================================================================
    @bot.message_handler(commands=['list_teachers'])
    def list_teachers_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ សកម្មភាពត្រូវបានបដិសេធ! លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            teachers_res = supabase.table("teachers").select("teacher_id", "name").execute()
            
            if not teachers_res.data:
                bot.send_message(chat_id, "ℹ️ មិនទាន់មានទិន្នន័យលោកគ្រូ-អ្នកគ្រូនៅក្នុងប្រព័ន្ធឡើយ។")
                return

            msg = f"👨‍🏫 [ បញ្ជីឈ្មោះលោកគ្រូ-អ្នកគ្រូសរុប៖ {len(teachers_res.data)} នាក់ ]\n"
            msg += "========================================\n"
            for i, t in enumerate(teachers_res.data, 1):
                msg += f"{i}. ID: {t.get('teacher_id')} | លោកគ្រូ-អ្នកគ្រូ៖ {t.get('name')}\n"
            msg += "========================================\n"
            msg += "👇 លោកអ្នកអាចចុចលើប៊ូតុងខាងក្រោម ដើម្បីមើលព័ត៌មានលម្អិតរបស់គ្រូម្នាក់ៗ៖"

            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_list = [types.InlineKeyboardButton(f"👨‍🏫 {t.get('name')}", callback_data=f"view_teacher:{t.get('teacher_id')}") for t in teachers_res.data]
            markup.add(*btn_list)
            
            bot.send_message(chat_id, msg, reply_markup=markup)
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេស៖ {e}")


    # ====================================================================================================
    # 📡 ៤. ផ្ទាំងប្រមូលផ្ដុំគ្រាប់ចាប់សកម្មភាពចុចប៊ូតុងទាំងអស់ (ALL CALLBACK HANDLERS - ដំណើរការ ១០០%)
    # ====================================================================================================
    
    # 📡 ៤.១ ចាប់សកម្មភាពពេលចុចមើល «សិស្សក្នុងថ្នាក់»
    @bot.callback_query_handler(func=lambda call: call.data.startswith('view_students:'))
    def callback_view_students(call):
        chat_id = call.message.chat.id
        try:
            user_id = call.from_user.id
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.answer_callback_query(call.id, "❌ សកម្មភាពត្រូវបានបដិសេធ!", show_alert=True)
                return

            target_class = call.data.split(':', 1)[1]
            bot.answer_callback_query(call.id, f"កំពុងទាញទិន្នន័យថ្នាក់ {target_class}...")

            students_res = supabase.table("students").select("student_id", "name", "gender").eq("class_level", target_class).execute()
            
            if not students_res.data:
                bot.send_message(chat_id, f"ℹ️ មិនទាន់មានសិស្សចុះឈ្មោះក្នុងថ្នាក់ '{target_class}' នៅឡើយទេ។")
                return

            msg = f"👨‍🎓 [ បញ្ជីឈ្មោះសិស្សានុសិស្សក្នុងថ្នាក់៖ {target_class} ]\n"
            msg += f"📊 ចំនួនសិស្សសរុប៖ {len(students_res.data)} នាក់\n"
            msg += "========================================\n"
            for i, stu in enumerate(students_res.data, 1):
                g_kh = "ប្រុស" if stu.get('gender', '').upper() == 'M' else "ស្រី" if stu.get('gender', '').upper() == 'F' else stu.get('gender')
                msg += f"{i}. ID: {stu.get('student_id')} | ឈ្មោះ: {stu.get('name')} ({g_kh})\n"
            msg += "========================================\n"
            bot.send_message(chat_id, msg)
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេស៖ {e}")

    # 📡 ៤.២ ចាប់សកម្មភាពពេលចុចមើល «មុខវិជ្ជាតាមដេប៉ាតាម៉ង់»
    @bot.callback_query_handler(func=lambda call: call.data.startswith('view_dept:'))
    def callback_view_dept(call):
        chat_id = call.message.chat.id
        try:
            user_id = call.from_user.id
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.answer_callback_query(call.id, "❌ សកម្មភាពត្រូវបានបដិសេធ!", show_alert=True)
                return

            target_dept_id = call.data.split(':', 1)[1]
            
            dept_info = supabase.table("departments").select("department_name").eq("id", target_dept_id).execute()
            dept_name = dept_info.data[0].get('department_name', 'មិនមានឈ្មោះ') if dept_info.data else "ផ្នែកទូទៅ"
            
            bot.answer_callback_query(call.id, f"កំពុងទាញទិន្នន័យ {dept_name}...")

            # 💡 ទាញយកមុខវិជ្ជាមកបង្ហាញឱ្យចំតារាង schedules 
            hw_res = supabase.table("schedules").select("subject_name").execute()
            msg = f"🏢 [ បញ្ជីឈ្មោះមុខវិជ្ជាសកម្មក្នុង៖ {dept_name} ]\n"
            msg += "========================================\n"

            if hw_res.data:
                distinct_subjects = set(hw.get('subject_name').strip() for hw in hw_res.data if hw.get('subject_name'))
                found_sub = False
                sub_idx = 1
                for sub in sorted(distinct_subjects):
                    msg += f"  └ {sub_idx}. មុខវិជ្ជា៖ {sub}\n"
                    sub_idx += 1
                    found_sub = True
                if not found_sub: msg += "  └ (មិនទាន់មានមុខវិជ្ជាដំឡើងក្នុងផ្នែកនេះឡើយ)\n"
            else:
                msg += "  └ (មិនទាន់មានទិន្នន័យមុខវិជ្ជាសកម្មក្នុងប្រព័ន្ធ)\n"
            msg += "========================================\n"
            bot.send_message(chat_id, msg)
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេស៖ {e}")

    # 📡 ៤.៣ ចាប់សកម្មភាពពេលចុចមើល «ប្រវត្តិរូប និងបន្ទុករបស់គ្រូ»
    @bot.callback_query_handler(func=lambda call: call.data.startswith('view_teacher:'))
    def callback_view_teacher(call):
        chat_id = call.message.chat.id
        try:
            user_id = call.from_user.id
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.answer_callback_query(call.id, "❌ សកម្មភាពត្រូវបានបដិសេធ!", show_alert=True)
                return

            target_teacher_id = call.data.split(':', 1)[1]
            bot.answer_callback_query(call.id, f"កំពុងទាញទិន្នន័យគ្រូ ID: {target_teacher_id}...")

            teacher_info = supabase.table("teachers").select("*").eq("teacher_id", target_teacher_id).execute()
            # 💡 កែសម្រួល៖ ប្ដូរទៅហៅ 'study_day' ឱ្យត្រូវនឹងរចនាសម្ព័ន្ធតារាង schedules របស់បង
            schedule_info = supabase.table("schedules").select("class_level", "subject_name", "study_day", "start_time", "end_time").eq("teacher_id", target_teacher_id).execute()

            if not teacher_info.data:
                bot.send_message(chat_id, "❌ រកមិនឃើញទិន្នន័យគ្រូម្នាក់នេះឡើយ។")
                return

            t_data = teacher_info.data[0]
            msg = "📋 [ ព័ត៌មានលម្អិតរបស់លោកគ្រូ-អ្នកគ្រូ ]\n"
            msg += "========================================\n"
            msg += f"🆔 អត្តសញ្ញាណ ID៖ {t_data.get('teacher_id')}\n"
            msg += f"👤 នាមនិងគោត្តនាម៖ {t_data.get('name')}\n"
            msg += f"📞 លេខទូរស័ព្ទ៖ {t_data.get('phone', 'N/A')}\n"
            msg += "----------------------------------------\n"
            msg += "🏫 បន្ទុកថ្នាក់ និងមុខវិជ្ជាបង្រៀន៖\n"
            if schedule_info.data:
                for idx, sch in enumerate(schedule_info.data, 1):
                    msg += f"  ├ {idx}. {sch.get('subject_name')} (ថ្នាក់៖ {sch.get('class_level')}) \n"
                    msg += f"  │  └ ថ្ងៃ៖ {sch.get('study_day')} ({sch.get('start_time')} - {sch.get('end_time')})\n"
            else:
                msg += "  └ (មិនទាន់មានកាលវិភាគបង្រៀនឡើយ)\n"
            msg += "========================================\n"
            bot.send_message(chat_id, msg)
        except Exception as e:
            bot.send_message(chat_id, f"❌ កំហុសបច្ចេកទេស៖ {e}")
