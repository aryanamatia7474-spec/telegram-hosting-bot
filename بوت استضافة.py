#By @shllhoom
# ممنوع نشر الاداة بدون حقوقي 
# ممنوع بيع الاداة !!

import sys
import subprocess 
import os
import time
import random
import re
import json
import threading
import shutil
import telebot
from telebot import types
from datetime import datetime, timedelta
import requests

# تعريف الألوان
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
RESET = '\033[0m'
BOLD = '\033[1m'

# ========== شعار SHLHOM ==========
def show_shlhom_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{C}
============================================================
    ███████╗██╗  ██╗██╗  ██╗ ██████╗ ███╗   ███╗
    ██╔════╝██║  ██║██║  ██║██╔═══██╗████╗ ████║
    ███████╗███████║███████║██║   ██║██╔████╔██║
    ╚════██║██╔══██║██╔══██║██║   ██║██║╚██╔╝██║
    ███████║██║  ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║
    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝
============================================================
{RESET}""")
    print(f"{BOLD}{C}⚡ DevEuserer : {G}SHLHOM{RESET}")
    print(f"{BOLD}{C}🤖 Edition    : {G}HOSTING BOT{RESET}")
    print(f"{BOLD}{C}📢 Channel    : {G}@shllhom{RESET}")
    print(f"{BOLD}{C}👤 Developer  : {G}@shllhoom{RESET}")
    print(f"{C}============================================================{RESET}\n")

show_shlhom_banner()

# ========== التوكن والايدي ==========
BOT_TOKEN = "8962473963:AAFLjqjlqPWNN47J61emkTCxTDp3YkDlAw4"
OWNER_ID = 8247917300

print(f"{G}✅ Token: {BOT_TOKEN[:10]}...{RESET}")
print(f"{G}✅ Owner ID: {OWNER_ID}{RESET}\n")

# ========== إعداد البوت ==========
try:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True", timeout=5)
    print(f"{G}✅ Webhook deleted{RESET}")
except:
    pass

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
bot.delete_webhook()

# ========== المتغيرات ==========
RUNNING_DIR = os.path.join(os.getcwd(), 'active_bots')
LOGS_DIR = os.path.join(os.getcwd(), 'bot_logs')
BOTS_DIR = os.path.join(os.getcwd(), 'bots')

for d in [RUNNING_DIR, LOGS_DIR, BOTS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

active_processes = {}
bot_users = set()
admin_users = {OWNER_ID: "👑 المالك"}
pending_approvals = {}
restart_count = 0

# ========== دوال الاستضافة ==========
def start_bot(bot_id, user_id, file_content, filename):
    try:
        bot_dir = os.path.join(BOTS_DIR, f"bot_{bot_id}")
        if not os.path.exists(bot_dir):
            os.makedirs(bot_dir)
        
        file_path = os.path.join(bot_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        log_path = os.path.join(LOGS_DIR, f"{bot_id}.log")
        log_file = open(log_path, "a", encoding="utf-8")
        
        proc = subprocess.Popen(
            [sys.executable, "-u", file_path],
            stdout=log_file,
            stderr=log_file,
            cwd=bot_dir,
            start_new_session=True
        )
        
        active_processes[bot_id] = {
            'process': proc,
            'user_id': user_id,
            'filename': filename,
            'file_path': file_path,
            'bot_dir': bot_dir,
            'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'log_path': log_path
        }
        return True
    except Exception as e:
        print(f"Start error: {e}")
        return False

def stop_bot(bot_id):
    if bot_id in active_processes:
        proc = active_processes[bot_id]
        try:
            os.killpg(os.getpgid(proc['process'].pid), 9)
        except:
            try:
                proc['process'].terminate()
            except:
                pass
        del active_processes[bot_id]
        return True
    return False

def delete_bot(bot_id):
    if bot_id in active_processes:
        stop_bot(bot_id)
    
    if os.path.exists(os.path.join(BOTS_DIR, f"bot_{bot_id}")):
        try:
            shutil.rmtree(os.path.join(BOTS_DIR, f"bot_{bot_id}"))
        except:
            pass
    
    log_path = os.path.join(LOGS_DIR, f"{bot_id}.log")
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except:
            pass
    
    return True

def get_logs(bot_id, lines=40):
    log_path = os.path.join(LOGS_DIR, f"{bot_id}.log")
    try:
        if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                last = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(last)
        return "📝 لا توجد مخرجات"
    except:
        return "❌ خطأ في القراءة"

def validate_code(content):
    suspicious_patterns = [
        r'os\.system',
        r'subprocess\.',
        r'__import__',
        r'eval\(',
        r'exec\(',
        r'compile\(',
        r'globals\(\)',
        r'locals\(\)',
        r'getattr\(',
        r'setattr\(',
        r'delattr\(',
        r'__builtins__',
        r'open\(',
        r'file\(',
        r'input\(',
        r'raw_input\(',
    ]
    
    warnings = []
    for pattern in suspicious_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            warnings.append(f"⚠️ تم العثور على: `{pattern}`")
    
    return warnings

# ========== أزرار ذهبية وخضراء ==========
def main_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📤 رفع ملف", callback_data="upload"),
        types.InlineKeyboardButton("📁 ملفاتي", callback_data="my_bots")
    )
    kb.add(
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"),
        types.InlineKeyboardButton("💬 تواصل مع المبرمج", callback_data="contact_dev")
    )
    kb.add(
        types.InlineKeyboardButton("👑 المطور", url="https://t.me/shllhoom"),
        types.InlineKeyboardButton("📢 القناة", url="https://t.me/shllhom")
    )
    return kb

def admin_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users")
    )
    kb.add(
        types.InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("📁 كل البوتات", callback_data="admin_bots")
    )
    kb.add(
        types.InlineKeyboardButton("📋 طلبات الموافقة", callback_data="admin_approvals"),
        types.InlineKeyboardButton("🗑️ تنظيف", callback_data="admin_clean")
    )
    kb.add(
        types.InlineKeyboardButton("💬 تواصل مع المبرمج", callback_data="contact_dev"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return kb

def bot_control_kb(bot_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    if bot_id in active_processes:
        kb.add(types.InlineKeyboardButton("⏹️ إيقاف", callback_data=f"stop_{bot_id}"))
    else:
        kb.add(types.InlineKeyboardButton("▶️ تشغيل", callback_data=f"start_{bot_id}"))
    kb.add(types.InlineKeyboardButton("📟 سجلات", callback_data=f"logs_{bot_id}"))
    kb.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_{bot_id}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="my_bots"))
    return kb

def approval_kb(request_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{request_id}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{request_id}")
    )
    kb.add(types.InlineKeyboardButton("📄 عرض الملف", callback_data=f"view_file_{request_id}"))
    return kb

# ========== أوامر البوت ==========
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid = m.chat.id
    
    if uid not in bot_users:
        bot_users.add(uid)
    
    welcome = f"""👋 <b>مرحباً!</b>

