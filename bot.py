#!/usr/bin/env python3
# ============================================
#   🦅 XINN PANEL — Premium Telegram Bot
#   Jual Panel Hosting Otomatis
#   🏦 Dana: 083175050030
#   Created by BARR — 2060
# ============================================

import os, json, random, string, datetime, asyncio
from telethon import TelegramClient, events, Button

# ============ CONFIG ============
API_ID = int(os.environ.get('API_ID', '34605949'))
API_HASH = os.environ.get('API_HASH', 'a2a5059020c873e72bdb14d61e6b69e0')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8765474262:AAGf8-xBfp0s4bPTduMD3jk_j1G-tG8awRY')
ADMIN_IDS = [7562630960]
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
bot = TelegramClient('xinn_panel_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

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

# ============ BOT COMMANDS ============
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = str(event.sender_id)
    db = load_db()
    
    if user_id not in db['users']:
        db['users'][user_id] = {
            'balance': 0,
            'accounts': [],
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

@bot.on(events.NewMessage(pattern='/admin'))
async def admin_cmd(event):
    if event.sender_id not in ADMIN_IDS: return
    
    db = load_db()
    total_users = len(db['users'])
    total_active = sum(1 for u in db['users'].values() for a in u['accounts'] if not is_expired(a.get('expired','')))
    total_rev = db['stats']['total_revenue']
    
    text = (
        f"**🔐 ADMIN PANEL**\n\n"
        f"👥 Total User: `{total_users}`\n"
        f"✅ Akun Aktif: `{total_active}`\n"
        f"💰 Total Cuan: `{rp(total_rev)}`\n"
        f"🏦 Dana: `{DANA_NUMBER}`\n"
    )
    
    buttons = [
        [Button.inline("📊 STATISTIK", b"admin_stats")],
        [Button.inline("🔙 KEMBALI", b"back")]
    ]
    
    await event.respond(text, buttons=buttons)

# ============ CALLBACK HANDLER ============
@bot.on(events.CallbackQuery())
async def callback_handler(event):
    data = event.data.decode()
    user_id = str(event.sender_id)
    db = load_db()
    user = db['users'].get(user_id, {'balance': 0, 'accounts': [], 'name': 'User'})
    
    try:
        if data == "buy":
            text = (
                f"**🛒 BELI PANEL HOSTING**\n\n"
                f"🏦 **Dana:** `{DANA_NUMBER}`\n\n"
                f"💎 **Pilih Paket:**\n"
                f"▸ 📅 Mingguan — {rp(db['settings']['price_weekly'])}\n"
                f"▸ 📅 Bulanan — {rp(db['settings']['price_monthly'])}\n"
                f"▸ 👑 VIP 3 Bulan — {rp(db['settings']['price_vip'])}\n\n"
                f"💰 **Saldo Lo:** {rp(user['balance'])}"
            )
            await event.edit(text, buttons=buy_menu())
        
        elif data in ["buy_weekly", "buy_monthly", "buy_vip"]:
            pkg_map = {"buy_weekly": ("weekly", 7, db['settings']['price_weekly']),
                       "buy_monthly": ("monthly", 30, db['settings']['price_monthly']),
                       "buy_vip": ("vip", 90, db['settings']['price_vip'])}
            pkg_type, days, price = pkg_map[data]
            
            if user['balance'] < price:
                text = f"**❌ SALDO KURANG!**\n\n💰 Butuh: **{rp(price)}**\n💸 Saldo: **{rp(user['balance'])}**\n\n🏦 Topup ke Dana: `{DANA_NUMBER}`"
                await event.edit(text, buttons=[[Button.inline("💸 TOPUP SEKARANG", b"topup")], [Button.inline("🔙 KEMBALI", b"back")]])
                return
            
            db['users'][user_id]['balance'] -= price
            db['stats']['total_revenue'] += price
            db['stats']['total_accounts'] += 1
            
            username = gen_user()
            password = gen_pass()
            expired = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            
            db['users'][user_id]['accounts'].append({
                'username': username, 'password': password,
                'created': datetime.datetime.now().strftime('%Y-%m-%d'),
                'expired': expired, 'type': pkg_type
            })
            db['orders'].append({'user': user_id, 'type': pkg_type, 'amount': price, 'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            save_db(db)
            
            text = (
                f"**✅ PEMBELIAN BERHASIL!**\n\n"
                f"🎉 **{pkg_type.upper()}** — {days} Hari\n\n"
                f"🔗 **Panel:** `{PANEL_URL}`\n"
                f"👤 **Username:** `{username}`\n"
                f"🔑 **Password:** `{password}`\n"
                f"📅 **Expired:** `{expired}`\n"
                f"💰 **Sisa Saldo:** {rp(db['users'][user_id]['balance'])}\n\n"
                f"⚠️ **SIMPAN DATA INI!**"
            )
            await event.edit(text, buttons=back_btn())
        
        elif data == "accounts":
            accounts = user['accounts']
            if not accounts:
                await event.edit("📋 **Belum punya akun.**\n\nBeli dulu ya, Bos!", buttons=back_btn())
                return
            text = "**📋 DAFTAR AKUN LO**\n\n"
            for i, acc in enumerate(accounts, 1):
                status = '🟢 AKTIF' if not is_expired(acc.get('expired','')) else '🔴 EXPIRED'
                text += f"**{i}.** 👤 `{acc['username']}` | 🔑 `{acc['password']}`\n    📅 Exp: `{acc.get('expired','?')}` | {status}\n\n"
            await event.edit(text, buttons=back_btn())
        
        elif data == "topup":
            text = (
                f"**💸 TOPUP SALDO**\n\n"
                f"🏦 **DANA:** `{DANA_NUMBER}`\n"
                f"👤 **A/N:** XINN STORE\n\n"
                f"📝 **Cara Topup:**\n"
                f"1. Transfer ke nomor Dana di atas\n"
                f"2. Kirim bukti ke @xinn_admin\n"
                f"3. Admin konfirmasi manual\n"
                f"4. Saldo otomatis nambah\n\n"
                f"💰 **Rate:** Rp 1.000 = 1.000 Saldo"
            )
            await event.edit(text, buttons=[[Button.url("📞 HUBUNGI ADMIN", "https://t.me/xinn_admin")], [Button.inline("🔙 KEMBALI", b"back")]])
        
        elif data == "status":
            active = len([a for a in user['accounts'] if not is_expired(a.get('expired',''))])
            total = len(user['accounts'])
            bar = '▓' * min(active, 10) + '░' * (10 - min(active, 10))
            text = (
                f"**📊 STATUS AKUN LO**\n\n"
                f"👤 **Nama:** {user['name']}\n"
                f"🆔 **ID:** `{user_id}`\n"
                f"💎 **Role:** {'👑 VIP' if active > 0 else '🆓 FREE'}\n"
                f"💰 **Saldo:** {rp(user['balance'])}\n\n"
                f"📦 **Akun:** [{bar}] {active}/{total}\n"
                f"✅ **Aktif:** `{active}` | 🔴 **Expired:** `{total - active}`"
            )
            await event.edit(text, buttons=back_btn())
        
        elif data == "promo":
            text = f"**🎁 PROMO SPESIAL**\n\n🔥 **BULAN INI:**\n▸ Beli 2 Bulan GRATIS 1 Minggu\n▸ Beli VIP dapet akses PREMIUM\n▸ Referral dapet saldo Rp 2.000\n\n🏦 **Dana:** `{DANA_NUMBER}`"
            await event.edit(text, buttons=back_btn())
        
        elif data == "help":
            text = f"**ℹ️ BANTUAN XINN PANEL**\n\n**Cara Beli Panel:**\n1. Topup ke Dana `{DANA_NUMBER}`\n2. Konfirmasi ke admin\n3. Pilih paket di menu BELI\n4. Akun otomatis dibuat!\n\n📞 Butuh bantuan? Klik ADMIN"
            await event.edit(text, buttons=back_btn())
        
        elif data == "admin":
            await event.edit(
                f"**📞 HUBUNGI ADMIN**\n\n👤 Telegram: @xinn_admin\n📱 WhatsApp: {DANA_NUMBER}\n🏦 Dana: `{DANA_NUMBER}`\n🕐 Aktif: 08:00 - 22:00 WIB",
                buttons=[[Button.url("💬 CHAT ADMIN", "https://t.me/xinn_admin")], [Button.inline("🔙 KEMBALI", b"back")]]
            )
        
        elif data == "back":
            active = len([a for a in user['accounts'] if not is_expired(a.get('expired',''))])
            text = (
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
            await event.edit(text, buttons=main_menu(user_id))
        
        elif data == "admin_stats":
            total_users = len(db['users'])
            total_active = sum(1 for u in db['users'].values() for a in u['accounts'] if not is_expired(a.get('expired','')))
            total_rev = db['stats']['total_revenue']
            text = f"**📊 STATISTIK**\n\n👥 User: `{total_users}`\n✅ Aktif: `{total_active}`\n💰 Cuan: `{rp(total_rev)}`\n🏦 Dana: `{DANA_NUMBER}`"
            await event.edit(text, buttons=back_btn())
    
    except Exception as e:
        await event.respond(f"❌ Error: {str(e)}")

# ============ START ============
print("""
╔══════════════════════════════╗
║  🦅 XINN PANEL — READY      ║
║  Dana: 083175050030         ║
║  Admin: @xinn_admin         ║
╚══════════════════════════════╝
""")

bot.run_until_disconnected()
