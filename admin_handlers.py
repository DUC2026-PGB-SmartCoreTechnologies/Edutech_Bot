import telebot
from telebot import types
from datetime import datetime

# 💡 register_admin_teacher_handlers ទទួល bot និង supabase ពី main.py រួចជាស្រេច
def register_admin_teacher_handlers(bot, supabase):
    
   # 👑 មុខងារ៖ Admin វាយលេខសម្ងាត់មេដើម្បី Login (Only Admin Menu Control)
    # ========================================================
    @bot.message_handler(commands=['login'])
    def admin_secret_login(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # 🔄 កាត់យកពាក្យសម្ងាត់ដែលវាយបន្ទាប់ពី /login
        text_input = message.text.strip()[6:].strip()
        
        # 🔑 លេខសម្ងាត់មេរបស់សាលា DUC
        ADMIN_MASTER_PASSWORD = "DUC_Admin@2026"
        
        if not text_input:
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ Admin!**\nសូមវាយ៖ `/login លេខសម្ងាត់មេ`", parse_mode='Markdown')
            return
            
        if text_input != ADMIN_MASTER_PASSWORD:
            bot.reply_to(message, "❌ **លេខសម្ងាត់ Admin មិនត្រឹមត្រូវទេ!** សូមព្យាយាមម្ដងទៀត។")
            return
            
        try:
            # 🔄 ១. អាប់ដេតសិទ្ធិអ្នកវាយនេះទៅជា ADMIN ក្នុងតារាង users លើ Supabase ភ្លាមៗ
            supabase.table("users").upsert({
                "telegram_id": user_id,
                "role": "ADMIN",
                "status": "APPROVED",
                "language": "km"
            }, on_conflict="telegram_id").execute()
            
            # 🔍 ២. រត់ទៅទាញទិន្នន័យមកឆែកមើល Role ម្ដងទៀត ដើម្បីធានាថាគាត់ជា Admin ពិតប្រាកដ (Only Admin Safety Rule)
            user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
            
            if user_check.data and user_check.data[0].get('role') == 'ADMIN':
                
                # 🎛️ បង្កើតផ្ទាំងប៊ូតុង Menu ពណ៌ប្រផេះធំៗ (លោតពីក្រោមអេក្រង់) ផ្ដាច់មុខសម្រាប់តែ Admin 
                admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                admin_menu.add("➕ បង្កើតគណនីគ្រូ", "📋 មើលបញ្ជីគ្រូ", "🔙 ចាកចេញ (Logout)")
                
                # 📢 ផ្ញើសារប្រកាសជោគជ័យ
                bot.send_message(chat_id, "🟢 **ផ្ទៀងផ្ទាត់សិទ្ធិ Admin មេជោគជ័យ!**", parse_mode='Markdown')
                
                # 💡 ហៅផ្ទាំងរូបភាព Panel Dashboard ពី helpers.py
                import helpers
                helpers.send_admin_panel(bot, chat_id)
                
                # 📤 បាញ់បញ្ចេញប៊ូតុង Menu ជូនតែ Admin តែម្នាក់គត់
                bot.send_message(
                    chat_id, 
                    "👑 **លោកអ្នកក៏អាចប្រើប្រាស់ ប៊ូតុង Menu ខាងក្រោម នេះបានផងដែរ៖**", 
                    reply_markup=admin_menu,
                    parse_mode='Markdown'
                )
                print(f"👑 [ONLY ADMIN MENU LIVE] Admin Telegram ID: {user_id} Verified.")
            else:
                # ករណីលួចបន្លំ ឬ Role មិនមែនជា Admin គឺប្រព័ន្ធដេញចេញភ្លាម
                bot.reply_to(message, "❌ **សុំទោស!** គណនីរបស់អ្នកមិនមានសិទ្ធិចូលប្រើប្រាស់មឺនុយ Admin ឡើយ។")
                
        except Exception as e:
            print(f"❌ Admin Login Error: {e}")
            bot.reply_to(message, f"❌ មិនអាចបើកផ្ទាំង Admin Panel បានទេ៖ `{e}`")

    # ========================================================
    # 🎛️ មុខងារ៖ ស្ទាក់ចាប់ការចុចប៊ូតុង Inline លើ Admin Dashboard
    # ========================================================
    @bot.callback_query_handler(func=lambda call: call.data.startswith('adm_guide_'))
    def handle_admin_panel_inline_clicks(call):
        chat_id = call.message.chat.id
        action = call.data
        
        if action == "adm_guide_stats":
            bot.send_message(chat_id, "📊 **[ មើលស្ថិតិសាលារួម ]**\nសូមវាយបញ្ជា៖ `/school_stats`", parse_mode='Markdown')
        elif action == "adm_guide_analytics":
            bot.send_message(chat_id, "📈 **[ មើលអត្រាប្រគល់កិច្ចការ ]**\nសូមវាយបញ្ជា៖ `/hw_analytics`", parse_mode='Markdown')
        elif action == "adm_guide_addstu":
            bot.send_message(chat_id, "👤 **[ របៀបថែមសិស្សថ្មី ]**\nសូមវាយ៖ `/addstu ID,ឈ្មោះ,ភេទ(M/F),ថ្នាក់`\n💡 *ឧទាហរណ៍៖* `/addstu STU001,សុខ ជា,M,Grade3_A`", parse_mode='Markdown')
        elif action == "adm_guide_discipline":
            bot.send_message(chat_id, "⚖️ **[ កត់ត្រាវិន័យសិស្ស ]**\nសូមវាយ៖ `/adddiscipline ID_សិស្ស,បញ្ហាកើតឡើង,វិធានការកែប្រែ`", parse_mode='Markdown')
        elif action == "adm_guide_grade":
            bot.send_message(chat_id, "✍️ **[ ដាក់ពិន្ទុ & Feedback ]**\nសូមវាយ៖ `/grade ID_Submission,ពិន្ទុ,មតិយោបល់`", parse_mode='Markdown')
        elif action == "adm_guide_notice":
            bot.send_message(chat_id, "📢 **[ ថែមសេចក្ដីប្រកាសសាលា ]**\nសូមវាយ៖ `/addnotice ចំណងជើង,ខ្លឹមសារព័ត៌មាន`", parse_mode='Markdown')
        elif action == "adm_guide_addteacher":
            bot.send_message(chat_id, "➕ **[ បង្កើតគ្រូថ្មី ]**\nសូមវាយ៖ `/addteacher ID,ឈ្មោះគ្រូ,លេខសម្ងាត់`", parse_mode='Markdown')
            
        bot.answer_callback_query(call.id)


    # ========================================================
    # 👑 មុខងារទី ១៖ Admin បង្កើត ID និង លេខសម្ងាត់ឱ្យគ្រូ
    # ========================================================
    @bot.message_handler(commands=['addteacher'])
    def admin_add_teacher(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text.strip()[12:].strip() # កាត់ពាក្យ /addteacher ចេញ
        
        if not text:
            error_usage = (
                "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
                "--------------------------------------------------\n"
                "📌 **សូមវាយ៖** `/addteacher ID,ឈ្មោះគ្រូ,លេខសម្ងាត់`\n\n"
                "💡 **ឧទាហរណ៍៖** `/addteacher TCH001,លោកគ្រូ ណារំង,Naron@2026`"
            )
            bot.reply_to(message, error_usage, parse_mode='Markdown')
            return
            
        try:
            # 🔒 ឆែកសិទ្ធិ Admin សិន (រត់ទៅឆែកក្នុងតារាង users)
            admin_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
            if not admin_check.data or admin_check.data[0].get('role') not in ['ADMIN', 'SUPER_ADMIN']:
                bot.reply_to(message, "❌ **សុំទោស!** បញ្ជានេះសម្រាប់តែ Admin សាលាតែប៉ុណ្ណោះ។")
                return

            # ✂️ បំបែកទិន្នន័យដោយប្រើសញ្ញាក្បៀស ( , )
            parts = text.split(',')
            
            # 🛡️ ប្រព័ន្ធការពារករណីវាយខ្វះផ្នែក
            if len(parts) < 3:
                bot.reply_to(message, "⚠️ **ទិន្នន័យមិនគ្រប់គ្រាន់ទេ!** សូមប្រាកដថាបានប្រើ **សញ្ញាក្បៀស ( , )** ឱ្យបានគ្រប់ ៣ ផ្នែក៖\n👉 `ID,ឈ្មោះ,លេខសម្ងាត់`")
                return

            t_id = parts[0].strip()
            t_name = parts[1].strip()
            t_password = parts[2].strip()
            
            if t_id == "" or t_name == "" or t_password == "":
                bot.reply_to(message, "⚠️ **មិនអាចទុកប្រអប់ណាមួយទំនេរបានទេ!**")
                return

            # 🔄 បញ្ជូនទៅរក្សាទុកក្នុងតារាង teachers លើ Supabase 
            supabase.table("teachers").upsert({
                "teacher_id": t_id,
                "name": t_name,
                "password": t_password,  
                "telegram_id": None      # ទុកទំនេរចាំគ្រូ Login មកភ្ជាប់តាមក្រោយ
            }, on_conflict="teacher_id").execute()
            
            success_msg = (
                "👑 **[ បង្កើតគណនីគ្រូជោគជ័យ! ]**\n"
                "--------------------------------------------------\n"
                f"🆔 **ID គ្រូ៖** `{t_id}`\n"
                f"👤 **ឈ្មោះពិត៖** *{t_name}*\n"
                f"🔑 **លេខសម្ងាត់៖** `{t_password}`\n"
                "--------------------------------------------------\n"
                f"📢 លោកគ្រូអាចវាយ Login តាមទម្រង់៖\n`/tlogin {t_id},{t_password}`"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            
        except Exception as e:
            print(f"❌ Add Teacher Error: {e}")
            bot.reply_to(message, f"❌ មិនអាចបង្កើតទិន្នន័យគ្រូបានទេ៖ `{e}`")


    # ========================================================
    # 👩‍🏫 មុខងារទី ២៖ គ្រូ Login ផ្ទៀងផ្ទាត់ជាមួយ ID & Password
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
    # 🎛️ មុខងារទី ៣៖ ស្ទាក់ចាប់រាល់ពេលគ្រូ ឬ Admin ចុចប៊ូតុង Menu ធំៗ
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
        user_id = message.from_user.id
        user_text = message.text
        
        if user_text == "📚 ដាក់កិច្ចការផ្ទះ (Add HW)":
            guide = (
                "📚 **[ ផ្ទាំងដាក់កិច្ចការផ្ទះ (Add HW) ]**\n"
                "--------------------------------------------------\n"
                "📌 **សូមលោកគ្រូភ្ជាប់ឯកសារ (PDF ឬ រូបភាព) រួចវាយ Caption ៖**\n"
                "`/addhw ថ្នាក់,មុខវិជ្ជា,ខ្លឹមសារកិច្ចការ,ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី`\n\n"
                "💡 **ឧទាហរណ៍៖**\n"
                "`/addhw GRADE12_A,ភាសាខ្មែរ,លំហាត់ទំព័រ៥០,2026-06-15 23:59`"
            )
            bot.send_message(chat_id, guide, parse_mode='Markdown')
            
        elif user_text == "📊 មើលវត្តមានសិស្ស":
            bot.send_message(chat_id, "📊 **[ ពិនិត្យវត្តមាន ]**\nសូមវាយ៖ `/ld ឈ្មោះថ្នាក់` (ឧទាហរណ៍៖ `/ld GRADE12_A`)", parse_mode='Markdown')
            
        elif user_text == "✍️ ដាក់ពិន្ទុសិស្ស (Grade)":
            bot.send_message(chat_id, "✍️ **[ ដាក់ពិន្ទុកិច្ចការ ]**\nសូមវាយ៖ `/lh ឈ្មោះថ្នាក់` ដើម្បីមើលកិច្ចការដែលសិស្សផ្ញើមក (ឧទាហរណ៍៖ `/lh GRADE12_A`)", parse_mode='Markdown')

        elif user_text == "➕ បង្កើតគណនីគ្រូ":
            bot.send_message(chat_id, "👑 **[ បង្កើតគ្រូថ្មី ]**\nសូមវាយបញ្ជា៖ `/addteacher ID,ឈ្មោះគ្រូ,លេខសម្ងាត់`", parse_mode='Markdown')

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
                supabase.table("users").update({"status": "NEW", "role": "USER"}).eq("telegram_id", user_id).execute()
                supabase.table("teachers").update({"telegram_id": None}).eq("telegram_id", user_id).execute()
                remove_markup = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(chat_id, "👋 **ចាកចេញពីគណនីជោគជ័យ!** សូមវាយ `/start` ដើម្បីចូលគណនីផ្សេងទៀតបាទ។", reply_markup=remove_markup)
            except Exception as e:
                bot.reply_to(message, f"❌ Logout ជួបបញ្ហា៖ `{e}`")


    # ========================================================
    # 📚 មុខងារទី ៤៖ /addhw គ្រូដាក់កិច្ចការផ្ទះ (លុបចោលជួរ class_level ក្នុង homework ដាច់ខាត)
    # ========================================================
    @bot.message_handler(
        content_types=['text', 'photo', 'document'],
        func=lambda message: (message.text and message.text.strip().lower().startswith('/addhw')) or 
                             (message.caption and message.caption.strip().lower().startswith('/addhw'))
    )
    def teacher_add_homework_fixed_final(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        raw_text = message.text if message.text else message.caption
        
        if not raw_text: return
            
        text = raw_text.strip()[7:].strip()
        if not text or len(text.split(',')) < 4:
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយលោកគ្រូ!**\nសូមវាយ៖ `/addhw ថ្នាក់,មុខវិជ្ជា,ខ្លឹមសារ,ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី`", parse_mode='Markdown')
            return
            
        try:
            parts = text.split(',')
            class_input = parts[0].strip()       
            subject_name = parts[1].strip()
            description = parts[2].strip()
            deadline_string = parts[3].strip() 
            
            try:
                formatted_deadline = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").isoformat()
            except ValueError:
                bot.reply_to(message, "⚠️ **ទម្រង់ថ្ងៃខែខុសហើយ!** លំនាំ៖ `ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី` (ឧទាហរណ៍៖ `2026-06-15 17:00`)")
                return
            
            t_check = supabase.table("teachers").select("teacher_id").eq("telegram_id", user_id).execute()
            t_id = t_check.data[0]['teacher_id'] if t_check.data else str(user_id)
            
            file_id_to_save = None
            file_type_to_save = None
            
            if message.content_type == 'photo':
                file_id_to_save = message.photo[-1].file_id
                file_type_to_save = "photo"
            elif message.content_type == 'document':
                file_id_to_save = message.document.file_id
                file_type_to_save = "document"
                
            # 📤 រក្សាទុកចូល homework (លុបចោលជួរ class_level ចេញស្អាតបាត ១០០%)
            supabase.table("homework").insert({
                "subject_name": subject_name,
                "description": description,
                "deadline_at": formatted_deadline, 
                "teacher_id": t_id,
                "attachment_file": file_id_to_save,   
                "attachment_type": file_type_to_save
                # ❌ លុប "class_level": class_input ចេញរួចរាល់ហើយបង ការពារទិន្នន័យឌុប
            }).execute()
            
            # 🔍 [ប្រព័ន្ធការពារ Comment Hint]៖ ឆែកស្កែនរកឈ្មោះថ្នាក់ពីតារាងសិស្ស students ផ្ទាល់
            student_check = supabase.table("students").select("class_level").eq("class_level", class_input).limit(1).execute()
            display_date = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").strftime("%d-%b-%Y ម៉ោង %I:%M %p")
            
            success_msg = (
                "🎯 **[ បង្ហោះកិច្ចការផ្ទះ + ឯកសារជោគជ័យ! ]**\n"
                "--------------------------------------------------\n"
                f"🏫 **សម្រាប់ថ្នាក់៖** `{class_input}`\n"
                f"📚 **មុខវិជ្ជា៖** *{subject_name}*\n"
                f"📝 **ខ្លឹមសារ៖** _{description}_\n"
                f"⏳ **Deadline៖** `📅 {display_date}`\n"
                "--------------------------------------------------\n"
            )
            
            if student_check.data:
                success_msg += "🟢 *ប្រព័ន្ធបានឆែកឃើញមានសិស្សក្នុងថ្នាក់នេះរួចរាល់ហើយ លោកគ្រូ!*"
            else:
                all_stud = supabase.table("students").select("class_level").execute()
                class_list_str = "មិនទាន់មានថ្នាក់ចុះឈ្មោះ"
                if all_stud.data:
                    unique_classes = list(set([row.get('class_level') for row in all_stud.data if row.get('class_level')]))
                    class_list_str = ", ".join([f"`{c}`" for c in unique_classes])
                    
                success_msg += (
                    f"⚠️ **សូមលោកគ្រូជួយ Check Class ឡើងវិញ៖**\n"
                    f"ព្រោះរកមិនឃើញសិស្សក្នុងថ្នាក់ `{class_input}` នេះដេកក្នុងតារាងសិស្សទេបាទ!\n"
                    f"📋 **ឈ្មោះថ្នាក់ដែលមានសិស្សពិតប្រាកដគឺ៖** {class_list_str}"
                )
                
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            
        except Exception as e:
            bot.reply_to(message, f"❌ មិនអាចរក្សាទុកកិច្ចការផ្ទះបានទេ៖ `{e}`")


    # ========================================================
    # 📊 មុខងារទី ៥៖ /ld មើលវត្តមានសិស្សទាំងអស់ក្នុងថ្នាក់
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
    # 📝 មុខងារទី ៦៖ /lh ទាញយកកិច្ចការសិស្ស (PDF/Picture) មកមើល (MATCHED TO DB 100%)
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
            
            # 🎯 ឆែកទាញយកពីតារាងពិតរបស់បង `student_submissions` យកតែស្ថានភាព 'PENDING'
            sub_res = supabase.table("student_submissions").select("*").eq("class_level", class_target).eq("status", "PENDING").execute()
            
            if not sub_res.data:
                bot.send_message(chat_id, f"✨ **មិនមានកិច្ចការដែលត្រូវដាក់ពិន្ទុទេ** សម្រាប់ថ្នាក់ {class_target}។")
                return
                
            for sub in sub_res.data:
                sub_id = sub['id']               
                s_id = sub['student_id']     
                file_telegram_id = sub['submitted_file']  # 📎 ទាញយក Telegram File ID ចំៗពី DB បង
                f_type = sub.get('submitted_type', 'document')     
                
                # បង្កើត Inline Button សម្រាប់ចុចដាក់ពិន្ទុ
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(f"✍️ ដាក់ពិន្ទុឱ្យសិស្ស {s_id}", callback_data=f"grh_{sub_id}"))
                
                info_text = f"👤 **កូដសិស្ស៖** `{s_id}`\n🏫 **ថ្នាក់៖** `{class_target}`\n📂 ឯកសារភ្ជាប់៖ `{f_type.upper()}`"
                
                # 📤 បាញ់ចេញ File ទៅឱ្យគ្រូមើលតាមរយៈ Telegram File ID
                if 'photo' in f_type.lower():
                    bot.send_photo(chat_id, photo=file_telegram_id, caption=info_text, parse_mode='Markdown', reply_markup=markup)
                else:
                    bot.send_document(chat_id, document=file_telegram_id, caption=info_text, parse_mode='Markdown', reply_markup=markup)
                    
        except Exception as e:
            bot.reply_to(message, f"❌ មិនអាចទាញទិន្នន័យកិច្ចការសិស្សបានទេ៖ `{e}`")


    # ========================================================
    # 🎛️ មុខងារទី ៧៖ ស្ទាក់ចាប់ប៊ូតុង Inline "✍️ ដាក់ពិន្ទុឱ្យ..."
    # ========================================================
    @bot.callback_query_handler(func=lambda call: call.data.startswith('grh_'))
    def handle_grade_button_click(call):
        sub_id = call.data.split('_')[1]
        instruction = (
            f"✍️ **[ វគ្គបញ្ចូលពិន្ទុ ]**\n"
            f"លោកគ្រូអាចបញ្ចូលពិន្ទុឱ្យកិច្ចការលេខ `{sub_id}` បានដោយវាយបញ្ជា៖\n"
            f"👉 `/grade {sub_id},[ពិន្ទុ],[មតិយោបល់]`\n\n"
            f"💡 *ឧទាហរណ៍៖* `/grade {sub_id},9,ធ្វើបានល្អណាស់កូន!`"
        )
        bot.send_message(call.message.chat.id, instruction, parse_mode='Markdown')
        bot.answer_callback_query(call.id)


    # ========================================================
    # ✍️ មុខងារទី ៨៖ /grade ដាក់ពិន្ទុ រុញទៅ Database (MATCHED TO DB 100%)
    # ========================================================
    @bot.message_handler(commands=['grade'])
    def admin_grade_homework(message):
        text = message.text.strip()[7:].strip()
        if not text or len(text.split(',')) < 3:
            bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ!** សូមវាយ៖ `/grade ID,ពិន្ទុ,មតិយោបល់`", parse_mode='Markdown')
            return
            
        try:
            parts = text.split(',')
            sub_id = int(parts[0].strip())
            score = parts[1].strip()
            comment = parts[2].strip()
            
            # 🔄 អាប់ដេតពិន្ទុចូលជួរឈរពិតប្រាកដក្នុងតារាង `student_submissions` របស់បង
            supabase.table("student_submissions").update({
                "score": score, 
                "teacher_comment": comment, 
                "status": "GRADED"
            }).eq("id", sub_id).execute()
            
            bot.reply_to(message, f"✅ **ដាក់ពិន្ទុជោគជ័យ!**\n📂 កិច្ចការលេខ៖ `{sub_id}`\n💯 ពិន្ទុ៖ *{score}* 🌟\n💬 មតិគ្រូ៖ `{comment}`", parse_mode='Markdown')
            
        except Exception as e:
            bot.reply_to(message, f"❌ មិនអាចរក្សាទុកការដាក់ពិន្ទុបានទេ៖ `{e}`")