🚀 <b>SHLHOM HOSTING BOT</b>

📤 ارفع ملف .py وسيتم استضافته
📁 شاهد ملفاتك وتحكم بها
💬 تواصل مع المبرمج لحل أي مشكلة

👑 @shllhoom"""
    
    if uid == OWNER_ID:
        bot.send_message(uid, welcome, parse_mode="HTML", reply_markup=admin_kb())
    else:
        bot.send_message(uid, welcome, parse_mode="HTML", reply_markup=main_kb())

@bot.message_handler(commands=['shlhom'])
def admin_cmd(m):
    uid = m.chat.id
    if uid != OWNER_ID:
        bot.send_message(uid, "❌ هذا الأمر للمطور فقط!", parse_mode="HTML")
        return
    
    welcome = f"""👋 <b>مرحباً أيها المالك!</b>

🚀 <b>SHLHOM HOSTING BOT</b>
⚙️ <b>لوحة التحكم الكاملة</b>

📊 <b>الإحصائيات</b> - عرض إحصائيات البوت
👥 <b>المستخدمين</b> - عرض قائمة المستخدمين
📢 <b>إذاعة</b> - إرسال رسالة للجميع
📁 <b>كل البوتات</b> - عرض جميع البوتات
📋 <b>طلبات الموافقة</b> - الموافقة على رفع البوتات
🗑️ <b>تنظيف</b> - حذف الملفات المؤقتة
💬 <b>تواصل مع المبرمج</b> - للدعم والمساعدة

