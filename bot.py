#!/usr/bin/env python3
# ============================================
#   🦅 XINN PANEL — Premium Telegram Bot
#   Jual Panel Hosting Otomatis
#   🏦 Dana: 083175050030
#   Created by BARR — 2060
# ============================================

import os, json, random, string, datetime
from telethon import TelegramClient, events, Button

# ============ CONFIG (AMAN - DIAMBIL DARI ENV) ============
API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_IDS = [int(os.environ.get('ADMIN_ID', '7562630960'))]
DANA_NUMBER = "083175050030"
PANEL_URL = "https://panel.xinnstore.my.id"

DB_FILE = 'xinn_db.json'

# ============ DATABASE ============
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f: return json.load(f)
    return {
        "users": {},
        "orders": [],
        "stats": {"total_revenue": 0, "total_accounts": 0},
        "settings": {
            "panel_name": "🦅 XINN PANEL",
            "panel_url": PANEL_URL,
            "price_weekly": 5000,
            "price_monthly": 15000,
            "price_vip": 50000,
            "dana": DANA_NUMBER,
            "admin_username": "@xinn_admin"
        }
    }

def save_db(db):
    with open(DB_FILE, 'w') as f: json.dump(db, f, indent=2)

def gen_user(): return 'xinn_' + ''.join(random.choice(string.digits) for _ in range(6))
def gen_pass(): return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
def rp(n): return f"Rp {n:,}".replace(',', '.')
def is_expired(d): 
    if not d: return True
    return datetime.datetime.now() > datetime.datetime.strptime(d, '%Y-%m-%d')

