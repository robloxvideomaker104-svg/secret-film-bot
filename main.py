import asyncio
import logging
from datetime import datetime, timedelta
import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiohttp import web
import os

# ==========================================
#               SOZLAMALAR
# ==========================================
BOT_TOKEN = "8656369612:AAHpVfrFadGX7RQgNu7YNZAYfqP_zJFinQQ"
ADMIN_ID = 8631477823  # Sizning Telegram ID raqamingiz
CARD_NUMBER = "9860 1666 5645 6349"
CARD_OWNER = "AZIZBEK K"

# Majburiy obuna kanallari
CHANNELS = [
    "@azizakabott",  
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==========================================
#        CALLBACK DATA FABRIKALARI
# ==========================================
class TariffCB(CallbackData, prefix="tariff"):
    days: int
    price: int

class ApproveCB(CallbackData, prefix="approve"):
    user_id: int
    days: int

class RejectCB(CallbackData, prefix="reject"):
    user_id: int

# ==========================================
#        MA'LUMOTLAR BAZASI (SQLITE)
# ==========================================
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                premium_until DATETIME
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                code INTEGER PRIMARY KEY,
                file_id TEXT
            )
        """)
        await db.commit()

async def add_user(user_id):
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()

async def is_premium(user_id) -> bool:
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT premium_until FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row and row[0]:
            premium_until = datetime.fromisoformat(row[0])
            return datetime.now() < premium_until
        return False

# ==========================================
#          MAJBURIY OBUNA MANTIQI
# ==========================================
async def check_subscription(user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

def get_sub_keyboard():
    builder = []
    for channel in CHANNELS:
        builder.append([InlineKeyboardButton(text="Obuna bo'lish", url=f"https://t.me/{channel[1:]}")])
    
    builder.append([InlineKeyboardButton(text="Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=builder)

main_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 Premium")]
    ],
    resize_keyboard=True
)

# ==========================================
#              KLAVIATURALAR
# ==========================================
def get_tariffs_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 kunlik obuna - 5 000 so'm", callback_data=TariffCB(days=1, price=5000).pack())],
        [InlineKeyboardButton(text="1 oylik obuna - 10 000 so'm", callback_data=TariffCB(days=30, price=10000).pack())],
        [InlineKeyboardButton(text="3 oylik obuna - 20 000 so'm", callback_data=TariffCB(days=90, price=20000).pack())],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_start")]
    ])

# ==========================================
#              FSM STATE'LAR
# ==========================================
class AdminState(StatesGroup):
    waiting_for_broadcast = State()

class PaymentState(StatesGroup):
    waiting_for_receipt = State()

# ==========================================
#          FOYDALANUVCHI HANDLERLARI
# ==========================================
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await add_user(message.from_user.id)
    subscribed = await check_subscription(message.from_user.id)
    
    if subscribed:
        await message.answer(
            f"👋 Assalomu alaykum <b>{message.from_user.first_name}</b>, botimizga xush kelibsiz.\n\n"
            f"✍️ Kino kodini yuboring...", 
            reply_markup=main_reply_keyboard, 
            parse_mode="HTML"
        )
    else:
        text = (
            "❌ <b>Kechirasiz, botimizdan foydalanish uchun ushbu kanallarga obuna bo'lishingiz kerak.</b>\n\n"
            "💎 <i>Premium obuna sotib olib, kanallarga obuna bo'lmasdan foydalanishingiz mumkin.</i>"
        )
        await message.answer(text, reply_markup=get_sub_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "check_sub")
async def check_sub_handler(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.delete()
        await call.message.answer(
            "✅ Obuna tasdiqlandi!\n\n✍️ Kino kodini yuboring...", 
            reply_markup=main_reply_keyboard, 
            parse_mode="HTML"
        )
    else:
        await call.answer("Barcha kanallarga obuna bo'lmadingiz!", show_alert=True)

@dp.callback_query(F.data == "back_to_start")
async def back_to_start_handler(call: types.CallbackQuery):
    await call.message.delete()
    fake_msg = types.Message(
        message_id=call.message.message_id,
        date=call.message.date,
        chat=call.message.chat,
        from_user=call.from_user
    )
    await start_handler(fake_msg)

@dp.message(F.text == "💎 Premium")
async def premium_text_handler(message: types.Message):
    text = (
        "💎 <b>Premium obuna</b>\n\n"
        "Premium orqali quyidagilarga ega bo'lasiz:\n"
        "• Kanallarga obuna bo'lmasdan kino ko'rish\n"
        "• Reklamalarsiz foydalanish\n"
        "• Yuqori sifatda tomosha qilish\n\n"
        "📋 Quyidagi tariflardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_tariffs_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "premium_menu")
async def premium_menu_handler(call: types.CallbackQuery):
    text = (
        "💎 <b>Premium obuna</b>\n\n"
        "Premium orqali quyidagilarga ega bo'lasiz:\n"
        "• Kanallarga obuna bo'lmasdan kino ko'rish\n"
        "• Reklamalarsiz foydalanish\n"
        "• Yuqori sifatda tomosha qilish\n\n"
        "📋 Quyidagi tariflardan birini tanlang:"
    )
    try:
        await call.message.edit_text(text, reply_markup=get_tariffs_keyboard(), parse_mode="HTML")
    except:
        await call.message.answer(text, reply_markup=get_tariffs_keyboard(), parse_mode="HTML")

@dp.callback_query(TariffCB.filter())
async def tariff_selected_handler(call: types.CallbackQuery, callback_data: TariffCB, state: FSMContext):
    await state.update_data(days=callback_data.days, price=callback_data.price)
    
    text = (
        "💎 <b>PREMIUM OBUNA — TO'LOV MA'LUMOTLARI</b>\n\n"
        f"📦 Tarif: {callback_data.days} kunlik obuna\n"
        f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"👤 Karta egasi: {CARD_OWNER}\n"
        f"💰 To'lov summasi: {callback_data.price:,} so'm\n\n"
        "⚠️ <b>Diqqat:</b>\n"
        "📸 Pulni o'tkazgandan so'ng, chekni (skrinshotni) yuborish uchun pastdagi tugmani bosing!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Chek rasmini yuborish", callback_data="send_receipt")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="premium_menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "send_receipt")
async def ask_receipt_handler(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(PaymentState.waiting_for_receipt)
    await call.message.answer("📸 Iltimos, to'lovni tasdiqlovchi chek (skrinshot) rasmini shu yerga yuboring:")
    await call.answer()

@dp.message(PaymentState.waiting_for_receipt, F.photo)
async def receipt_received_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    days = data.get("days", 30)
    price = data.get("price", 0)
    photo_file_id = message.photo[-1].file_id
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=ApproveCB(user_id=message.from_user.id, days=days).pack()),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=RejectCB(user_id=message.from_user.id).pack())
        ]
    ])
    
    caption = (
        "💳 <b>Yangi to'lov cheki keldi!</b>\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"📦 Tarif: {days} kunlik\n"
        f"💰 Summa: {price:,} so'm"
    )
    
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=caption, reply_markup=admin_kb, parse_mode="HTML")
    await message.answer("✅ <b>Chekingiz adminga yuborildi!</b>\nAdminlar tekshirib chiqquncha kuting.", parse_mode="HTML", reply_markup=main_reply_keyboard)
    await state.clear()

@dp.callback_query(ApproveCB.filter(), F.from_user.id == ADMIN_ID)
async def approve_payment_handler(call: types.CallbackQuery, callback_data: ApproveCB):
    user_id = callback_data.user_id
    days = callback_data.days
    
    now = datetime.now()
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT premium_until FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        
        if row and row[0]:
            current_expiry = datetime.fromisoformat(row[0])
            if current_expiry > now:
                new_expiry = current_expiry + timedelta(days=days)
            else:
                new_expiry = now + timedelta(days=days)
        else:
            new_expiry = now + timedelta(days=days)
        
        await db.execute("UPDATE users SET premium_until = ? WHERE user_id = ?", (new_expiry.isoformat(), user_id))
        await db.commit()
        
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 <b>Tabriklaymiz! To'lovingiz tasdiqlandi.</b>\nSizga {days} kunlik Premium obuna berildi. Endi kino kodlarini yuborishingiz mumkin!",
            parse_mode="HTML"
        )
    except Exception:
        pass
        
    await call.message.edit_caption(caption=call.message.caption + "\n\n<b>✅ TASDIQLANDI</b>", parse_mode="HTML")
    await call.answer("To'lov tasdiqlandi va foydalanuvchiga premium berildi!", show_alert=True)

@dp.callback_query(RejectCB.filter(), F.from_user.id == ADMIN_ID)
async def reject_payment_handler(call: types.CallbackQuery, callback_data: RejectCB):
    user_id = callback_data.user_id
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text="❌ <b>Kechirasiz, to'lov chekingiz rad etildi.</b>\nIltimos, to'g'ri chek yuborganingizga ishonch hosil qiling.",
            parse_mode="HTML"
        )
    except Exception:
        pass
        
    await call.message.edit_caption(caption=call.message.caption + "\n\n<b>❌ RAD ETILDI</b>", parse_mode="HTML")
    await call.answer("To'lov rad etildi.", show_alert=True)

# ==========================================
#      ADMIN: /prem va /backup BUYRUQLARI
# ==========================================
@dp.message(Command("prem"), F.from_user.id == ADMIN_ID)
async def admin_set_premium(message: types.Message):
    args = message.text.split()
    if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
        await message.reply("❌ <b>Xato format!</b>\n\nIshlatilishi: <code>/prem user_id kun</code>\nMisol: <code>/prem 123456789 30</code>", parse_mode="HTML")
        return
    
    uid = int(args[1])
    days = int(args[2])
    now = datetime.now()
    
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT premium_until FROM users WHERE user_id = ?", (uid,))
        row = await cursor.fetchone()
        
        if row and row[0]:
            current_expiry = datetime.fromisoformat(row[0])
            if current_expiry > now:
                new_expiry = current_expiry + timedelta(days=days)
            else:
                new_expiry = now + timedelta(days=days)
        else:
            new_expiry = now + timedelta(days=days)
            await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
            
        await db.execute("UPDATE users SET premium_until = ? WHERE user_id = ?", (new_expiry.isoformat(), uid))
        await db.commit()
    
    await message.reply(f"✅ <b>{uid}</b> ID raqamli foydalanuvchiga <b>{days} kunlik</b> Premium muvaffaqiyatli berildi!", parse_mode="HTML")
    try:
        await bot.send_message(uid, f"🎉 <b>Sizga admin tomonidan {days} kunlik Premium obuna taqdim etildi!</b> ✨", parse_mode="HTML")
    except:
        pass

@dp.message(Command("backup"), F.from_user.id == ADMIN_ID)
async def backup_database(message: types.Message):
    if os.path.exists("bot_database.db"):
        await message.answer_document(
            types.FSInputFile("bot_database.db"),
            caption="📂 <b>Bazaning nusxasi (Backup) tayyor!</b>\n\nBarcha ma'lumotlar xavfsiz saqlangan.",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ <b>Hozircha baza fayli topilmadi.</b>", parse_mode="HTML")

@dp.message(F.document & (F.from_user.id == ADMIN_ID))
async def restore_database(message: types.Message):
    if message.document.file_name.endswith(".db"):
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        await bot.download(file, destination="bot_database.db")
        await message.reply("✅ <b>Baza muvaffaqiyatli tiklandi!</b> Barcha ma'lumotlar joyiga qaytdi.", parse_mode="HTML")

# Kino qidirish
@dp.message(F.text.regexp(r'^\d+$'))
async def find_movie_handler(message: types.Message):
    movie_code = int(message.text)
    
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT file_id FROM movies WHERE code = ?", (movie_code,))
        row = await cursor.fetchone()
        
    # Agar kod bazada umuman bo'lmasa:
    if not row:
        await message.reply("❌ Kino kodini noto'g'ri yubordingiz!")
        return

    # Agar kod to'g'ri (bazada bor) lekin foydalanuvchida Premium yo'q bo'lsa:
    if not await is_premium(message.from_user.id) and message.from_user.id != ADMIN_ID:
        text = (
            "🔒 <b>Ushbu kino faqat «Premium» foydalanuvchilar uchun</b>\n\n"
            "❗ <b>Premium ga obuna bo'ling.</b>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Premium", callback_data="premium_menu")]
        ])
        await message.reply(text, reply_markup=kb, parse_mode="HTML")
        return

    # Agar foydalanuvchida Premium bo'lsa yoki admin bo'lsa, kinoni yuboramiz:
    await message.reply_video(video=row[0], caption=f"🎬 Kino kodi: {movie_code}\n\n🤖 @{bot._me.username}")

# ==========================================
#               ADMIN PANEL
# ==========================================
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie_handler(message: types.Message):
    if not message.caption or not message.caption.isdigit():
        await message.reply("❌ Kino qo'shish uchun video bilan birga uning kodini (faqat raqam) yozib yuboring!")
        return
    
    movie_code = int(message.caption)
    file_id = message.video.file_id
    
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT OR REPLACE INTO movies (code, file_id) VALUES (?, ?)", (movie_code, file_id))
        await db.commit()
        
    await message.reply(f"✅ Kino bazaga qo'shildi!\nKodi: {movie_code}")

@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel_handler(message: types.Message):
    btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Xabar tarqatish", callback_data="admin_broadcast")]
    ])
    await message.answer("👨‍💻 <b>Admin panelga xush kelibsiz!</b>\n\nQuyidagi menyudan kerakli bo'limni tanlang:", reply_markup=btn, parse_mode="HTML")

@dp.callback_query(F.data == "admin_stats", F.from_user.id == ADMIN_ID)
async def admin_stats_handler(call: types.CallbackQuery):
    async with aiosqlite.connect("bot_database.db") as db:
        users_count = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        movies_count = await (await db.execute("SELECT COUNT(*) FROM movies")).fetchone()
    
    text = (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"👥 Jami obunachilar: <b>{users_count[0]}</b> ta\n"
        f"🎬 Bazadagi kinolar: <b>{movies_count[0]}</b> ta"
    )
    back_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back")]])
    await call.message.edit_text(text, reply_markup=back_btn, parse_mode="HTML")

@dp.callback_query(F.data == "admin_back", F.from_user.id == ADMIN_ID)
async def admin_back_handler(call: types.CallbackQuery):
    btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Xabar tarqatish", callback_data="admin_broadcast")]
    ])
    await call.message.edit_text("👨‍💻 <b>Admin panelga xush kelibsiz!</b>\n\nQuyidagi menyudan kerakli bo'limni tanlang:", reply_markup=btn, parse_mode="HTML")

@dp.callback_query(F.data == "admin_broadcast", F.from_user.id == ADMIN_ID)
async def admin_broadcast_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "📢 <b>Barcha foydalanuvchilarga yuboriladigan xabarni yuboring:</b>\n"
        "(Matn, rasm yoki video yuborishingiz mumkin)\n\n"
        "<i>Bekor qilish uchun /cancel buyrug'ini yuboring.</i>", 
        parse_mode="HTML"
    )
    await state.set_state(AdminState.waiting_for_broadcast)

@dp.message(AdminState.waiting_for_broadcast, F.from_user.id == ADMIN_ID)
async def send_broadcast_handler(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        await message.answer("❌ Xabar tarqatish bekor qilindi.")
        await state.clear()
        return

    await message.answer("⏳ <b>Xabar tarqatish boshlandi...</b>", parse_mode="HTML")
    
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT user_id FROM users")
        users = await cursor.fetchall()
        
    success = 0
    for user in users:
        try:
            await message.send_copy(chat_id=user[0])
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    
    await message.answer(f"✅ <b>Xabar tarqatish yakunlandi!</b>\n\nYetib bordi: {success} ta foydalanuvchiga.", parse_mode="HTML")
    await state.clear()

# ==========================================
#          RENDER UCHUN WEB SERVER
# ==========================================
async def web_server():
    app = web.Application()
    async def index(request):
        return web.Response(text="Bot is running successfully!")
    app.router.add_get("/", index)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ==========================================
#          BOTNI ISHGA TUSHIRISH
# ==========================================
async def main():
    await init_db()
    bot._me = await bot.get_me() 
    print(f"Bot ishga tushdi: @{bot._me.username}")
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Render uchun veb-serverni fonda ishga tushiramiz
    asyncio.create_task(web_server())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