👑 @shllhoom"""
    
    bot.send_message(uid, welcome, parse_mode="HTML", reply_markup=admin_kb())

@bot.message_handler(commands=['shlhom1'])
def restart_cmd(m):
    uid = m.chat.id
    if uid != OWNER_ID:
        bot.send_message(uid, "❌ هذا الأمر للمطور فقط!", parse_mode="HTML")
        return
    
    global restart_count
    restart_count += 1
    
    bot.send_message(uid, f"🔄 <b>جاري إعادة تشغيل البوت...</b>\n\n📊 عدد مرات إعادة التشغيل: {restart_count}", parse_mode="HTML")
    
    for bot_id in list(active_processes.keys()):
        try:
            stop_bot(bot_id)
        except:
            pass
    
    try:
        for f in os.listdir('.'):
            if f.startswith('temp_') or f.startswith('enc_'):
                try:
                    os.remove(f)
                except:
                    pass
    except:
        pass
    
    time.sleep(2)
    
    bot.send_message(uid, f"✅ <b>تم إعادة تشغيل البوت بنجاح!</b>\n\n🔄 عدد مرات إعادة التشغيل: {restart_count}\n\n👑 @shllhoom", parse_mode="HTML", reply_markup=admin_kb())

@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    uid = c.from_user.id
    data = c.data
    
    try:
        bot.answer_callback_query(c.id)
    except:
        pass
    
    # ====== التواصل مع المبرمج ======
    if data == "contact_dev":
        contact_text = f"""💬 <b>تواصل مع المبرمج</b>
━━━━━━━━━━━━━━━━━━━━━
👤 <b>المبرمج:</b> @shllhoom
📢 <b>القناة:</b> @shllhom

📌 <b>للتواصل:</b>
• اضغط على اسم المبرمج أعلاه
• أو ابحث عن @shllhoom في تيليجرام

🔹 <b>يمكنك التواصل لحل:</b>
• مشاكل في الاستضافة
• أعطال البوتات
• استفسارات عامة
• اقتراحات وتطوير

━━━━━━━━━━━━━━━━━━━━━
👑 @shllhoom"""
        
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("👤 المبرمج", url="https://t.me/shllhoom"))
        kb.add(types.InlineKeyboardButton("📢 القناة", url="https://t.me/shllhom"))
        kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        
        bot.edit_message_text(contact_text, c.message.chat.id, c.message.message_id, 
                            parse_mode="HTML", reply_markup=kb)
        return
    
    # ====== عرض الملف ======
    if data.startswith("view_file_"):
        req_id = data.replace("view_file_", "")
        if req_id not in pending_approvals:
            bot.edit_message_text("❌ الطلب غير موجود", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            return
        
        req = pending_approvals[req_id]
        
        file_content = req['content']
        file_name = req['filename']
        
        temp_file = f"temp_{req_id}.py"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        with open(temp_file, 'rb') as f:
            bot.send_document(uid, f, caption=f"📄 <b>ملف: {file_name}</b>\n👤 المستخدم: <code>{req['user_id']}</code>", parse_mode="HTML")
        
        try:
            os.remove(temp_file)
        except:
            pass
        
        warnings = validate_code(file_content)
        if warnings:
            warn_text = "🔍 <b>تحليل الكود:</b>\n" + "\n".join(warnings)
            bot.send_message(uid, warn_text, parse_mode="HTML")
        else:
            bot.send_message(uid, "✅ <b>الملف آمن</b> - لم يتم العثور على أنماط مشبوهة", parse_mode="HTML")
        
        bot.edit_message_text(f"📄 <b>تم إرسال الملف {req['filename']}</b>\n\nاستخدم الأزرار للموافقة أو الرفض", 
                            c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=approval_kb(req_id))
        return
    
    # ====== ملفاتي ======
    if data == "my_bots":
        user_bots = {bid: info for bid, info in active_processes.items() if info['user_id'] == uid}
        
        if not user_bots:
            bot.edit_message_text("📁 <b>لا توجد ملفات</b>\n\nقم برفع ملف .py للاستضافة", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=main_kb())
            return
        
        kb = types.InlineKeyboardMarkup(row_width=1)
        for bid, info in user_bots.items():
            status = "🟢" if bid in active_processes else "🔴"
            kb.add(types.InlineKeyboardButton(f"{status} {info['filename']}", callback_data=f"bot_{bid}"))
        kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        
        bot.edit_message_text("📁 <b>ملفاتي</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb)
        return
    
    if data.startswith("bot_"):
        bot_id = data.replace("bot_", "")
        if bot_id not in active_processes:
            bot.edit_message_text("❌ البوت غير موجود", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=main_kb())
            return
        
        info = active_processes[bot_id]
        status = "🟢 يعمل" if bot_id in active_processes else "🔴 متوقف"
        msg = f"""📄 <b>{info['filename']}</b>
