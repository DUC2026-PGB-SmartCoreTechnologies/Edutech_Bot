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
                if user_id != existing_admin_id:
                    bot.reply_to(message, "❌ **សុំទោស!** ប្រព័ន្ធគ្រប់គ្រងសាលា DUC មាន Admin មេរួចរាល់ហើយ។ លោកអ្នកមិនអាច Login ចូលបានឡើយ។")
                    print(f"⚠️ [SECURITY BLOCK] ID {user_id} ព្យាយាមលួច Login ត្រួតលើ Admin ចាស់ ID {existing_admin_id}!")
                    return
            
        except Exception as e:
            print(f"❌ Supabase Admin Lock Check Error: {e}")
            bot.reply_to(message, "❌ មានបញ្ហាបច្ចេកទេសក្នុងការឆែកមើលសិទ្ធិ។")
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
            # 🟢 ថែមជួរឈរគន្លឹះនេះចូល ដើម្បីឱ្យវាលោតប៊ូតុងលើអេក្រង់ទូរស័ព្ទរបស់ Admin
        
            
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
        elif action == "adm_guide_checkreq":
            bot.send_message(chat_id, "🔍 **[ មើលបញ្ជីសិស្សចុះឈ្មោះថ្មី ]**\nសូមវាយបញ្ជាខ្លី៖ `/checkreq` ដើម្បីទាញយកបញ្ជីសិស្ស PENDING ទាំងអស់", parse_mode='Markdown')
        elif action == "adm_guide_approve":
            bot.send_message(chat_id, "🟢 **[ របៀបអនុម័ត / Approve សិស្ស ]**\nសូមវាយបញ្ជា៖ `/approve ID_Telegram`\n💡 *ឧទាហរណ៍៖* `/approve 548962145`", parse_mode='Markdown')
            
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
                f"📢 លោកគ្រូអាវាយ Login តាមទម្រង់៖\n`/tlogin {t_id},{t_password}`"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            
        except Exception as e:
            print(f"❌ Add Teacher Error: {e}")
            bot.reply_to(message, f"❌ មិនអាចបង្កើតទិន្នន័យគ្រូបានទេ៖ `{e}`")


    # ========================================================
    # 👩‍🏫 មុខងារទី ២៖ គ្រូ Login ផ្ទៀងផ្ទាត់ជាមួយ ID & Password
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
    # # 📚 មុខងារទី ៤៖ /addhw គ្រូដាក់កិច្ចការផ្ទះ (លុបចោលជួរ class_level ក្នុង homework ដាច់ខាត)
    # # ========================================================
    # @bot.message_handler(
    #     content_types=['text', 'photo', 'document'],
    #     func=lambda message: (message.text and message.text.strip().lower().startswith('/addhw')) or 
    #                          (message.caption and message.caption.strip().lower().startswith('/addhw'))
    # )
    # def teacher_add_homework_fixed_final(message):
    #     chat_id = message.chat.id
    #     user_id = message.from_user.id
    #     raw_text = message.text if message.text else message.caption
        
    #     if not raw_text: return
            
    #     text = raw_text.strip()[7:].strip()
    #     if not text or len(text.split(',')) < 4:
    #         bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយលោកគ្រូ!**\nសូមវាយ៖ `/addhw ថ្នាក់,មុខវិជ្ជា,ខ្លឹមសារ,ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី`", parse_mode='Markdown')
    #         return
            
    #     try:
    #         parts = text.split(',')
    #         class_input = parts[0].strip()       
    #         subject_name = parts[1].strip()
    #         description = parts[2].strip()
    #         deadline_string = parts[3].strip() 
            
    #         try:
    #             formatted_deadline = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").isoformat()
    #         except ValueError:
    #             bot.reply_to(message, "⚠️ **ទម្រង់ថ្ងៃខែខុសហើយ!** លំនាំ៖ `ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី` (ឧទាហរណ៍៖ `2026-06-15 17:00`)")
    #             return
            
    #         t_check = supabase.table("teachers").select("teacher_id").eq("telegram_id", user_id).execute()
    #         t_id = t_check.data[0]['teacher_id'] if t_check.data else str(user_id)
            
    #         file_id_to_save = None
    #         file_type_to_save = None
            
    #         if message.content_type == 'photo':
    #             file_id_to_save = message.photo[-1].file_id
    #             file_type_to_save = "photo"
    #         elif message.content_type == 'document':
    #             file_id_to_save = message.document.file_id
    #             file_type_to_save = "document"
                
    #         # 📤 រក្សាទុកចូល homework (លុបចោលជួរ class_level ចេញស្អាតបាត ១០០%)
    #         supabase.table("homework").insert({
    #             "class_level": class_input,
    #             "subject_name": subject_name,
    #             "description": description,
    #             "deadline_at": formatted_deadline, 
    #             "teacher_id": t_id,
    #             "attachment_file": file_id_to_save,   
    #             "attachment_type": file_type_to_save
    #             # ❌ លុប "class_level": class_input ចេញរួចរាល់ហើយបង ការពារទិន្នន័យឌុប
    #         }).execute()
            
    #         # 🔍 [ប្រព័ន្ធការពារ Comment Hint]៖ ឆែកស្កែនរកឈ្មោះថ្នាក់ពីតារាងសិស្ស students ផ្ទាល់
    #         student_check = supabase.table("students").select("class_level").eq("class_level", class_input).limit(1).execute()
    #         display_date = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").strftime("%d-%b-%Y ម៉ោង %I:%M %p")
            
    #         success_msg = (
    #             "🎯 **[ បង្ហោះកិច្ចការផ្ទះ + ឯកសារជោគជ័យ! ]**\n"
    #             "--------------------------------------------------\n"
    #             f"🏫 **សម្រាប់ថ្នាក់៖** `{class_input}`\n"
    #             f"📚 **មុខវិជ្ជា៖** *{subject_name}*\n"
    #             f"📝 **ខ្លឹមសារ៖** _{description}_\n"
    #             f"⏳ **Deadline៖** `📅 {display_date}`\n"
    #             "--------------------------------------------------\n"
    #         )
            
    #         if student_check.data:
    #             success_msg += "🟢 *ប្រព័ន្ធបានឆែកឃើញមានសិស្សក្នុងថ្នាក់នេះរួចរាល់ហើយ លោកគ្រូ!*"
    #         else:
    #             all_stud = supabase.table("students").select("class_level").execute()
    #             class_list_str = "មិនទាន់មានថ្នាក់ចុះឈ្មោះ"
    #             if all_stud.data:
    #                 unique_classes = list(set([row.get('class_level') for row in all_stud.data if row.get('class_level')]))
    #                 class_list_str = ", ".join([f"`{c}`" for c in unique_classes])
                    
    #             success_msg += (
    #                 f"⚠️ **សូមលោកគ្រូជួយ Check Class ឡើងវិញ៖**\n"
    #                 f"ព្រោះរកមិនឃើញសិស្សក្នុងថ្នាក់ `{class_input}` នេះដេកក្នុងតារាងសិស្សទេបាទ!\n"
    #                 f"📋 **ឈ្មោះថ្នាក់ដែលមានសិស្សពិតប្រាកដគឺ៖** {class_list_str}"
    #             )
                
    #         bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            
    #     except Exception as e:
    #         bot.reply_to(message, f"❌ មិនអាចរក្សាទុកកិច្ចការផ្ទះបានទេ៖ `{e}`")
    #         return