# ============ BOT INIT ============
bot = TelegramClient('xinn_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ============ KEYBOARDS ============
def main_menu(user_id):
    db = load_db()
    user = db['users'].get(str(user_id), {'balance': 0, 'accounts': []})
    active = len([a for a in user['accounts'] if not is_expired(a.get('expired',''))])
    return [
        [Button.inline("🛒 BELI PANEL HOSTING", b"buy")],
        [Button.inline("📋 AKUN SAYA", b"accounts"), Button.inline("💸 TOPUP SALDO", b"topup")],
        [Button.inline("📊 STATUS AKUN", b"status"), Button.inline("🎁 PROMO", b"promo")],
        [Button.inline("ℹ️ BANTUAN", b"help"), Button.inline("📞 ADMIN", b"admin")],
    ]

def buy_menu():
    db = load_db()
    return [
        [Button.inline(f"📅 MINGGUAN — {rp(db['settings']['price_weekly'])}", b"buy_weekly")],
        [Button.inline(f"📅 BULANAN — {rp(db['settings']['price_monthly'])}", b"buy_monthly")],
        [Button.inline(f"👑 VIP 3 BULAN — {rp(db['settings']['price_vip'])}", b"buy_vip")],
        [Button.inline("🔙 KEMBALI", b"back")]
    ]

def back_btn():
    return [[Button.inline("🔙 KEMBALI KE MENU", b"back")]]

# ============ COMMANDS ============
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = str(event.sender_id)
    db = load_db()
    if user_id not in db['users']:
        db['users'][user_id] = {
            'balance': 0, 'accounts': [],
            'joined': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'name': event.sender.first_name or 'User'
        }
        save_db(db)
    user = db['users'][user_id]
    active = len([a for a in user['accounts'] if not is_expired(a.get('expired',''))])
    welcome = (
        f"**╔══════════════════════════════════╗**\n"
        f"**║      🦅 XINN PANEL 🦅        ║**\n"
        f"**║   Premium Bot Hosting          ║**\n"
        f"**╚══════════════════════════════════╝**\n\n"
        f"🆔 **ID:** `{user_id}`\n"
        f"👤 **Nama:** {user['name']}\n"
        f"💎 **Role:** {'👑 VIP' if active > 0 else '🆓 FREE'}\n"
        f"💰 **Saldo:** {rp(user['balance'])}\n"
        f"📦 **Akun Aktif:** `{active}`\n\n"
        f"🏦 **Dana:** `{DANA_NUMBER}`\n\n"
        f"🔥 **Pilih menu di bawah:**"
    )
    await event.respond(welcome, buttons=main_menu(user_id))

# ============ CALLBACKS ============
@bot.on(events.CallbackQuery())
async def callback_handler(event):
    data = event.data.decode()
    user_id = str(event.sender_id)
    db = load_db()
    user = db['users'].get(user_id, {'balance': 0, 'accounts': [], 'name': 'User'})
    
    if data == "buy":
        text = f"**🛒 BELI PANEL HOSTING**\n\n🏦 **Dana:** `{DANA_NUMBER}`\n\n💎 **Pilih Paket:**\n▸ 📅 Mingguan — {rp(db['settings']['price_weekly'])}\n▸ 📅 Bulanan — {rp(db['settings']['price_monthly'])}\n▸ 👑 VIP 3 Bulan — {rp(db['settings']['price_vip'])}\n\n💰 **Saldo Lo:** {rp(user['balance'])}"
        await event.edit(text, buttons=buy_menu())
    
    elif data in ["buy_weekly", "buy_monthly", "buy_vip"]:
        pkg = {"buy_weekly": ("weekly", 7, db['settings']['price_weekly']),
               "buy_monthly": ("monthly", 30, db['settings']['price_monthly']),
               "buy_vip": ("vip", 90, db['settings']['price_vip'])}
        t, d, p = pkg[data]
        if user['balance'] < p:
            await event.edit(f"**❌ SALDO KURANG!**\n💰 Butuh: **{rp(p)}**\n💸 Saldo: **{rp(user['balance'])}**\n\n🏦 Topup: `{DANA_NUMBER}`", buttons=[[Button.inline("💸 TOPUP", b"topup")], [Button.inline("🔙 KEMBALI", b"back")]])
            return
        db['users'][user_id]['balance'] -= p
        db['stats']['total_revenue'] += p
        db['stats']['total_accounts'] += 1
        u = gen_user(); pw = gen_pass()
        exp = (datetime.datetime.now() + datetime.timedelta(days=d)).strftime('%Y-%m-%d')
        db['users'][user_id]['accounts'].append({'username': u, 'password': pw, 'created': datetime.datetime.now().strftime('%Y-%m-%d'), 'expired': exp, 'type': t})
        save_db(db)
        await event.edit(f"**✅ PEMBELIAN BERHASIL!**\n\n🎉 **{t.upper()}** — {d} Hari\n\n🔗 **Panel:** `{PANEL_URL}`\n👤 **Username:** `{u}`\n🔑 **Password:** `{pw}`\n📅 **Expired:** `{exp}`\n💰 **Sisa Saldo:** {rp(db['users'][user_id]['balance'])}\n\n⚠️ **SIMPAN DATA INI!**", buttons=back_btn())
    
    elif data == "accounts":
        accs = user['accounts']
        if not accs: await event.edit("📋 **Belum punya akun.**\n\nBeli dulu ya, Bos!", buttons=back_btn()); return
        text = "**📋 DAFTAR AKUN LO**\n\n"
        for i, a in enumerate(accs, 1):
            s = '🟢 AKTIF' if not is_expired(a.get('expired','')) else '🔴 EXPIRED'
            text += f"**{i}.** 👤 `{a['username']}` | 🔑 `{a['password']}`\n    📅 Exp: `{a.get('expired','?')}` | {s}\n\n"
        await event.edit(text, buttons=back_btn())
    
    elif data == "topup":
        await event.edit(f"**💸 TOPUP SALDO**\n\n🏦 **DANA:** `{DANA_NUMBER}`\n👤 **A/N:** XINN STORE\n\n📝 **Cara:**\n1. Transfer ke Dana di atas\n2. Kirim bukti ke @xinn_admin\n3. Admin konfirmasi\n\n💰 **Rate:** Rp 1.000 = 1.000 Saldo", buttons=[[Button.url("📞 ADMIN", "https://t.me/xinn_admin")], [Button.inline("🔙 KEMBALI", b"back")]])
    
    elif data == "status":
        active = len([a for a in user['accounts'] if not is_expired(a.get('expired',''))])
        total = len(user['accounts'])
        bar = '▓' * min(active, 10) + '░' * (10 - min(active, 10))
        await event.edit(f"**📊 STATUS AKUN LO**\n\n👤 **Nama:** {user['name']}\n🆔 **ID:** `{user_id}`\n💎 **Role:** {'👑 VIP' if active > 0 else '🆓 FREE'}\n💰 **Saldo:** {rp(user['balance'])}\n\n📦 **Akun:** [{bar}] {active}/{total}\n✅ **Aktif:** `{active}` | 🔴 **Expired:** `{total - active}`", buttons=back_btn())
    
    elif data == "promo":
        await event.edit(f"**🎁 PROMO SPESIAL**\n\n🔥 **BULAN INI:**\n▸ Beli 2 Bulan GRATIS 1 Minggu\n▸ Beli VIP dapet PREMIUM\n▸ Referral dapet Rp 2.000\n\n🏦 **Dana:** `{DANA_NUMBER}`", buttons=back_btn())
    
    elif data == "help":
        await event.edit(f"**ℹ️ BANTUAN**\n\n**Cara Beli:**\n1. Topup ke Dana `{DANA_NUMBER}`\n2. Konfirmasi ke admin\n3. Pilih paket di BELI\n4. Akun otomatis dibuat!\n\n📞 Butuh bantuan? Klik ADMIN", buttons=back_btn())
    
    elif data == "admin":
        await event.edit(f"**📞 HUBUNGI ADMIN**\n\n👤 Telegram: @xinn_admin\n📱 WhatsApp: {DANA_NUMBER}\n🏦 Dana: `{DANA_NUMBER}`\n🕐 Aktif: 08:00 - 22:00 WIB", buttons=[[Button.url("💬 CHAT ADMIN", "https://t.me/xinn_admin")], [Button.inline("🔙 KEMBALI", b"back")]])
    
    elif data == "back":
        active = len([a for a in user['accounts'] if not is_expired(a.get('expired',''))])
        await event.edit(f"**╔══════════════════════════════════╗**\n**║      🦅 XINN PANEL 🦅        ║**\n**║   Premium Bot Hosting          ║**\n**╚══════════════════════════════════╝**\n\n🆔 **ID:** `{user_id}`\n👤 **Nama:** {user['name']}\n💎 **Role:** {'👑 VIP' if active > 0 else '🆓 FREE'}\n💰 **Saldo:** {rp(user['balance'])}\n📦 **Akun Aktif:** `{active}`\n\n🏦 **Dana:** `{DANA_NUMBER}`\n\n🔥 **Pilih menu:**", buttons=main_menu(user_id))

# ============ START ============
print("🦅 XINN PANEL — READY | Dana: 083175050030")
bot.run_until_disconnected()