━━━━━━━━━━━━━━━━━━━━━
🆔 <b>المعرف:</b> {bot_id}
📊 <b>الحالة:</b> {status}
📅 <b>التشغيل:</b> {info['start_time']}
━━━━━━━━━━━━━━━━━━━━━
👑 @shllhoom"""
        
        bot.edit_message_text(msg, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=bot_control_kb(bot_id))
        return
    
    # ====== التحكم بالبوت ======
    if data.startswith("stop_"):
        bot_id = data.replace("stop_", "")
        if stop_bot(bot_id):
            bot.answer_callback_query(c.id, "✅ تم الإيقاف")
        else:
            bot.answer_callback_query(c.id, "❌ فشل", True)
        callback_restart = types.CallbackQuery()
        callback_restart.id = c.id
        callback_restart.message = c.message
        callback_restart.data = f"bot_{bot_id}"
        callback_restart.from_user = c.from_user
        callback(callback_restart)
        return
    
    if data.startswith("start_"):
        bot_id = data.replace("start_", "")
        if bot_id in active_processes:
            info = active_processes[bot_id]
            stop_bot(bot_id)
            time.sleep(0.5)
            with open(info['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            if start_bot(bot_id, info['user_id'], content, info['filename']):
                bot.answer_callback_query(c.id, "✅ تم التشغيل")
            else:
                bot.answer_callback_query(c.id, "❌ فشل", True)
        callback_restart = types.CallbackQuery()
        callback_restart.id = c.id
        callback_restart.message = c.message
        callback_restart.data = f"bot_{bot_id}"
        callback_restart.from_user = c.from_user
        callback(callback_restart)
        return
    
    if data.startswith("logs_"):
        bot_id = data.replace("logs_", "")
        logs = get_logs(bot_id)
        bot.edit_message_text(f"📟 <b>سجلات البوت</b>\n━━━━━━━━━━━━━━━━━━━━━\n<code>{logs[:3000]}</code>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=bot_control_kb(bot_id))
        return
    
    if data.startswith("delete_"):
        bot_id = data.replace("delete_", "")
        if delete_bot(bot_id):
            bot.answer_callback_query(c.id, "🗑️ تم الحذف")
            bot.edit_message_text("🗑️ <b>تم حذف البوت</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=main_kb())
        else:
            bot.answer_callback_query(c.id, "❌ فشل", True)
        return
    
    # ====== رفع ملف ======
    if data == "upload":
        msg = bot.send_message(uid, "📤 <b>أرسل ملف .py للاستضافة</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, upload_step)
        return
    
    # ====== إحصائيات ======
    if data == "stats":
        stats = f"""📊 <b>إحصائيات البوت</b>
━━━━━━━━━━━━━━━━━━━━━
👥 <b>المستخدمين:</b> {len(bot_users)}
🟢 <b>البوتات العاملة:</b> {len(active_processes)}
🔄 <b>إعادة التشغيل:</b> {restart_count}
━━━━━━━━━━━━━━━━━━━━━
👑 @shllhoom"""
        bot.edit_message_text(stats, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=main_kb())
        return
    
    # ====== رجوع ======
    if data == "back_main":
        if uid == OWNER_ID:
            welcome = f"""👋 <b>مرحباً أيها المالك!</b>

🚀 <b>SHLHOM HOSTING BOT</b>
⚙️ <b>لوحة التحكم</b>

👑 @shllhoom"""
            bot.edit_message_text(welcome, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
        else:
            welcome = f"""👋 <b>مرحباً!</b>

🚀 <b>SHLHOM HOSTING BOT</b>