# ========================================================
    # 📚 មុខងារ៖ /addhw គ្រូដាក់កិច្ចការផ្ទះ (កំណែត្រឹមត្រូវ)
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
            
            # ១. ពិនិត្យសុពលភាពថ្ងៃខែ
            try:
                formatted_deadline = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").isoformat()
            except ValueError:
                bot.reply_to(message, "⚠️ **ទម្រង់ថ្ងៃខែខុសហើយ!** លំនាំ៖ `ឆ្នាំ-ខែ-ថ្ងៃ ម៉ោង:នាទី` (ឧទាហរណ៍៖ `2026-06-15 17:00`)")
                return
            
            # ២. ពិនិត្យរកថ្នាក់ក្នុងតារាងសិស្ស (CHECK FIRST)
            student_check = supabase.table("students").select("class_level").eq("class_level", class_input).limit(1).execute()
            
            if not student_check.data:
                # ទាញឈ្មោះថ្នាក់ដែលមានក្នុងប្រព័ន្ធមកបង្ហាញគ្រូ
                all_stud = supabase.table("students").select("class_level").execute()
                class_list_str = "មិនទាន់មានថ្នាក់ចុះឈ្មោះ"
                if all_stud.data:
                    unique_classes = list(set([row.get('class_level') for row in all_stud.data if row.get('class_level')]))
                    class_list_str = ", ".join([f"`{c}`" for c in unique_classes])
                
                bot.reply_to(message, (
                    f"⚠️ **សូមលោកគ្រូជួយ Check Class ឡើងវិញ៖**\n"
                    f"រកមិនឃើញសិស្សក្នុងថ្នាក់ `{class_input}` នេះក្នុងតារាងសិស្សទេបាទ!\n"
                    f"📋 **ឈ្មោះថ្នាក់ដែលមានសិស្សពិតប្រាកដគឺ៖** {class_list_str}"
                ), parse_mode='Markdown')
                return # ❌ បញ្ឈប់កូដនៅត្រង់នេះ មិនឱ្យ Insert ចូល Database

            # ៣. បើឆ្លងផុតការ Check ទើប Insert ចូល Database
            t_check = supabase.table("teachers").select("teacher_id").eq("telegram_id", user_id).execute()
            t_id = t_check.data[0]['teacher_id'] if t_check.data else str(user_id)
            
            file_id_to_save = message.photo[-1].file_id if message.content_type == 'photo' else (message.document.file_id if message.content_type == 'document' else None)
            file_type_to_save = message.content_type if message.content_type in ['photo', 'document'] else None
                
            supabase.table("homework").insert({
                "class_level": class_input,
                "subject_name": subject_name,
                "description": description,
                "deadline_at": formatted_deadline, 
                "teacher_id": t_id,
                "attachment_file": file_id_to_save,   
                "attachment_type": file_type_to_save
            }).execute()
            
            # ៤. ជូនដំណឹងជោគជ័យ
            display_date = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M").strftime("%d-%b-%Y ម៉ោង %I:%M %p")
            success_msg = (
                "🎯 **[ បង្ហោះកិច្ចការផ្ទះ + ឯកសារជោគជ័យ! ]**\n"
                "--------------------------------------------------\n"
                f"🏫 **សម្រាប់ថ្នាក់៖** `{class_input}`\n"
                f"📚 **មុខវិជ្ជា៖** *{subject_name}*\n"
                f"📝 **ខ្លឹមសារ៖** _{description}_\n"
                f"⏳ **Deadline៖** `📅 {display_date}`\n"
                "🟢 *ប្រព័ន្ធបានឆែកឃើញមានសិស្សក្នុងថ្នាក់នេះរួចរាល់ហើយ លោកគ្រូ!*"
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
    @bot.message_handler(commands=['checkreq'])
    def check_requests_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.send_message(chat_id, "❌ **សកម្មភាពត្រូវបានបដិសេធ!**")
                return

            bot.send_message(chat_id, "🔍 **កំពុងស្វែងរកសិស្សដែលទាមទារការអនុម័ត (Pending)...**")

            # ២. ទាញយកតែសិស្សណាដែល student_id មានពាក្យ "PENDING"
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
                # បង្ហាញបញ្ជា Admin ឱ្យងាយស្រួលចុច (គ្រាន់តែចុចលើលេខ ID សិស្ស)
                response_msg += f"👉 **អនុម័ត៖** `/approve {parent_tg}, DUC{index:03d}`\n"
                response_msg += "--------------------------------------------------\n\n"
            
            bot.send_message(chat_id, response_msg, parse_mode='Markdown')

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: `{e}`")
        # ========================================================
    # # 🟢 មុខងារ៖ Admin វាយ /approve ដើម្បីបើកសិទ្ធិឱ្យសិស្ស និងបាញ់សារទៅសិស្សផ្ទាល់
    # # ========================================================
    # @bot.message_handler(commands=['approve'])
    # def approve_user_command(message):
    #     chat_id = message.chat.id
    #     user_id = message.from_user.id
        
    #     try:
    #         # 🔒 ជាន់ទី ១៖ ឆែកសិទ្ធិ Admin ក្នុងតារាង users
    #         user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
    #         if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
    #             bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
    #             return

    #         # 🔄 ជំហានទី ២៖ កាត់យកអក្សរខាងក្រោយពាក្យ /approve រួចបំបែកដោយសញ្ញាក្បៀស (,)
    #         input_text = message.text.strip()[8:].strip()
            
    #         if not input_text or "," not in input_text:
    #             bot.reply_to(
    #                 message, 
    #                 "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
    #                 "សូមវាយ៖ `/approve លេខTelegramID, លេខIDសិស្ស`\n"
    #                 "💡 *ឧទាហរណ៍៖* `/approve 548962145, DUC001`", 
    #                 parse_mode='Markdown'
    #             )
    #             return

    #         parts = input_text.split(",")
    #         target_tg_id = parts[0].strip()
    #         new_student_id = parts[1].strip().upper() # លេខ ID ដែល Admin ដាក់ឱ្យ

    #         bot.send_message(chat_id, f"⏳ **កំពុងអនុម័តគណនី Telegram ID: `{target_tg_id}`...**")

    #         # 🔍 ៣. រត់ទៅឆែកមើលគណនីរបស់គាត់ក្នុងតារាង users ជាមុនសិន
    #         target_user = supabase.table("users").select("*").eq("telegram_id", target_tg_id).execute()
            
    #         if not target_user.data:
    #             bot.reply_to(message, f"❌ រកមិនឃើញគណនី Telegram ID: `{target_tg_id}` នេះនៅក្នុងតារាង users ឡើយបាទ។")
    #             return
                
    #         # 🔄 ៤. អាប់ដេតស្ថានភាពក្នុងតារាង "users" ឱ្យទៅជា APPROVED ដើម្បីឱ្យគាត់ចូល Menu បាន
    #         supabase.table("users").update({
    #             "status": "APPROVED"
    #         }).eq("telegram_id", target_tg_id).execute()

    #         # 🎯 ៥. ទៅអាប់ដេតលេខ student_id ជូនគាត់នៅក្នុងតារាង "students" ឱ្យត្រូវគ្នាតាមដាតាបេស
    #         try:
    #             supabase.table("students").update({
    #                 "student_id": new_student_id
    #             }).eq("parent_telegram_id", target_tg_id).execute()
    #             db_student_status = "✅ (បានរក្សាទុក ID ចូលតារាង students រួចរាល់)"
    #         except Exception as e_db:
    #             print(f"⚠️ Students table update student_id failed: {e_db}")
    #             db_student_status = f"⚠️ (មិនអាចកែក្នុងតារាង students ទេ៖ {e_db})"

    #         # 🔔 ៦. ដំណើរការបាញ់សារផ្ដាច់មុខទៅប្រាប់សិស្ស/អាណាព្យាបាលម្នាក់នោះផ្ទាល់ខ្លួន (Direct Message)
    #         student_notified = "❌ (សិស្សចុច Block Bot ឬលុបឆាតចោល មិនអាចផ្ញើសារបានទេ)"
    #         try:
    #             alert_student = (
    #                 "🎉 **សូមអបអរសាទរ! គណនីរបស់អ្នកត្រូវបានអនុម័តហើយ**\n"
    #                 "--------------------------------------------------\n"
    #                 f"👑 **លោកអ្នកទទួលបានលេខកូដសិស្សជាផ្លូវការ៖** `{new_student_id}`\n"
    #                 "--------------------------------------------------\n"
    #                 "🤖 ឥឡូវនេះ លោកអ្នកអាចវាយបញ្ជា `/start` សារជាថ្មី ដើម្បីចូលប្រើប្រាស់មឺនុយសាលាអនឡាញ DUC បានហើយបាទ! សូមអរគុណ។"
    #             )
    #             bot.send_message(target_tg_id, alert_student, parse_mode='Markdown')
    #             student_notified = "✅ (បានផ្ញើសារជូនដំណឹងទៅសិស្សផ្ទាល់រួចរាល់)"
    #         except Exception as e_msg:
    #             print(f"⚠️ Cannot send message to student ID {target_tg_id}: {e_msg}")

    #         # 📢 ៧. ផ្ញើសារលទ្ធផលរួមមកប្រាប់ Admin វិញ
    #         bot.send_message(
    #             chat_id, 
    #             f"🟢 **អនុម័តគណនីជោគជ័យ!**\n\n"
    #             f"🆔 **Telegram ID៖** `{target_tg_id}`\n"
    #             f"👑 **ID សាលា៖** `{new_student_id}`\n"
    #             f"📱 **ស្ថានភាព Users៖** `APPROVED` (ចូលប្រព័ន្ធបានហើយ)\n"
    #             f"🗂️ **ស្ថានភាព Students៖** {db_student_status}\n"
    #             f"🔔 **ការជូនដំណឹងសិស្ស៖** {student_notified}",
    #             parse_mode='Markdown'
    #         )

    #     except Exception as e:
    #         print(f"❌ Full Approve Error: {e}")
    #         # 💡 ជួរដេកគន្លឹះ៖ ទោះបីជាកូដគាំង Error អ្វីក៏ដោយ គឺត្រូវតែបាញ់សារមកប្រាប់ Admin ភ្លាម លែងឱ្យស្ងាត់ទៀតហើយ
    #         bot.send_message(chat_id, f"❌ **Bot គាំងមិនអាចអនុម័តបានទេ ដោយសារ Error៖** `{e}`", parse_mode='Markdown')
            


                    # 🟢 មុខងារ៖ Admin វាយ /approve ដើម្បីបើកសិទ្ធិឱ្យសិស្ស និងបាញ់សារទៅសិស្សផ្ទាល់
    # ========================================================
    @bot.message_handler(commands=['approve'])
    def approve_user_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            # ២. កាត់យកអក្សរខាងក្រោយពាក្យ /approve
            input_text = message.text.strip()[8:].strip()
            if not input_text or "," not in input_text:
                bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ Admin!**\nសូមវាយ៖ `/approve លេខTelegramID, លេខIDសិស្ស`", parse_mode='Markdown')
                return

            parts = input_text.split(",")
            target_tg_id = parts[0].strip()
            new_student_id = parts[1].strip().upper() 

            bot.send_message(chat_id, f"⏳ **កំពុងអនុម័តគណនី Telegram ID: `{target_tg_id}`...**")

            # ៣. ឆែកមើលគណនីក្នុងតារាង users
            target_user = supabase.table("users").select("*").eq("telegram_id", target_tg_id).execute()
            if not target_user.data:
                bot.reply_to(message, f"❌ រកមិនឃើញគណនី Telegram ID: `{target_tg_id}` នេះក្នុងតារាង users ទេ។")
                return
                
            # ៤. អាប់ដេតតារាង "users" (ប្តូរ status និងដាក់ student_id ពិតប្រាកដ)
            supabase.table("users").update({
                "status": "APPROVED",
                "student_id": new_student_id
            }).eq("telegram_id", target_tg_id).execute()

            # ៥. អាប់ដេតតារាង "students" (ប្តូរលេខ ID ពី PENDING_... ទៅជាលេខកូដសិស្សពិតប្រាកដ)
            # ប្រើ parent_telegram_id ដើម្បីស្វែងរកសិស្ស
            update_stu = supabase.table("students").update({
                "student_id": new_student_id
            }).eq("parent_telegram_id", target_tg_id).execute()
            
            db_student_status = "✅ (បានអាប់ដេតលេខកូដសិស្សចូលតារាង students រួចរាល់)"

            # ៦. បាញ់សារជូនដំណឹងទៅសិស្ស
            try:
                alert_student = (
                    "🎉 **សូមអបអរសាទរ! គណនីរបស់អ្នកត្រូវបានអនុម័តហើយ**\n"
                    "--------------------------------------------------\n"
                    f"👑 **លេខកូដសិស្ស៖** `{new_student_id}`\n"
                    "🤖 ឥឡូវនេះ លោកអ្នកអាចប្រើប្រាស់មឺនុយសាលាអនឡាញ DUC បានហើយ!"
                )
                bot.send_message(target_tg_id, alert_student, parse_mode='Markdown')
                student_notified = "✅ (បានផ្ញើសារជូនដំណឹងទៅសិស្សរួចរាល់)"
            except Exception as e_msg:
                student_notified = "❌ (មិនអាចផ្ញើសារទៅសិស្សបាន)"

            # ៧. ផ្ញើសារលទ្ធផលប្រាប់ Admin
            bot.send_message(chat_id, f"🟢 **អនុម័តជោគជ័យ!**\n\n🆔 **Telegram ID៖** `{target_tg_id}`\n👑 **ID សាលា៖** `{new_student_id}`\n📱 **Status:** `APPROVED`\n🗂️ {db_student_status}\n🔔 {student_notified}", parse_mode='Markdown')

        except Exception as e:
            bot.send_message(chat_id, f"❌ **Bot Error:** `{e}`", parse_mode='Markdown')
            # ========================================================
    # 📅 មុខងារ៖ Admin វាយ /addschedule ដើម្បីបន្ថែមតារាងរៀន
    # ========================================================
    @bot.message_handler(commands=['addschedule'])
    def add_schedule_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔒 ១. ឆែកសិទ្ធិ Admin ក្នុងតារាង users
            user_check = supabase.table("users").select("role").eq("telegram_id", user_id).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            # 🔄 ២. កាត់យកអក្សរខាងក្រោយពាក្យ /addschedule
            input_text = message.text.strip()[12:].strip()
            
            # ឆែកទម្រង់វាយបញ្ចូល (ត្រូវមានសញ្ញាក្បៀស ៥ ដើម្បីបំបែកជា ៦ ផ្នែក)
            if not input_text or input_text.count(",") < 5:
                guide_msg = (
                    "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
                    "សូមវាយ៖ `/addschedule ថ្នាក់, មុខវិជ្ជា, IDគ្រូ, ថ្ងៃរៀន, ម៉ោងដើម, ម៉ោងចប់`\n\n"
                    "💡 *ឧទាហរណ៍៖* `/addschedule GRADE12_A, គណិតវិទ្យា, T001, Monday, 08:00, 09:30`\n"
                    "*(បញ្ជាក់៖ ប្រសិនបើគ្មាន IDគ្រូ ទេ សូមវាយពាក្យ NULL)*"
                )
                bot.reply_to(message, guide_msg, parse_mode='Markdown')
                return

            # 🔄 ៣. បំបែកទិន្នន័យ
            parts = input_text.split(",")
            class_lvl   = parts[0].strip().upper()
            subject     = parts[1].strip()
            teacher_id  = parts[2].strip()
            study_day   = parts[3].strip()
            start_time  = parts[4].strip()
            end_time    = parts[5].strip()

            # បើ Admin វាយ NULL ឱ្យដូរទៅជាតម្លៃ None (NULL ក្នុង Database)
            if teacher_id.upper() == "NULL" or teacher_id == "":
                teacher_id = None

            bot.send_message(chat_id, f"⏳ **កំពុងរក្សាទុកកាលវិភាគថ្នាក់ `{class_lvl}` ចូលដាតាបេស...**")

            # 🎯 ៤. Insert ចូលតារាង schedules ក្នុង Supabase
            supabase.table("schedules").insert({
                "class_level": class_lvl,
                "subject_name": subject,
                "teacher_id": teacher_id,
                "study_day": study_day,
                "start_time": start_time,
                "end_time": end_time
            }).execute()

            # 📢 ៥. ផ្ញើសារលទ្ធផលជោគជ័យជូន Admin
            success_msg = (
                "🟢 **បន្ថែមព័ត៌មានកាលវិភាគជោគជ័យ!**\n\n"
                 f"🏫 **ថ្នាក់រៀន៖** `{class_lvl}`\n"
                 f"📖 **មុខវិជ្ជា៖** *{subject}*\n"
                 f"👨‍🏫 **ID គ្រូ៖** `{teacher_id if teacher_id else 'មិនមាន'}`\n"
                 f"📅 **ថ្ងៃសិក្សា៖** `{study_day}`\n"
                 f"⏰ **ម៉ោងសិក្សា៖** `{start_time} - {end_time}`"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ Add Schedule Error: {e}")
            # ករណីជួបលក្ខខណ្ឌ Unique Constraint (ថ្នាក់ ដដែល, ថ្ងៃដដែល, ម៉ោងដដែល)
            if "unique_class_schedule" in str(e):
                bot.send_message(chat_id, "❌ **មិនអាចបន្ថែមបានទេ!** ដោយសារថ្នាក់នេះមានកាលវិភាគរៀនចំម៉ោង និងថ្ងៃនេះរួចរាល់ហើយបាទ។")
            else:
                bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
                # 🏢 មុខងារ៖ Admin វាយ /adddept ដើម្បីបន្ថែមដេប៉ាតឺម៉ង់/ផ្នែក
                # 🏢 មុខងារ៖ បន្ថែមដេប៉ាតឺម៉ង់ និង Update ចូលតារាងគ្រូភ្លាមៗ
    # ========================================================
    @bot.message_handler(commands=['adddept'])
    def add_department_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔒 ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            # 🔄 ២. កាត់យកអត្ថបទខាងក្រោយពាក្យ /adddept
            input_text = message.text.strip()[8:].strip()
            
            if not input_text or "," not in input_text:
                guide_msg = (
                    "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
                    "សូមវាយ៖ `/adddept IDគ្រូ, ឈ្មោះដេប៉ាតឺម៉ង់/ផ្នែក`\n\n"
                    "💡 *ឧទាហរណ៍៖* `/adddept TCH001, វិទ្យាសាស្ត្រពិត`"
                )
                bot.reply_to(message, guide_msg, parse_mode='Markdown')
                return

            # បំបែកជា ២ ផ្នែក (ID គ្រូ និង ឈ្មោះផ្នែក)
            parts = input_text.split(",")
            t_id = parts[0].strip()
            dept_name = parts[1].strip()

            # 🔎 ៣. ឆែកមើលថាតើមាន ID គ្រូហ្នឹងក្នុងតារាង teachers អត់
            teacher_check = supabase.table("teachers").select("name").eq("teacher_id", t_id).execute()
            if not teacher_check.data:
                bot.reply_to(message, f"❌ **រកមិនឃើញគ្រូដែលមាន ID `{t_id}` ទេ!** សូមពិនិត្យមើល ID គ្រូឡើងវិញ។")
                return
            
            t_name = teacher_check.data[0]['name']

            # 🎯 ៤. Insert ចូលតារាង departments (ប្រើ upsert បើមានឈ្មោះហ្នឹងហើយ វាទាញយក ID មកប្រើ តែបើអត់ទាន់មានវាបង្កើតថ្មី)
            dept_res = supabase.table("departments").upsert({"department_name": dept_name}, on_conflict="department_name").execute()
            
            # ទាញយកលេខ ID ផ្នែកដែលទើបតែបង្កើត ឬមានស្រាប់
            dept_id = dept_res.data[0]['id']

            # 🔄 ៥. រត់ទៅ Update ក្នុងតារាង teachers ត្រង់ ID គ្រូដែលបានកំណត់
            supabase.table("teachers").update({"department_id": dept_id}).eq("teacher_id", t_id).execute()

            # 📢 ៦. ផ្ញើសារលទ្ធផលជោគជ័យ
            success_msg = (
                "🟢 **រៀបចំរចនាសម្ព័ន្ធគ្រូជោគជ័យ!**\n\n"
                f"🏢 **បានបង្កើតផ្នែក៖** `{dept_name}` (ID: {dept_id})\n"
                f"👤 **បានបច្ចុប្បន្នភាពគ្រូ៖** លោកគ្រូ/អ្នកគ្រូ `{t_name}` (ID: {t_id}) ឥឡូវនេះស្ថិតក្នុងផ្នែកនេះហើយបាទ។"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ Add Dept & Update Teacher Error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
            # 🎓 មុខងារ៖ បន្ថែមជំនាញសិក្សា និង Update ចូលតារាងគ្រូភ្លាមៗ
    # ========================================================
    @bot.message_handler(commands=['addmajor'])
    def add_major_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔒 ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            # 🔄 ២. កាត់យកអត្ថបទនៅខាងក្រោយពាក្យ /addmajor
            input_text = message.text.strip()[9:].strip()
            
            if not input_text or input_text.count(",") < 2:
                guide_msg = (
                    "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
                    "សូមវាយ៖ `/addmajor IDគ្រូ, ឈ្មោះផ្នែក, ឈ្មោះជំនាញថ្មី`\n\n"
                    "💡 *ឧទាហរណ៍៖* `/addmajor TCH001, វិទ្យាសាស្ត្រពិត, គណិតវិទ្យា`"
                )
                bot.reply_to(message, guide_msg, parse_mode='Markdown')
                return

            # បំបែកជា ៣ ផ្នែក
            parts = input_text.split(",")
            t_id = parts[0].strip()
            dept_name = parts[1].strip()
            major_name = parts[2].strip()

            # 🔎 ៣. ឆែកមើល ID គ្រូក្នុងតារាង teachers
            teacher_check = supabase.table("teachers").select("name").eq("teacher_id", t_id).execute()
            if not teacher_check.data:
                bot.reply_to(message, f"❌ **រកមិនឃើញគ្រូដែលមាន ID `{t_id}` ទេ!**")
                return
            t_name = teacher_check.data[0]['name']

            # 🔎 ៤. ស្វែងរក department_id ពីឈ្មោះផ្នែក
            dept_res = supabase.table("departments").select("id").eq("department_name", dept_name).execute()
            if not dept_res.data:
                bot.reply_to(message, f"❌ **រកមិនឃើញផ្នែកឈ្មោះ `{dept_name}` ទេ!** សូមបង្កើតផ្នែកនេះជាមួយ `/adddept` មុនសិន។")
                return
            dept_id = dept_res.data[0]['id']

            # 🎯 ៥. Insert ចូលតារាង majors (ប្រើ upsert ការពារឈ្មោះជាន់គ្នា)
            major_res = supabase.table("majors").upsert({
                "department_id": dept_id,
                "major_name": major_name
            }, on_conflict="department_id, major_name").execute()
            
            major_id = major_res.data[0]['id']

            # 🔄 ៦. រត់ទៅ Update ក្នុងតារាង teachers ភ្លាមៗ
            supabase.table("teachers").update({"major_id": major_id}).eq("teacher_id", t_id).execute()

            # 📢 ៧. ផ្ញើសារលទ្ធផលជោគជ័យ
            success_msg = (
                "🟢 **ភ្ជាប់ជំនាញសិក្សាជូនគ្រូរួចរាល់!**\n\n"
                f"🏢 **ផ្នែក៖** `{dept_name}` (ID: {dept_id})\n"
                f"🎓 **ជំនាញសិក្សាថ្មី៖** `{major_name}` (ID: {major_id})\n"
                f"👤 **គ្រូដែលទទួលបាន៖** លោកគ្រូ/អ្នកគ្រូ `{t_name}` (ID: {t_id})"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ Add Major & Update Teacher Error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
            # 📅 មុខងារ៖ Admin វាយ /addnotice ដើម្បីបង្កើតសេចក្ដីប្រកាស និងផ្ញើទៅគ្រប់គ្នា (Broadcast)
            
    # 📅 មុខងារ៖ Admin វាយ /addnotice បាញ់ទៅកាន់ STUDENT, TEACHER, ALL (ជួសជុលរឿងគ្មាន group_chat_id ក្នុងតារាងគ្រូ)
    # ===================================================================================
    # @bot.message_handler(commands=['addnotice'])
    # def add_notice_command(message):
    #     chat_id = message.chat.id
    #     user_id = message.from_user.id
        
    #     try:
    #         # 🔒 ១. ឆែកសិទ្ធិ Admin
    #         user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
    #         if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
    #             bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
    #             return

        #     # 🔄 ២. កាត់យកអត្ថបទខាងក្រោយពាក្យ /addnotice
        #     input_text = message.text.strip()[10:].strip()
            
        #     if not input_text or input_text.count(",") < 2:
        #         guide_msg = (
        #             "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
        #             "សូមវាយ៖ `/addnotice គោលដៅ, ចំណងជើង, ខ្លឹមសារព័ត៌មាន`\n\n"
        #             "💡 *ជម្រើសគោលដៅ (Target)៖*\n"
        #             "🔹 `STUDENT` ➡️ ផ្ញើទៅគ្រប់គ្រុបថ្នាក់ និងសិស្សទាំងអស់\n"
        #             "🔹 `TEACHER` ➡️ ផ្ញើទៅលោកគ្រូទាំងអស់ (Chat ផ្ទាល់ខ្លួន)\n"
        #             "🔹 `ALL`     ➡️ ផ្ញើទៅសាលាទាំងមូល (គ្រូ សិស្ស និងគ្រប់គ្រុបថ្នាក់ទាំងអស់)\n"
        #             "🔹 `ឈ្មោះថ្នាក់` ➡️ ផ្ញើចំគោលដៅថ្នាក់ជាក់លាក់ (ឧទាហរណ៍៖ `5_SPD`)\n\n"
        #             "💡 *គំរូ៖* `/addnotice ALL, ជូនដំណឹងរួម, ថ្ងៃស្អែកសាលាឈប់សម្រាក។`"
        #         )
        #         bot.reply_to(message, guide_msg, parse_mode='Markdown')
        #         return

        #     # បំបែកទិន្នន័យជា ៣ ផ្នែក
        #     parts = input_text.split(",", 2)
        #     target = parts[0].strip().upper()
        #     title = parts[1].strip()
        #     content = parts[2].strip()

        #     bot.send_message(chat_id, f"⏳ **កំពុងរក្សាទុកចូលតារាង school_notices និងចាប់ផ្ដើមបាញ់ប្រកាសទៅ {target}...**")

        #     # 🎯 ៣. រក្សាទុក (Insert) ចូលទៅក្នុងតារាង school_notices
        #     supabase.table("school_notices").insert({
        #         "title": title,
        #         "content": content,
        #         "notice_type": target, 
        #         "created_by_telegram_id": int(user_id) 
        #     }).execute()

        #     # 🎯 ៤. រៀបចំទម្រង់សារសម្រាប់ផ្ញើចេញដ៏ស្រស់ស្អាត
        #     broadcast_msg = (
        #         "📢 **[ សេចក្ដីជូនដំណឹងថ្មីពីសាលា ]**\n"
        #         f"📌 **ចំណងជើង៖** {title}\n"
        #         f"----------------------------------------\n"
        #         f"📝 **ខ្លឹមសារ៖** {content}\n\n"
        #         "🔔 *សូមលោកគ្រូ-អ្នកគ្រូ សិស្សានុសិស្ស និងអាណាព្យាបាលទាំងអស់ជ្រាបជាព័ត៌មាន!*"
        #     )

        #     teacher_chats = set()
        #     student_parent_chats = set()
        #     group_chats = set()

        #     # 🔎 ៥. ទាញយកទិន្នន័យពីដាតាបេស (កែសម្រួលលុប group_chat_id ចេញពីតារាង teachers)
        #     if target == "STUDENT":
        #         students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id").execute()
        #         if students_res.data:
        #             for s in students_res.data:
        #                 if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
        #                 if s.get('student_id') and str(s['student_id']).isdigit(): student_parent_chats.add(str(s['student_id']))
        #                 if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "" and str(s['group_chat_id']).strip().lower() != "null":
        #                     group_chats.add(str(s['group_chat_id']).strip())
                            
        #     elif target == "TEACHER":
        #         # ទាញយកតែ telegram_id ធម្មតាប៉ុណ្ណោះ ការពារ Error គ្មាន column
        #         teachers_res = supabase.table("teachers").select("telegram_id").execute()
        #         if teachers_res.data:
        #             for t in teachers_res.data:
        #                 if t.get('telegram_id'): teacher_chats.add(str(t['telegram_id']))
                            
        #     elif target == "ALL":
        #         # ទាញយកគ្រូ (យកតែ telegram_id)
        #         teachers_res = supabase.table("teachers").select("telegram_id").execute()
        #         if teachers_res.data:
        #             for t in teachers_res.data:
        #                 if t.get('telegram_id'): teacher_chats.add(str(t['telegram_id']))
        #         # យកសិស្ស និងគ្រប់គ្រុបថ្នាក់        
        #         students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id").execute()
        #         if students_res.data:
        #             for s in students_res.data:
        #                 if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
        #                 if s.get('student_id') and str(s['student_id']).isdigit(): student_parent_chats.add(str(s['student_id']))
        #                 if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "" and str(s['group_chat_id']).strip().lower() != "null":
        #                     group_chats.add(str(s['group_chat_id']).strip())
        #     else:
        #         # 🎯 ករណីបាញ់ចំឈ្មោះថ្នាក់ជាក់លាក់ (ដូចជា 5_SPD)
        #         students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id")\
        #             .or_(f"class_level.ilike.{target}, class_level.ilike.%{target}%").execute()
                
        #         if students_res.data:
        #             for s in students_res.data:
        #                 if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
        #                 if s.get('student_id') and str(s['student_id']).isdigit(): student_parent_chats.add(str(s['student_id']))
        #                 if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "" and str(s['group_chat_id']).strip().lower() != "null":
        #                     group_chats.add(str(s['group_chat_id']).strip())
                
        #         # ទាញយកគ្រូដែលបង្រៀនថ្នាក់នេះពីតារាង schedules
        #         sched_res = supabase.table("schedules").select("teacher_id").or_(f"class_level.ilike.{target}, class_level.ilike.%{target}%").execute()
        #         if sched_res.data:
        #             t_ids = [sch['teacher_id'] for sch in sched_res.data if sch.get('teacher_id')]
        #             if t_ids:
        #                 teachers_res = supabase.table("teachers").select("telegram_id").in_("teacher_id", t_ids).execute()
        #                 if teachers_res.data:
        #                     for t in teachers_res.data:
        #                         if t.get('telegram_id'): teacher_chats.add(str(t['telegram_id']))

        #     # 🚀 ៦. ចាប់ផ្ដើមរត់ Loop បាញ់ប្រកាសទៅកាន់គ្រប់ច្រក (បម្លែងជា int ធានាភាពហ្មត់ចត់)
        #     count_teacher = 0
        #     count_student_parent = 0
        #     count_group = 0

        #     for t_id in teacher_chats:
        #         try:
        #             bot.send_message(int(t_id), broadcast_msg, parse_mode='Markdown')
        #             count_teacher += 1
        #         except Exception: pass

        #     for sp_id in student_parent_chats:
        #         try:
        #             bot.send_message(int(sp_id), broadcast_msg, parse_mode='Markdown')
        #             count_student_parent += 1
        #         except Exception: pass

        #     for g_id in group_chats:
        #         try:
        #             bot.send_message(int(g_id), broadcast_msg, parse_mode='Markdown')
        #             count_group += 1
        #         except Exception as e_group:
        #             print(f"❌ Error sending to group {g_id}: {e_group}")

        #     # 🟢 ៧. បូកសរុបរបាយការណ៍លម្អិតត្រឡប់ជូន Admin វិញ
        #     report = (
        #         "🟢 **រក្សាទុកដាតាបេស និងផ្សព្វផ្សាយជោគជ័យ!**\n\n"
        #         f"🗄️ **ស្ថានភាព៖** រក្សាទុកចូលតារាង `school_notices` រួចរាល់\n"
        #         f"🎯 **គោលដៅបាញ់សារ៖** `{target}`\n"
        #         f"----------------------------------------\n"
        #         f"👨‍🏫 **ផ្ញើទៅ Chat គ្រូផ្ទាល់ខ្លួន៖** `{count_teacher}` នាក់\n"
        #         f"📲 **ផ្ញើទៅ Chat សិស្ស/អាណាព្យាបាល៖** `{count_student_parent}` នាក់\n"
        #         f"🏫 **បាញ់ចូល Group ថ្នាក់រៀនសិស្ស៖** `{count_group}` គ្រុប"
        #     )
        #     bot.send_message(chat_id, report, parse_mode='Markdown')

        # except Exception as e:
        #     print(f"❌ Notice Insert & Broadcast Error: {e}")
        #     bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
    
    # ===================================================================================
    # 📅 មុខងារ៖ Admin វាយ /addnotice ដើម្បីបង្កើតសេចក្ដីប្រកាស + ប៊ូតុង Acknowledge ឌីជីថល
    # ===================================================================================
    bot.message_handler(commands=['addnotice'])
    def add_notice_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔒 ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            # 🔄 ២. កាត់យកអត្ថបទខាងក្រោយពាក្យ /addnotice
            input_text = message.text.strip()[10:].strip()
            
            if not input_text or input_text.count(",") < 2:
                guide_msg = (
                    "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
                    "សូមវាយ៖ `/addnotice គោលដៅ, ចំណងជើង, ខ្លឹមសារព័ត៌មាន`\n\n"
                    "💡 *ជម្រើសគោលដៅ (Target)៖*\n"
                    "🔹 `STUDENT` ➡️ ផ្ញើទៅគ្រប់គ្រុបថ្នាក់ និងសិស្សទាំងអស់\n"
                    "🔹 `TEACHER` ➡️ ផ្ញើទៅលោកគ្រូទាំងអស់ (Chat ផ្ទាល់ខ្លួន)\n"
                    "🔹 `ALL`      ➡️ ផ្ញើទៅសាលាទាំងមូល (គ្រូ សិស្ស និងគ្រប់គ្រុបថ្នាក់ទាំងអស់)\n"
                    "🔹 `ឈ្មោះថ្នាក់` ➡️ ផ្ញើចំគោលដៅថ្នាក់ជាក់លាក់ (ឧទាហរណ៍៖ `5_SPD`)\n\n"
                    "💡 *គំរូ៖* `/addnotice ALL, ជូនដំណឹងរួម, ថ្ងៃស្អែកសាលាឈប់សម្រាក។`"
                )
                bot.reply_to(message, guide_msg, parse_mode='Markdown')
                return

            # បំបែកទិន្នន័យជា ៣ ផ្នែក
            parts = input_text.split(",", 2)
            target = parts[0].strip().upper()
            title = parts[1].strip()
            content = parts[2].strip()

            bot.send_message(chat_id, f"⏳ **កំពុងរក្សាទុកចូលតារាង school_notices និងចាប់ផ្ដើមបាញ់ប្រកាសទៅ {target}...**")

            # 🎯 ៣. រក្សាទុក (Insert) ចូលទៅក្នុងតារាង school_notices រួចទាញយក ID មកប្រើភ្លាមៗ
            notice_res = supabase.table("school_notices").insert({
                "title": title,
                "content": content,
                "notice_type": target, 
                "created_by_telegram_id": int(user_id) 
            }).select().execute()

            # ចាប់យក notice_id ដែលទើបតែ Insert មិញ
            notice_id = notice_res.data[0]['id'] if notice_res.data else None

            # 🎯 ៤. រៀបចំទម្រង់សារសម្រាប់ផ្ញើចេញដ៏ស្រស់ស្អាត
            broadcast_msg = (
                "📢 **[ សេចក្ដីជូនដំណឹងថ្មីពីសាលា ]**\n"
                f"📌 **ចំណងជើង៖** {title}\n"
                f"----------------------------------------\n"
                f"📝 **ខ្លឹមសារ៖** {content}\n\n"
                "🔔 *សូមលោកគ្រូ-អ្នកគ្រូ សិស្សានុសិស្ស និងអាណាព្យាបាលទាំងអស់ជ្រាបជាព័ត៌មាន!*"
            )

            # 🎛️ ៥. បង្កើតប៊ូតុង Inline Keyboard សម្រាប់ឱ្យចុច "ទទួលដឹងឮ" (ភ្ជាប់ notice_id)
            markup_ack = types.InlineKeyboardMarkup()
            markup_ack.add(types.InlineKeyboardButton("✅ ខ្ញុំបានអាន និងទទួលដឹងឮ (Acknowledge)", callback_data=f"ack_{notice_id}"))

            teacher_chats = set()
            student_parent_chats = set()
            group_chats = set()

            # 🔎 ៦. ទាញយកទិន្នន័យពីដាតាបេស (កំណែទម្រង់ស្អាត គ្មាន group_chat_id ក្នុងតារាង teachers)
            if target == "STUDENT":
                students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id").execute()
                if students_res.data:
                    for s in students_res.data:
                        if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
                        if s.get('student_id') and str(s['student_id']).isdigit(): student_parent_chats.add(str(s['student_id']))
                        if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "" and str(s['group_chat_id']).strip().lower() != "null":
                            group_chats.add(str(s['group_chat_id']).strip())
                            
            elif target == "TEACHER":
                teachers_res = supabase.table("teachers").select("telegram_id").execute()
                if teachers_res.data:
                    for t in teachers_res.data:
                        if t.get('telegram_id'): teacher_chats.add(str(t['telegram_id']))
                            
            elif target == "ALL":
                teachers_res = supabase.table("teachers").select("telegram_id").execute()
                if teachers_res.data:
                    for t in teachers_res.data:
                        if t.get('telegram_id'): teacher_chats.add(str(t['telegram_id']))
                        
                students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id").execute()
                if students_res.data:
                    for s in students_res.data:
                        if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
                        if s.get('student_id') and str(s['student_id']).isdigit(): student_parent_chats.add(str(s['student_id']))
                        if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "" and str(s['group_chat_id']).strip().lower() != "null":
                            group_chats.add(str(s['group_chat_id']).strip())
            else:
                students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id")\
                    .or_(f"class_level.ilike.{target}, class_level.ilike.%{target}%").execute()
                
                if students_res.data:
                    for s in students_res.data:
                        if s.get('parent_telegram_id'): student_parent_chats.add(str(s['parent_telegram_id']))
                        if s.get('student_id') and str(s['student_id']).isdigit(): student_parent_chats.add(str(s['student_id']))
                        if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "" and str(s['group_chat_id']).strip().lower() != "null":
                            group_chats.add(str(s['group_chat_id']).strip())
                
                sched_res = supabase.table("schedules").select("teacher_id").or_(f"class_level.ilike.{target}, class_level.ilike.%{target}%").execute()
                if sched_res.data:
                    t_ids = [sch['teacher_id'] for sch in sched_res.data if sch.get('teacher_id')]
                    if t_ids:
                        teachers_res = supabase.table("teachers").select("telegram_id").in_("teacher_id", t_ids).execute()
                        if teachers_res.data:
                            for t in teachers_res.data:
                                if t.get('telegram_id'): teacher_chats.add(str(t['telegram_id']))

            # 🚀 ៧. ចាប់ផ្ដើមរត់ Loop បាញ់ប្រកាស + កត់ត្រាការផ្ញើទៅដល់ចូល notice_engagements
            count_teacher = 0
            count_student_parent = 0
            count_group = 0

            # ក. បាញ់ទៅលោកគ្រូ-អ្នកគ្រូ (ផ្ទាល់ខ្លួន)
            for t_id in teacher_chats:
                try:
                    bot.send_message(int(t_id), broadcast_msg, parse_mode='Markdown', reply_markup=markup_ack)
                    count_teacher += 1
                    if notice_id:
                        supabase.table("notice_engagements").upsert({
                            "notice_id": notice_id, 
                            "parent_telegram_id": int(t_id), 
                            "is_seen": True, 
                            "seen_at": datetime.now().isoformat()
                        }, on_conflict="notice_id,parent_telegram_id").execute()
                except Exception: pass

            # ខ. បាញ់ទៅសិស្ស / អាណាព្យាបាល (ផ្ទាល់ខ្លួន)
            for sp_id in student_parent_chats:
                try:
                    bot.send_message(int(sp_id), broadcast_msg, parse_mode='Markdown', reply_markup=markup_ack)
                    count_student_parent += 1
                    # 🔄 កត់ត្រាអូតូភ្លាមៗថា សារត្រូវបានផ្ញើទៅដល់ដៃពួកគាត់ហើយ (is_seen = True)
                    if notice_id:
                        supabase.table("notice_engagements").upsert({
                            "notice_id": notice_id, 
                            "parent_telegram_id": int(sp_id), 
                            "is_seen": True, 
                            "seen_at": datetime.now().isoformat()
                        }, on_conflict="notice_id,parent_telegram_id").execute()
                except Exception: pass

            # គ. បាញ់ចូល Group ថ្នាក់រៀនសិស្ស (គ្រុបរួមមិនបាច់ចង Acknowledge ឯកជនទេ)
            for g_id in group_chats:
                try:
                    bot.send_message(int(g_id), broadcast_msg, parse_mode='Markdown')
                    count_group += 1
                except Exception as e_group:
                    print(f"❌ Error sending to group {g_id}: {e_group}")

            # 🟢 ៨. បូកសរុបរបាយការណ៍លម្អិតត្រឡប់ជូន Admin វិញ
            report = (
                "🟢 **រក្សាទុកដាតាបេស និងផ្សព្វផ្សាយជោគជ័យ!**\n\n"
                f"🗄️ **ស្ថានភាព៖** រក្សាទុកចូលតារាង `school_notices` និងកត់ត្រាចូល `notice_engagements` រួចរាល់\n"
                f"🎯 **គោលដៅបាញ់សារ៖** `{target}`\n"
                f"----------------------------------------\n"
                f"👨‍🏫 **ផ្ញើទៅ Chat គ្រូផ្ទាល់ខ្លួន៖** `{count_teacher}` នាក់ (ភ្ជាប់ប៊ូតុង)\n"
                f"📲 **ផ្ញើទៅ Chat សិស្ស/អាណាព្យាបាល៖** `{count_student_parent}` នាក់ (ភ្ជាប់ប៊ូតុង)\n"
                f"🏫 **បាញ់ចូល Group ថ្នាក់រៀនសិស្ស៖** `{count_group}` គ្រុប"
            )
            bot.send_message(chat_id, report, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ Notice Insert & Broadcast Error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')


    # ===================================================================================
    # 🎛️ មុខងារ៖ ស្ទាក់ចាប់ការចុចប៊ូតុង "Acknowledge / ទទួលដឹងឮ" រួចកែប្រែស្ថានភាពក្នុង Database
    # ===================================================================================
    @bot.callback_query_handler(func=lambda call: call.data.startswith('ack_'))
    def handle_notice_acknowledgement(call):
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        notice_id = int(call.data.split('_')[1]) # ទាញយក ID នៃ notice ចេញពីប៊ូតុង
        
        try:
            # 🔄 អាប់ដេតស្ថានភាពក្នុងតារាង notice_engagements ទៅជាបានចុះហត្ថលេខា (is_acknowledged = True)
            supabase.table("notice_engagements").upsert({
                "notice_id": notice_id,
                "parent_telegram_id": user_id,
                "is_acknowledged": True,
                "acknowledged_at": datetime.now().isoformat()
            }, on_conflict="notice_id,parent_telegram_id").execute()
            
            # ✂️ កែប្រែផ្ទាំងសារដើម លុបប៊ូតុងចាស់ចោលភ្លាម ការពារការចុចដដែលៗនាំឌុប
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
            
            # 📢 ឆ្លើយតប Callback query ទៅកាន់ Telegram API ដើម្បីបំបាត់សញ្ញាវិលៗលើប៊ូតុង
            bot.answer_callback_query(call.id, text="🟢 បានទទួលដឹងឮរួចរាល់!")
            
            # ផ្ញើសារអបអរសាទរត្រឡប់ទៅប្រាប់គាត់វិញ
            bot.send_message(chat_id, "✅ **លោកអ្នកបានចុះហត្ថលេខាឌីជីថល ទទួលដឹងឮលើសេចក្ដីជូនដំណឹងនេះរួចរាល់ហើយបាទ! សូមអរគុណ។**")
            
        except Exception as e:
            print(f"❌ Callback Acknowledge Error: {e}")
            bot.answer_callback_query(call.id, text="❌ មិនអាចកត់ត្រាការយល់ព្រមបានទេ")
    
    # ========================================================
    @bot.message_handler(commands=['setclass'])
    def set_class_group_id_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # 🔒 ១. ឆែកមើលថាតើវាយនៅក្នុង Group មែនអត់ (មិនមែនឆាតផ្ទាល់ខ្លួន)
        if message.chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "⚠️ **មុខងារនេះសម្រាប់ប្រើប្រាស់នៅក្នុង Group ថ្នាក់រៀនតែប៉ុណ្ណោះបាទ!**")
            return
            
        try:
            # 🔒 ២. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិជា Admin ឡើយ។")
                return

            # 🔄 ៣. កាត់យកឈ្មោះថ្នាក់រៀនខាងក្រោយពាក្យ /setclass
            class_name_input = message.text.strip()[9:].strip().upper() # បម្លែងជាអក្សរធំជានិច្ច
            
            if not class_name_input:
                bot.reply_to(message, "⚠️ **ទម្រង់ខុសហើយ Admin!**\nសូមវាយ៖ `/setclass ឈ្មោះថ្នាក់`\n\n💡 *ឧទាហរណ៍៖* `/setclass GRADE12_A`")
                return

            bot.reply_to(message, f"⏳ **កំពុងភ្ជាប់ ID គ្រុបនេះ ទៅកាន់សិស្សថ្នាក់ `{class_name_input}` ទាំងអស់...**")

            # 🎯 ៤. រត់ទៅ Update តារាង students ត្រង់សិស្សណាដែលមាន class_level ត្រូវនឹង Admin វាយ
            # វានឹងយក chat_id គ្រុបបច្ចុប្បន្ន ទៅញាត់ចូល column group_chat_id អូតូ
            update_res = supabase.table("students")\
                .update({"group_chat_id": str(chat_id)})\
                .eq("class_level", class_name_input)\
                .execute()

            # 📢 ៥. រាយការណ៍លទ្ធផល
            if update_res.data:
                updated_students_count = len(update_res.data)
                success_msg = (
                    f"🎯 **ភ្ជាប់គ្រុបថ្នាក់រៀនអូតូជោគជ័យ!**\n\n"
                    f"🏫 **ថ្នាក់រៀន៖** `{class_name_input}`\n"
                    f"🆔 **ID គ្រុបដែលចាប់បាន៖** `{chat_id}`\n"
                    f"👥 **ចំនួនសិស្សដែលទទួលបាន៖** `{updated_students_count}` នាក់ត្រូវបានដាក់បញ្ចូល។"
                )
                bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            else:
                bot.send_message(
                    chat_id, 
                    f"⚠️ **ធ្វើបច្ចុប្បន្នភាពបរាជ័យ!**\n"
                    f"រកមិនឃើញសិស្សណាម្នាក់ស្ថិតក្នុងថ្នាក់ `{class_name_input}` នៅក្នុងតារាង `students` ឡើយ។ "
                    f"សូមប្រាកដថាបានបញ្ចូលសិស្សទៅក្នុងថ្នាក់នេះមុនសិនបាទ។",
                    parse_mode='Markdown'
                )

        except Exception as e:
            print(f"❌ Set Class Group ID Error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
            # 📆 មុខងារ៖ Admin វាយ /addholiday ដើម្បីបន្ថែមថ្ងៃឈប់សម្រាក និងបាញ់ប្រកាសភ្លាមៗគ្រប់ច្រក
    # ========================================================
    @bot.message_handler(commands=['addholiday'])
    def add_holiday_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔒 ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិឡើយ។")
                return

            # 🔄 ២. កាត់យកអត្ថបទខាងក្រោយពាក្យ /addholiday
            input_text = message.text.strip()[11:].strip()
            
            # ឆែកទម្រង់ (ត្រូវមានសញ្ញាក្បៀសយ៉ាងហោចណាស់ ២)
            if not input_text or input_text.count(",") < 2:
                guide_msg = (
                    "⚠️ **ទម្រង់ខុសហើយ Admin!**\n"
                    "សូមវាយ៖ `/addholiday ឈ្មោះខ្មែរ, ឈ្មោះអង់គ្លេស, ឆ្នាំ-ខែ-ថ្ងៃ, តំណភ្ជាប់រូបភាព(បើមាន)`\n\n"
                    "💡 *គំរូអត់រូបភាព៖* `/addholiday ពិធីបុណ្យអុំទូក, Water Festival, 2026-11-23`\n"
                    "💡 *គំរូមានរូបភាព៖* `/addholiday បុណ្យឯករាជ្យជាតិ, Independence Day, 2026-11-09, https://example.com/image.jpg`"
                )
                bot.reply_to(message, guide_msg, parse_mode='Markdown')
                return

            # បំបែកទិន្នន័យ
            parts = [p.strip() for p in input_text.split(",")]
            name_km = parts[0]
            name_en = parts[1]
            h_date = parts[2]
            h_image = parts[3] if len(parts) > 3 else None

            bot.send_message(chat_id, "⏳ **កំពុងរក្សាទុក និងចាប់ផ្ដើមបាញ់ប្រកាសទៅកាន់ គ្រូ សិស្ស និងគ្រុបថ្នាក់...**")

            # 🎯 ៣. Insert ចូលតារាង holidays ក្នុង Supabase (កំណត់ announcement_sent = 1 ព្រោះយើងបាញ់ភ្លាមៗតែម្ដង)
            supabase.table("holidays").insert({
                "event_name_km": name_km,
                "event_name_en": name_en,
                "holiday_date": h_date,
                "holiday_image": h_image,
                "announcement_sent": 1 
            }).execute()

            # 📢 ៤. រៀបចំទម្រង់សារប្រកាសផ្លូវការ
            announcement_msg = (
                "🚨 **[ សេចក្ដីជូនដំណឹង៖ ថ្ងៃឈប់សម្រាកសាលា ]**\n\n"
                "សូមជម្រាបជូនលោកគ្រូ អ្នកគ្រូ សិស្សានុសិស្ស និងអាណាព្យាបាលទាំងអស់មេត្តាជ្រាបថា សាលានឹងមានការ**ឈប់សម្រាក**ក្នុងឱកាស៖\n\n"
                f"🇰🇭 **{name_km}**\n"
                f"🇬🇧 **{name_en}**\n"
                f"📅 **កាលបរិច្ឆេទ៖** {h_date}\n\n"
                "✨ *សូមជូនពរឱ្យទទួលបានការសម្រាកលំហែកាយយ៉ាងសប្បាយរីករាយ និងសុវត្ថិភាព!*"
            )

            # 🔎 ៥. ទាញយក ID គ្រប់ច្រកពី Database (Teachers & Students)
            teachers_res = supabase.table("teachers").select("telegram_id").execute()
            students_res = supabase.table("students").select("student_id", "parent_telegram_id", "group_chat_id").execute()

            # បង្កើត Set ដើម្បីប្រមូល ID ការពារកុំឱ្យផ្ញើជាន់គ្នា
            target_chats = set()
            target_groups = set()

            # ប្រមូល ID របស់គ្រូ (ពីតារាង teachers)
            if teachers_res.data:
                for t in teachers_res.data:
                    if t.get('telegram_id'): 
                        target_chats.add(str(t['telegram_id']))

            # 🔗 ប្រមូល ID សិស្ស, អាណាព្យាបាល និង ID គ្រុប (ពីតារាង students)
            if students_res.data:
                for s in students_res.data:
                    if s.get('parent_telegram_id'): 
                        target_chats.add(str(s['parent_telegram_id']))
                    if s.get('student_id') and str(s['student_id']).isdigit(): 
                        target_chats.add(str(s['student_id']))
                    if s.get('group_chat_id') and str(s['group_chat_id']).strip() != "": 
                        target_groups.add(str(s['group_chat_id']).strip())

            # 🚀 ៦. ចាប់ផ្ដើមរត់ Loop បាញ់ផ្ញើចេញភ្លាមៗ (Instant Broadcast)
            count_private = 0
            count_group = 0

            # ក. បាញ់ទៅកាន់បុគ្គល (Private Chat របស់គ្រូ សិស្ស អាណាព្យាបាល)
            for p_id in target_chats:
                try:
                    if h_image: 
                        bot.send_photo(p_id, h_image, caption=announcement_msg, parse_mode='Markdown')
                    else: 
                        bot.send_message(p_id, announcement_msg, parse_mode='Markdown')
                    count_private += 1
                except Exception: 
                    pass
                
            # ខ. បាញ់ចូល Group ថ្នាក់រៀនសិស្ស (Group Chat អូតូ)
            for g_id in target_groups:
                try:
                    if h_image: 
                        bot.send_photo(g_id, h_image, caption=announcement_msg, parse_mode='Markdown')
                    else: 
                        bot.send_message(g_id, announcement_msg, parse_mode='Markdown')
                    count_group += 1
                except Exception: 
                    pass

            # 🟢 ៧. រាយការណ៍លទ្ធផលជោគជ័យជូន Admin វិញ
            report_msg = (
                "🟢 **បន្ថែមថ្ងៃឈប់សម្រាក និងបាញ់ប្រកាសជោគជ័យ!**\n\n"
                f"🇰🇭 **ឱកាស៖** `{name_km}`\n"
                f"📅 **កាលបរិច្ឆេទ៖** `{h_date}`\n"
                f"----------------------------------------\n"
                f"📲 **ផ្ញើទៅសមាជិក (Private)៖** `{count_private}` នាក់\n"
                f"🏫 **បាញ់ចូលគ្រុបថ្នាក់រៀនអូតូ៖** `{count_group}` គ្រុប\n\n"
                "✨ រក្សាទុកក្នុង Database និងចែកចាយព័ត៌មានរួចរាល់ភិរម្យបាទ!"
            )
            bot.send_message(chat_id, report_msg, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ Add Holiday & Broadcast Error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
            # ===================================================================================
    # 📊 មុខងារ៖ Admin វាយ /school_stats ដើម្បីមើលស្ថិតិសរុបនៃសាលារៀន (DUC Metrics)
    # ===================================================================================
    @bot.message_handler(commands=['school_stats'])
    def school_stats_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔒 ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិមើលទិន្នន័យនេះឡើយ។")
                return

            bot.send_message(chat_id, "⏳ **កំពុងប្រមូលទិន្នន័យ និងគណនាស្ថិតិរួមពី Supabase...**")

            # 🔎 ២. រត់ទៅរាប់ទិន្នន័យពីគ្រប់តារាងស្នូល (Count Data)
            # រាប់ចំនួនសិស្សសរុប
            students_res = supabase.table("students").select("student_id", count="exact").execute()
            total_students = students_res.count if students_res.count is not None else 0

            # រាប់ចំនួនលោកគ្រូ-អ្នកគ្រូ
            teachers_res = supabase.table("teachers").select("teacher_id", count="exact").execute()
            total_teachers = teachers_res.count if teachers_res.count is not None else 0

            # រាប់ចំនួនកាលវិភាគ/ថ្នាក់រៀនប្លែកៗគ្នា
            schedules_res = supabase.table("schedules").select("class_level").execute()
            distinct_classes = set()
            if schedules_res.data:
                for sch in schedules_res.data:
                    if sch.get('class_level'):
                        distinct_classes.add(sch['class_level'].strip().upper())
            total_classes = len(distinct_classes)

            # រាប់ចំនួនផ្នែក/ដេប៉ាតាម៉ង់
            dept_res = supabase.table("departments").select("id", count="exact").execute()
            total_depts = dept_res.count if dept_res.count is not None else 0

            # រាប់ចំនួនសេចក្ដីជូនដំណឹងដែលបានបាញ់ប្រកាស
            notices_res = supabase.table("school_notices").select("id", count="exact").execute()
            total_notices = notices_res.count if notices_res.count is not None else 0

            # 🟢 ៣. រៀបចំសាររបាយការណ៍ស្អាតៗផ្ញើជូន Admin
            stats_msg = (
                "📊 **[ របាយការណ៍ស្ថិតិរួមរបស់សាលា DUC ]**\n"
                f"📆 *គិតត្រឹមថ្ងៃទី៖ {datetime.now().strftime('%d-%m-%Y')}*\n"
                f"----------------------------------------\n\n"
                f"👨‍🎓 **សិស្សានុសិស្សសរុប៖** `{total_students}` នាក់\n"
                f"👨‍🏫 **លោកគ្រូ-អ្នកគ្រូសរុប៖** `{total_teachers}` នាក់\n"
                f"🏫 **ថ្នាក់រៀនសកម្មសរុប៖** `{total_classes}` ថ្នាក់\n"
                f"🏢 **ដេប៉ាតាម៉ង់/ផ្នែកសរុប៖** `{total_depts}` ផ្នែក\n"
                f"📢 **សេចក្ដីប្រកាសដែលបានផ្សាយ៖** `{total_notices}` លើក\n\n"
                f"----------------------------------------\n"
                "📈 _ទិន្នន័យត្រូវបានធ្វើបច្ចុប្បន្នភាពអូតូពីប្រព័ន្ធ API Core Engine_"
            )

            bot.send_message(chat_id, stats_msg, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ School Stats Error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
            # ===================================================================================
    # 📊 មុខងារ៖ Admin វាយ /hw_analytics ដើម្បីមើលអត្រាប្រគល់កិច្ចការផ្ទះរបស់សិស្សតាមថ្នាក់
    # ===================================================================================
    @bot.message_handler(commands=['hw_analytics'])
    def hw_analytics_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # 🔒 ១. ឆែកសិទ្ធិ Admin
            user_check = supabase.table("users").select("role").eq("telegram_id", str(user_id)).execute()
            if not user_check.data or user_check.data[0].get('role') != 'ADMIN':
                bot.reply_to(message, "❌ **សកម្មភាពត្រូវបានបដិសេធ!** លោកអ្នកមិនមានសិទ្ធិមើលទិន្នន័យនេះឡើយ។")
                return

            bot.send_message(chat_id, "⏳ **កំពុងវិភាគទិន្នន័យ Homework និងគណនាភាគរយ...**")

            # 🔎 ២. ទាញយកទិន្នន័យចាំបាច់ពី Supabase
            # ទាញយកបញ្ជី Homework ទាំងអស់ដែលគ្រូបានដាក់
            hw_res = supabase.table("homework").select("id", "class_level", "subject").execute()
            # ទាញយកបញ្ជីដែលសិស្សបានប្រគល់រួច
            submissions_res = supabase.table("homework_submissions").select("homework_id", "status").execute()
            # ទាញយកបញ្ជីសិស្សទាំងអស់ដើម្បីដឹងចំនួនសិស្សក្នុងថ្នាក់នីមួយៗ
            students_res = supabase.table("students").select("class_level").execute()

            if not hw_res.data:
                bot.send_message(chat_id, "ℹ️ **មិនទាន់មានទិន្នន័យកិច្ចការផ្ទះ (Homework) នៅក្នុងប្រព័ន្ធនៅឡើយទេ។**")
                return

            # 🧮 ៣. ដំណើរការគណនាស្ថិតិតាមថ្នាក់ (Data Processing)
            # គណនាចំនួនសិស្សសរុបក្នុងមួយថ្នាក់ៗ
            class_student_count = {}
            if students_res.data:
                for s in students_res.data:
                    c_level = s.get('class_level', '').strip().upper()
                    if c_level:
                        class_student_count[c_level] = class_student_count.get(c_level, 0) + 1

            # រាប់ចំនួនកិច្ចការដែលបានដាក់ និងការប្រគល់តាមថ្នាក់
            class_analytics = {}
            
            # បង្កើតទីតាំងដេកចាំសម្រាប់ថ្នាក់នីមួយៗដែលមាន Homework
            for hw in hw_res.data:
                c_level = hw.get('class_level', '').strip().upper()
                if not c_level: continue
                
                if c_level not in class_analytics:
                    class_analytics[c_level] = {
                        "total_hw_assigned": 0,
                        "expected_submissions": 0,
                        "actual_submissions": 0
                    }
                
                class_analytics[c_level]["total_hw_assigned"] += 1
                # ចំនួនដែលត្រូវប្រគល់សរុប = ចំនួនកិច្ចការដែលដាក់ x ចំនួនសិស្សក្នុងថ្នាក់នោះ
                students_in_class = class_student_count.get(c_level, 0)
                class_analytics[c_level]["expected_submissions"] += students_in_class

            # រាប់ចំនួនដែលសិស្សបានប្រគល់ពិតប្រាកដ (Actual Submissions)
            if submissions_res.data:
                # បង្កើត Dictionary ងាយស្រួលរកមើលថាតើ Homework ID នោះជារបស់ថ្នាក់ណា
                hw_to_class = {hw['id']: hw['class_level'].strip().upper() for hw in hw_res.data if hw.get('class_level')}
                
                for sub in submissions_res.data:
                    hw_id = sub.get('homework_id')
                    status = sub.get('status', '').upper()
                    
                    # រាប់តែទិន្នន័យដែលបានប្រគល់រួច (SUBMITTED ឬ GRADED)
                    if hw_id in hw_to_class and status in ['SUBMITTED', 'GRADED']:
                        c_level = hw_to_class[hw_id]
                        if c_level in class_analytics:
                            class_analytics[c_level]["actual_submissions"] += 1

            # 🟢 ៤. រៀបចំសាររបាយការណ៍លទ្ធផលផ្ញើជូន Admin
            report_msg = (
                "📊 **[ របាយការណ៍វិភាគកិច្ចការផ្ទះ (Homework Analytics) ]**\n"
                f"📆 *ប្រព័ន្ធធ្វើបច្ចុប្បន្នភាព៖ {datetime.now().strftime('%d-%m-%Y %H:%M')}*\n"
                f"----------------------------------------\n\n"
            )

            for c_level, data in sorted(class_analytics.items()):
                assigned = data["total_hw_assigned"]
                expected = data["expected_submissions"]
                actual = data["actual_submissions"]
                
                # គណនាភាគរយនៃការប្រគល់កិច្ចការផ្ទះ
                rate = (actual / expected * 100) if expected > 0 else 0.0
                
                # ដាក់រូបតំណាង (Emoji) តាមកម្រិតភាគរយឧស្សាហ៍របស់សិស្ស
                if rate >= 80: emoji = "🟢"
                elif rate >= 50: emoji = "🟡"
                else: emoji = "🔴"

                report_msg += (
                    f"{emoji} **ថ្នាក់៖ {c_level}**\n"
                    f" └ 📚 ចំនួនកិច្ចការដែលគ្រូដាក់៖ `{assigned}` មេរៀន\n"
                    f" └ 📥 អត្រាប្រគល់កិច្ចការ៖ `{actual}/{expected}` ដង\n"
                    f" └ 📊 ភាគរយសម្រេចបាន៖ **{rate:.1f}%**\n\n"
                )

            report_msg += (
                f"----------------------------------------\n"
                "💡 _កំណត់សម្គាល់៖_\n"
                "🟢 ឧស្សាហ៍ (>=80%) | 🟡 មធ្យម (50-79%) | 🔴 ខ្ជិល (<50%)"
            )

            bot.send_message(chat_id, report_msg, parse_mode='Markdown')

        except Exception as e:
            print(f"❌ HW Analytics Error: {e}")
            bot.send_message(chat_id, f"❌ **កំហុសបច្ចេកទេស៖** `{e}`", parse_mode='Markdown')
            
            
    
    
