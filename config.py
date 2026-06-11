import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv() # 👈 ថែមជួរនេះ ដើម្បីអាន Key ពីកុំព្យូទ័រ
# 🔐 ទាញយក Token និង API Keys ពី Environment Variable លើ Render
# 🌐 ទាញយក Token ពី File .env មកប្រើអូតូ
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_PASSWORD_KEY = "DUC_Admin@2026"

# 🔗 បង្កើត Supabase API Client រួមមួយសម្រាប់គម្រោងទាំងមូល
if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ ព្រមាន៖ មិនទាន់មាន SUPABASE_URL ឬ SUPABASE_KEY ក្នុង Environment ឡើយ!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# បង្កើត Folder សម្រាប់ផ្ទុកឯកសារបណ្ដោះអាសន្នលើ Server
for folder in ['uploads', 'student_assignments']:
    if not os.path.exists(folder):
        os.makedirs(folder)