📤 ارفع ملف .py وسيتم استضافته
📁 شاهد ملفاتك وتحكم بها
💬 تواصل مع المبرمج لحل أي مشكلة

👑 @shllhoom"""
            bot.edit_message_text(welcome, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=main_kb())
        return
    
    # ====== أوامر الأدمن ======
    if uid == OWNER_ID:
        if data == "admin_approvals":
            if not pending_approvals:
                bot.edit_message_text("📋 <b>لا توجد طلبات موافقة</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
                return
            
            kb = types.InlineKeyboardMarkup(row_width=1)
            for req_id, req in pending_approvals.items():
                kb.add(types.InlineKeyboardButton(
                    f"📄 {req['filename']} - {req['user_id']}", 
                    callback_data=f"view_req_{req_id}"
                ))
            kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
            
            bot.edit_message_text("📋 <b>طلبات الموافقة</b>\n\nاختر طلباً للموافقة أو الرفض:", 
                                c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb)
            return
        
        if data.startswith("view_req_"):
            req_id = data.replace("view_req_", "")
            if req_id not in pending_approvals:
                bot.edit_message_text("❌ الطلب غير موجود", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
                return
            
            req = pending_approvals[req_id]
            
            msg = f"""📄 <b>طلب استضافة بوت</b>
━━━━━━━━━━━━━━━━━━━━━
📁 <b>اسم الملف:</b> {req['filename']}
👤 <b>المستخدم:</b> <code>{req['user_id']}</code>
⏱️ <b>وقت الطلب:</b> {req['time']}
📊 <b>حجم الملف:</b> {req['size']} bytes
━━━━━━━━━━━━━━━━━━━━━
<b>محتوى الملف (أول 300 حرف):</b>
<code>{req['content'][:300]}...</code>
━━━━━━━━━━━━━━━━━━━━━
👑 @shllhoom"""
            
            bot.edit_message_text(msg, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=approval_kb(req_id))
            return
        
        if data.startswith("approve_"):
            req_id = data.replace("approve_", "")
            if req_id not in pending_approvals:
                bot.edit_message_text("❌ الطلب غير موجود", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
                return
            
            req = pending_approvals[req_id]
            req_id2 = req['bot_id']
            
            if start_bot(req_id2, req['user_id'], req['content'], req['filename']):
                bot.send_message(req['user_id'], f"✅ <b>تمت الموافقة على استضافة البوت!</b>\n\n📄 {req['filename']}\n🆔 {req_id2}\n\n🔹 يمكنك التحكم به من قائمة ملفاتي", parse_mode="HTML")
                bot.edit_message_text(f"✅ <b>تمت الموافقة على طلب {req['filename']}</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            else:
                bot.send_message(req['user_id'], "❌ <b>فشل في استضافة البوت</b>", parse_mode="HTML")
                bot.edit_message_text(f"❌ <b>فشل في تشغيل {req['filename']}</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            
            del pending_approvals[req_id]
            return
        
        if data.startswith("reject_"):
            req_id = data.replace("reject_", "")
            if req_id not in pending_approvals:
                bot.edit_message_text("❌ الطلب غير موجود", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
                return
            
            req = pending_approvals[req_id]
            bot.send_message(req['user_id'], f"❌ <b>تم رفض طلب استضافة {req['filename']}</b>\n\nيرجى التواصل مع المبرمج @shllhoom للمزيد من المعلومات", parse_mode="HTML")
            bot.edit_message_text(f"❌ <b>تم رفض طلب {req['filename']}</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            del pending_approvals[req_id]
            return
        
        if data == "admin_stats":
            stats = f"""📊 <b>إحصائيات البوت</b>
━━━━━━━━━━━━━━━━━━━━━
👥 <b>المستخدمين:</b> {len(bot_users)}
🟢 <b>البوتات العاملة:</b> {len(active_processes)}
👑 <b>الأدمن:</b> {len(admin_users)}
📋 <b>طلبات الموافقة:</b> {len(pending_approvals)}
🔄 <b>إعادة التشغيل:</b> {restart_count}
━━━━━━━━━━━━━━━━━━━━━
👑 @shllhoom"""
            bot.edit_message_text(stats, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            return
        
        if data == "admin_users":
            users_list = "👥 <b>قائمة المستخدمين</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            for uid in list(bot_users)[:20]:
                try:
                    user = bot.get_chat(uid)
                    users_list += f"👤 {user.first_name} - <code>{uid}</code>\n"
                except:
                    users_list += f"👤 <code>{uid}</code>\n"
            if len(bot_users) > 20:
                users_list += f"\n... و {len(bot_users)-20} مستخدم"
            users_list += "\n━━━━━━━━━━━━━━━━━━━━━\n👑 @shllhoom"
            bot.edit_message_text(users_list, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            return
        
        if data == "admin_broadcast":
            msg = bot.send_message(uid, "📢 <b>أرسل رسالتك للإذاعة</b>", parse_mode="HTML")
            bot.register_next_step_handler(msg, broadcast_step)
            return
        
        if data == "admin_bots":
            if not active_processes:
                bot.edit_message_text("📁 <b>لا توجد بوتات</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
                return
            
            kb = types.InlineKeyboardMarkup(row_width=1)
            for bid, info in list(active_processes.items())[:20]:
                status = "🟢" if bid in active_processes else "🔴"
                kb.add(types.InlineKeyboardButton(f"{status} {info['filename']} - {info['user_id']}", callback_data=f"abot_{bid}"))
            kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
            
            bot.edit_message_text("📁 <b>جميع البوتات</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb)
            return
        
        if data.startswith("abot_"):
            bot_id = data.replace("abot_", "")
            if bot_id not in active_processes:
                bot.edit_message_text("❌ البوت غير موجود", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
                return
            
            info = active_processes[bot_id]
            status = "🟢 يعمل" if bot_id in active_processes else "🔴 متوقف"
            msg = f"""📄 <b>{info['filename']}</b>
━━━━━━━━━━━━━━━━━━━━━
🆔 <b>المعرف:</b> {bot_id}
👤 <b>المستخدم:</b> <code>{info['user_id']}</code>
📊 <b>الحالة:</b> {status}
📅 <b>التشغيل:</b> {info['start_time']}
━━━━━━━━━━━━━━━━━━━━━
👑 @shllhoom"""
            
            kb = types.InlineKeyboardMarkup(row_width=2)
            if bot_id in active_processes:
                kb.add(types.InlineKeyboardButton("⏹️ إيقاف", callback_data=f"astop_{bot_id}"))
            else:
                kb.add(types.InlineKeyboardButton("▶️ تشغيل", callback_data=f"astart_{bot_id}"))
            kb.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"adelete_{bot_id}"))
            kb.add(types.InlineKeyboardButton("📟 سجلات", callback_data=f"alogs_{bot_id}"))
            kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_bots"))
            
            bot.edit_message_text(msg, c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb)
            return
        
        if data.startswith("astop_"):
            bot_id = data.replace("astop_", "")
            stop_bot(bot_id)
            bot.answer_callback_query(c.id, "✅ تم الإيقاف")
            callback_restart = types.CallbackQuery()
            callback_restart.id = c.id
            callback_restart.message = c.message
            callback_restart.data = f"abot_{bot_id}"
            callback_restart.from_user = c.from_user
            callback(callback_restart)
            return
        
        if data.startswith("astart_"):
            bot_id = data.replace("astart_", "")
            if bot_id in active_processes:
                info = active_processes[bot_id]
                stop_bot(bot_id)
                time.sleep(0.5)
                with open(info['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                start_bot(bot_id, info['user_id'], content, info['filename'])
            bot.answer_callback_query(c.id, "✅ تم التشغيل")
            callback_restart = types.CallbackQuery()
            callback_restart.id = c.id
            callback_restart.message = c.message
            callback_restart.data = f"abot_{bot_id}"
            callback_restart.from_user = c.from_user
            callback(callback_restart)
            return
        
        if data.startswith("adelete_"):
            bot_id = data.replace("adelete_", "")
            delete_bot(bot_id)
            bot.answer_callback_query(c.id, "🗑️ تم الحذف")
            bot.edit_message_text("🗑️ <b>تم حذف البوت</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            return
        
        if data.startswith("alogs_"):
            bot_id = data.replace("alogs_", "")
            logs = get_logs(bot_id)
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data=f"abot_{bot_id}"))
            bot.edit_message_text(f"📟 <b>سجلات البوت</b>\n━━━━━━━━━━━━━━━━━━━━━\n<code>{logs[:3000]}</code>", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=kb)
            return
        
        if data == "admin_clean":
            bot.edit_message_text("🗑️ <b>جاري التنظيف...</b>", c.message.chat.id, c.message.message_id, parse_mode="HTML")
            cleaned = 0
            for f in os.listdir('.'):
                if f.startswith('temp_') or f.startswith('enc_') or f.startswith('bot_'):
                    try:
                        os.remove(f)
                        cleaned += 1
                    except:
                        pass
            bot.edit_message_text(f"✅ <b>تم التنظيف!</b>\n🗑️ تم حذف {cleaned} ملف", c.message.chat.id, c.message.message_id, parse_mode="HTML", reply_markup=admin_kb())
            return

def upload_step(m):
    uid = m.chat.id
    
    if not m.document or not m.document.file_name.endswith('.py'):
        bot.send_message(uid, "❌ الرجاء إرسال ملف .py", parse_mode="HTML", reply_markup=main_kb())
        return
    
    try:
        file_info = bot.get_file(m.document.file_id)
        content = bot.download_file(file_info.file_path).decode('utf-8')
        
        bot_id = f"bot_{int(time.time())}_{random.randint(100,999)}"
        
        request_id = f"req_{int(time.time())}_{random.randint(100,999)}"
        pending_approvals[request_id] = {
            'user_id': uid,
            'filename': m.document.file_name,
            'content': content,
            'bot_id': bot_id,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'size': len(content)
        }
        
        dev_msg = f"""📋 <b>طلب استضافة جديد</b>
━━━━━━━━━━━━━━━━━━━━━
📁 <b>اسم الملف:</b> {m.document.file_name}
👤 <b>المستخدم:</b> <code>{uid}</code>
⏱️ <b>الوقت:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📊 <b>حجم الملف:</b> {len(content)} bytes
━━━━━━━━━━━━━━━━━━━━━
⚠️ <b>يحتاج موافقتك لتشغيل البوت</b>
👑 @shllhoom"""
        
        bot.send_message(OWNER_ID, dev_msg, parse_mode="HTML", reply_markup=approval_kb(request_id))
        
        bot.send_message(uid, f"📤 <b>تم رفع الملف بنجاح!</b>\n\n📄 {m.document.file_name}\n⏳ جاري انتظار موافقة المطور على الاستضافة...\n\n🔹 سيتم إعلامك عند الموافقة", parse_mode="HTML", reply_markup=main_kb())
        
    except Exception as e:
        bot.send_message(uid, f"❌ خطأ: {str(e)}", parse_mode="HTML", reply_markup=main_kb())

def broadcast_step(m):
    uid = m.chat.id
    if uid != OWNER_ID:
        return
    
    text = m.text
    success = 0
    failed = 0
    
    status = bot.send_message(uid, f"⏳ جاري الإرسال لـ {len(bot_users)} مستخدم...")
    
    for user_id in list(bot_users):
        try:
            bot.send_message(user_id, text, parse_mode="HTML")
            success += 1
            time.sleep(0.02)
        except:
            failed += 1
    
    bot.edit_message_text(f"✅ تم الإرسال\n\n✅ نجح: {success}\n❌ فشل: {failed}", uid, status.message_id, parse_mode="HTML", reply_markup=admin_kb())

# ========== مراقبة البوتات ==========
def monitor_bots():
    while True:
        try:
            for bot_id in list(active_processes.keys()):
                proc = active_processes[bot_id]
                if proc['process'].poll() is not None:
                    del active_processes[bot_id]
        except:
            pass
        time.sleep(10)

monitor_thread = threading.Thread(target=monitor_bots, daemon=True)
monitor_thread.start()

# ========== تشغيل البوت ==========
print(f"{G}✅ Bot is running...{RESET}")
print(f"{G}📢 Send /start on Telegram{RESET}")
print(f"{G}🔑 Owner ID: {OWNER_ID}{RESET}")
print(f"{G}📁 Hosting Bot is ready!{RESET}")
print(f"{G}📋 Approval system with file preview enabled{RESET}")
print(f"{G}🔄 Restart command: /shlhom1{RESET}\n")

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"{R}❌ Error: {e}{RESET}")
        time.sleep(3)