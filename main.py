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

# Majburiy obuna va zayafka kanallari 
# DIQQAT: Bu yerda faqat KANAL yoki GURUH bo'lishi kerak! (Bot username yozmang)
CHANNELS = [
    "@azizakabott",  # <-- Haqiqiy kanal username yozing (masalan: @dono_kino)
    -1004433350429, 
    -1003822759522
]

# Kanallarning tugma uchun havolalari
CHANNEL_LINKS = {
    "@azizakabott": "https://t.me/azizakabott",
    -1004433350429: "https://t.me/+CAaOszXRNudkZmMy", 
    -1003822759522: "https://t.me/+iHpCgbHqot83Y2M6"  
}

# Namuna uchun stiker ID
DEFAULT_STICKER = "CAACAgIAAxkBAAE..."

async def send_safe_sticker(chat_id, sticker_id=DEFAULT_STICKER):
    try:
        await bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
    except Exception:
        pass

# ==========================================
#   ESKI PREMIUM FOYDALANUVCHILARNI TIKLASH
# ==========================================
RESTORE_PREMIUMS = {
    6995215348: 1,
    7357749954: 30,
    8155884555: 90,
    5155932471: 1,
    7731796910: 1,
    744698771: 1,
    8510392964: 1,
    5918260410: 30,
    8650088591: 1,
    7401775466: 1,
    2075869992: 1,
    5049541854: 1,
    7204139890: 1,
    8332345211: 30,
    571562624: 1,
    8691742694: 1,
    795489741: 30,
    8815235416: 30,
    1352713666: 30,
    8320258723: 30,
    8314003745: 1,
    7692360232: 30,
    7714128386: 1,
    928607993: 1,
    8537643549: 30,
    8342758698: 1,
    8057944739: 90,
    7945600821: 1,
    8059099133: 1,
    1308491657: 1,
    8772264288: 1,
    6434617440: 1,
    8754343665: 1,
    8430907854: 30,
    1439060625: 1,
    8509514098: 1,
    753002115: 1,
    5977138348: 1,
    6080026487: 1,
    6973564025: 1,
    7733996178: 30,
    7322214856: 1,
    5963739922: 1,
    7501215842: 1,
    6748870757: 1,
    8593927748: 1,
    1245128200: 30,
    6694134343: 1,
    6857725953: 1,
    8032474493: 30,
    852504096: 1,
    8520113330: 1,
    7417710338: 1,
    7282908833: 1,
    7399959572: 30,
    751263728: 30,
    7929897679: 1,
    83896599: 1,
    8531457148: 1,
    8741323351: 1,
    8889212515: 1,
    7602309795: 1,
    8702792457: 1,
    8538619007: 1,
    8218231106: 1,
    2054296247: 1,
    6141326741: 1,
    892751393: 30,
    7634960767: 1,
    7403182573: 30,
    1861385433: 1,
    6821100300: 1,
    8604082827: 30,
    5784891487: 1,
    7997224524: 1,
    698670822: 90,
    6468528104: 1,
    1918443225: 1,
    2130137985: 1,
    153276632: 1,
    7683507959: 1,
    8184013009: 90,
    8726443289: 30,
    5681338439: 1,
    5234537997: 1,
    7228628278: 30,
    1177224715: 1,
    7538665368: 30,
    7854162098: 1,
    8276775311: 30,
    5404074578: 90,
    8150430958: 1,
    8497247894: 1,
    5758172340: 1,
    1118945247: 30,
    8222256543: 1,
    8629852631: 30,
    1371548814: 1,
    8438917027: 1,
    8928414393: 90,
    7685177470: 30,
    8041366716: 30,
    8853329563: 30,
    8240387712: 30,
    6931882484: 90,
    6586070765: 1,
    797542524: 30,
    6599948446: 1,
    8131800490: 1,
    8752002895: 1,
    538612236: 1,
    8580152128: 30,
    6594543919: 90,
    7899686461: 1,
    7812929338: 1,
    5078273360: 30,
    344789400: 30,
    880004636: 1,
    5537387692: 1,
    7386991381: 30,
    6551739581: 1,
    1637768031: 1,
    7989042566: 1,
    1841178313: 1,
    5892028049: 30,
    530628067: 90,
    6044924286: 1,
    7598424593: 30,
    8753838076: 30,
    7943038460: 1,
    6075901755: 30,
    8673738885: 30,
    2133858309: 1,
    6743342411: 1,
    8543071824: 30,
    8673326507: 1,
    1402732175: 1,
    8302451432: 1,
    7417648259: 1,
    521186137: 1,
    5037855230: 1,
    1621013930: 1,
    5362441842: 1,
    8669490585: 1,
    630599183: 1,
    8523223733: 1,
    7098228838: 1,
    460921746: 30,
    8775426066: 1,
    6027898356: 30,
    8212146332: 1,
    8704581882: 1,
    828918955: 90,
    1033949413: 30,
    1068763023: 90,
    7733971853: 90,
    6717295772: 30,
    8071854273: 30,
    1083354173: 30,
    8746218879: 30,
    5245271026: 90,
    8576661469: 30,
    8134930963: 30,
    8711049823: 30,
    5248274740: 1
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class TariffCB(CallbackData, prefix="tariff"):
    days: int
    price: int

class ApproveCB(CallbackData, prefix="approve"):
    user_id: int
    days: int

class RejectCB(CallbackData, prefix="reject"):
    user_id: int

class BroadcastState(StatesGroup):
    waiting_for_message = State()

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
                file_id TEXT,
                views INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS join_requests (
                user_id INTEGER,
                chat_id TEXT,
                PRIMARY KEY (user_id, chat_id)
            )
        """)
        await db.commit()

        now = datetime.now()
        for uid, days in RESTORE_PREMIUMS.items():
            expiry = now + timedelta(days=days)
            await db.execute(
                "INSERT INTO users (user_id, premium_until) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET premium_until = ?",
                (uid, expiry.isoformat(), expiry.isoformat())
            )
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
#          ADMIN PREMIUM BERISH KOMANDASI
# ==========================================
@dp.message(Command("prem"), F.from_user.id == ADMIN_ID)
async def admin_set_premium(message: types.Message):
    args = message.text.split()
    if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
        await message.reply("❌ <b>Xato format!</b>\n\nIshlatilishi: <code>/prem user_id kun</code>\nMisol: <code>/prem 6995215348 30</code>", parse_mode="HTML")
        return
    
    uid = int(args[1])
    days = int(args[2])
    now = datetime.now()
    expiry = now + timedelta(days=days)
    
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute(
            "INSERT INTO users (user_id, premium_until) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET premium_until = ?",
            (uid, expiry.isoformat(), expiry.isoformat())
        )
        await db.commit()
    
    await message.reply(f"✅ <b>{uid}</b> ID raqamli foydalanuvchiga <b>{days} kunlik</b> Premium muvaffaqiyatli berildi!", parse_mode="HTML")
    try:
        await bot.send_message(uid, f"🎉 <b>Sizga admin tomonidan {days} kunlik Premium obuna taqdim etildi!</b> ✨")
    except:
        pass

# ==========================================
#    ZAYAFKANI BAZAGA YOZISH (QABUL QILMASDAN)
# ==========================================
@dp.chat_join_request()
async def chat_join_request_handler(chat_join: types.ChatJoinRequest):
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO join_requests (user_id, chat_id) VALUES (?, ?)",
            (chat_join.from_user.id, str(chat_join.chat.id))
        )
        await db.commit()

# ==========================================
#      QAT'IY OBUNA VA ZAYAFKA TEKSHIRISH
# ==========================================
async def check_subscription(user_id: int) -> bool:
    # Admin har doim o'tishi uchun (xohlasangiz bu qatorni olib tashlashingiz mumkin)
    if user_id == ADMIN_ID:
        return True

    async with aiosqlite.connect("bot_database.db") as db:
        for channel in CHANNELS:
            is_subbed = False
            
            # 1. Obuna bo'lganligini tekshirish
            try:
                member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
                if member.status in ['member', 'administrator', 'creator']:
                    is_subbed = True
            except Exception:
                pass
            
            # 2. Agar a'zo bo'lmasa, zayafka (so'rov) tashlaganini tekshirish
            if not is_subbed:
                cursor = await db.execute(
                    "SELECT 1 FROM join_requests WHERE user_id = ? AND chat_id = ?",
                    (user_id, str(channel))
                )
                row = await cursor.fetchone()
                if row:
                    is_subbed = True
            
            # Agar bittagina kanalda ham obuna yoki zayafka bo'lmasa -> DARHOL FALSE QAYTARADI
            if not is_subbed:
                return False
                
    return True

def get_sub_keyboard():
    builder = []
    for idx, channel in enumerate(CHANNELS, start=1):
        link = CHANNEL_LINKS.get(channel, "https://t.me/")
        builder.append([InlineKeyboardButton(text=f"📢 {idx}-Kanalga obuna / So'rov yuborish", url=link)])
    
    builder.append([InlineKeyboardButton(text="🔄 Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=builder)

main_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 Premium obuna")]
    ],
    resize_keyboard=True
)

def get_tariffs_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ 1 kunlik obuna - 5 000 so'm", callback_data=TariffCB(days=1, price=5000).pack())],
        [InlineKeyboardButton(text="📅 1 haftalik obuna - 10 000 so'm", callback_data=TariffCB(days=7, price=10000).pack())],
        [InlineKeyboardButton(text="🗓 1 oylik obuna - 20 000 so'm", callback_data=TariffCB(days=30, price=20000).pack())],
        [InlineKeyboardButton(text="⭐ 1 yillik obuna - 100 000 so'm", callback_data=TariffCB(days=365, price=100000).pack())],
        [InlineKeyboardButton(text="◀️ Orqaga qaytish", callback_data="back_to_start")]
    ])

class PaymentState(StatesGroup):
    waiting_for_receipt = State()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await add_user(message.from_user.id)
    if await check_subscription(message.from_user.id):
        await send_safe_sticker(message.from_user.id)
        await message.answer(
            f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
            "🤖 <b>Botimizga xush kelibsiz. Kinolarni topish uchun kino kodini yuboring:</b> 👇", 
            reply_markup=main_reply_keyboard, 
            parse_mode="HTML"
        )
    else:
        text = (
            "❌ <b>DIQQAT! BOTDAN FOYDALANIB BO'LMAYDI!</b>\n\n"
            "<b>Botimizning barcha imkoniyatlaridan foydalanish uchun quyidagi homiy kanallarga obuna bo'ling yoki zayafka tashlang:</b> 👇"
        )
        await message.answer(text, reply_markup=get_sub_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "check_sub")
async def check_sub_handler(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.delete()
        await send_safe_sticker(call.from_user.id)
        await call.message.answer(
            "✅ <b>Obunangiz tasdiqlandi!</b>\n\n"
            "🎬 <b>Endi kino kodini yuborishingiz mumkin:</b> 👇", 
            reply_markup=main_reply_keyboard, 
            parse_mode="HTML"
        )
    else:
        await call.answer("❌ Siz hali hamma kanallarga obuna bo'lmadingiz yoki zayafka tashlamadingiz!", show_alert=True)

@dp.callback_query(F.data == "back_to_start")
async def back_to_start_handler(call: types.CallbackQuery):
    await call.message.delete()
    fake_msg = types.Message(message_id=call.message.message_id, date=call.message.date, chat=call.message.chat, from_user=call.from_user)
    await start_handler(fake_msg)

@dp.message(F.text == "💎 Premium obuna")
async def premium_text_handler(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval barcha kanallarga obuna bo'ling!", reply_markup=get_sub_keyboard())
        return
    text = (
        "💎 <b>PREMIUM OBUNA MARKAZI</b>\n\n"
        "✨ <b>Premium foydalanuvchilar barcha kinolarni cheklovsiz va reklamasiz tomosha qilishadi!</b>\n\n"
        "👇 <b>Quyidagi tariflardan birini tanlang:</b>"
    )
    await send_safe_sticker(message.from_user.id)
    await message.answer(text, reply_markup=get_tariffs_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "premium_menu")
async def premium_menu_handler(call: types.CallbackQuery):
    if not await check_subscription(call.from_user.id):
        await call.message.answer("❌ Avval barcha kanallarga obuna bo'ling!", reply_markup=get_sub_keyboard())
        return
    text = (
        "💎 <b>PREMIUM OBUNA MARKAZI</b>\n\n"
        "✨ <b>Premium foydalanuvchilar barcha kinolarni cheklovsiz va reklamasiz tomosha qilishadi!</b>\n\n"
        "👇 <b>Quyidagi tariflardan birini tanlang:</b>"
    )
    try:
        await call.message.edit_text(text, reply_markup=get_tariffs_keyboard(), parse_mode="HTML")
    except:
        await call.message.answer(text, reply_markup=get_tariffs_keyboard(), parse_mode="HTML")

@dp.callback_query(TariffCB.filter())
async def tariff_selected_handler(call: types.CallbackQuery, callback_data: TariffCB, state: FSMContext):
    await state.update_data(days=callback_data.days, price=callback_data.price)
    text = (
        f"💳 <b>TO'LOV MA'LUMOTLARI</b>\n\n"
        f"📌 <b>Tanlangan tarif:</b> {callback_data.days} kun\n"
        f"💰 <b>Summa:</b> <code>{callback_data.price:,}</code> so'm\n\n"
        f"🏦 <b>Karta raqami:</b> <code>{CARD_NUMBER}</code>\n"
        f"👤 <b>Karta egasi:</b> {CARD_OWNER}\n\n"
        "📸 <b>To'lovni amalga oshirgach, chek skrinshotini botga yuboring!</b> 👇"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Chek rasmini yuborish", callback_data="send_receipt")],
        [InlineKeyboardButton(text="◀️ Orqaga qaytish", callback_data="premium_menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "send_receipt")
async def ask_receipt_handler(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(PaymentState.waiting_for_receipt)
    await call.message.answer("📸 <b>Iltimos, to'lov cheki skrinshotini rasm ko'rinishida yuboring:</b> 👇", parse_mode="HTML")
    await call.answer()

@dp.message(PaymentState.waiting_for_receipt, F.photo)
async def receipt_received_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    days = data.get("days", 30)
    price = data.get("price", 0)
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=ApproveCB(user_id=message.from_user.id, days=days).pack()),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=RejectCB(user_id=message.from_user.id).pack())
        ]
    ])
    
    caption = (
        f"💳 <b>YANGI TO'LOV CHEKI!</b>\n\n"
        f"👤 <b>Foydalanuvchi ID:</b> <code>{message.from_user.id}</code>\n"
        f"⏳ <b>Obuna muddati:</b> {days} kun\n"
        f"💰 <b>Summa:</b> <code>{price:,}</code> so'm"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, reply_markup=admin_kb, parse_mode="HTML")
    await message.answer("✅ <b>Chekingiz adminga muvaffaqiyatli yuborildi!</b>\n\nAdmin tasdiqlashini kuting. ⏳", reply_markup=main_reply_keyboard, parse_mode="HTML")
    await state.clear()

@dp.callback_query(ApproveCB.filter(), F.from_user.id == ADMIN_ID)
async def approve_payment_handler(call: types.CallbackQuery, callback_data: ApproveCB):
    now = datetime.now()
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT premium_until FROM users WHERE user_id = ?", (callback_data.user_id,))
        row = await cursor.fetchone()
        new_expiry = (datetime.fromisoformat(row[0]) if row and row[0] and datetime.fromisoformat(row[0]) > now else now) + timedelta(days=callback_data.days)
        await db.execute("UPDATE users SET premium_until = ? WHERE user_id = ?", (new_expiry.isoformat(), callback_data.user_id))
        await db.commit()
    try:
        await send_safe_sticker(callback_data.user_id)
        await bot.send_message(callback_data.user_id, f"🎉 <b>Tabriklaymiz! To'lovingiz tasdiqlandi va sizga {callback_data.days} kunlik Premium berildi!</b> ✨", parse_mode="HTML")
    except:
        pass
    await call.message.edit_caption(caption=call.message.caption + "\n\n<b>✅ HOLAT: TASDIQLANDI</b>", parse_mode="HTML")
    await call.answer("To'lov tasdiqlandi!")

@dp.callback_query(RejectCB.filter(), F.from_user.id == ADMIN_ID)
async def reject_payment_handler(call: types.CallbackQuery, callback_data: RejectCB):
    try:
        await bot.send_message(callback_data.user_id, "❌ <b>Kechirasiz, to'lov chekingiz admin tomonidan rad etildi.</b>", parse_mode="HTML")
    except:
        pass
    await call.message.edit_caption(caption=call.message.caption + "\n\n<b>❌ HOLAT: RAD ETILDI</b>", parse_mode="HTML")
    await call.answer("To'lov rad etildi.")

# ==========================================
#          BACKUP VA RESTORE TIZIMI
# ==========================================
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

# ==========================================
#          KINO VA STATISTIKA
# ==========================================
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie_handler(message: types.Message):
    if not message.caption or not message.caption.isdigit():
        await message.reply("❌ <b>Video bilan birga uning kodini (faqat raqam) yozib yuboring!</b>", parse_mode="HTML")
        return
    
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute(
            "INSERT INTO movies (code, file_id, views) VALUES (?, ?, 0) ON CONFLICT(code) DO UPDATE SET file_id=excluded.file_id", 
            (int(message.caption), message.video.file_id)
        )
        await db.commit()
    await message.reply(f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n🔢 Kodi: <code>{message.caption}</code>", parse_mode="HTML")

@dp.message(F.text.regexp(r'^\d+$'))
async def find_movie_handler(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer(
            "❌ <b>DIQQAT! Botdan foydalanish uchun kanallarga obuna bo'ling yoki so'rov yuboring:</b> 👇", 
            reply_markup=get_sub_keyboard(), 
            parse_mode="HTML"
        )
        return

    movie_code = int(message.text)
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT file_id, views FROM movies WHERE code = ?", (movie_code,))
        row = await cursor.fetchone()
        
        if row:
            await db.execute("UPDATE movies SET views = views + 1 WHERE code = ?", (movie_code,))
            await db.commit()
        
    if not row:
        await message.reply("❌ <b>Kechirasiz, bunday kodli kino topilmadi!</b>", parse_mode="HTML")
        return

    if not await is_premium(message.from_user.id) and message.from_user.id != ADMIN_ID:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💎 Premium obuna sotib olish", callback_data="premium_menu")]])
        await send_safe_sticker(message.from_user.id)
        await message.reply("🔒 <b>Ushbu kino faqat Premium foydalanuvchilar uchun mo'ljallangan!</b>", reply_markup=kb, parse_mode="HTML")
        return

    await message.reply_video(
        video=row[0], 
        caption=f"🎬 <b>Kino kodi:</b> <code>{movie_code}</code>\n👀 <b>Ko'rishlar soni:</b> <code>{row[1] + 1}</code> marta",
        parse_mode="HTML"
    )

@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel_handler(message: types.Message):
    btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Xabar tarqatish", callback_data="admin_broadcast")]
    ])
    await message.answer("👨‍💻 <b>Admin boshqaruv paneli:</b>", reply_markup=btn, parse_mode="HTML")

@dp.callback_query(F.data == "admin_stats", F.from_user.id == ADMIN_ID)
async def admin_stats_handler(call: types.CallbackQuery):
    async with aiosqlite.connect("bot_database.db") as db:
        u_cnt = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        m_cnt = await (await db.execute("SELECT COUNT(*) FROM movies")).fetchone()
        total_views = await (await db.execute("SELECT SUM(views) FROM movies")).fetchone()
        views_sum = total_views[0] if total_views and total_views[0] else 0
        
    text = (
        "📊 <b>BOT STATISTIKASI</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{u_cnt[0]}</b> ta\n"
        f"🎬 Bazadagi kinolar: <b>{m_cnt[0]}</b> ta\n"
        f"👀 Jami ko'rishlar: <b>{views_sum}</b> marta"
    )
    await call.message.edit_text(text, parse_mode="HTML")

# ==========================================
#          XABAR TARQATISH (BROADCAST)
# ==========================================
@dp.callback_query(F.data == "admin_broadcast", F.from_user.id == ADMIN_ID)
async def admin_broadcast_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastState.waiting_for_message)
    await call.message.answer("📢 <b>Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring (matn, rasm yoki video):</b>", parse_mode="HTML")
    await call.answer()

@dp.message(BroadcastState.waiting_for_message, F.from_user.id == ADMIN_ID)
async def admin_broadcast_process(message: types.Message, state: FSMContext):
    await state.clear()
    status_msg = await message.answer("⏳ <b>Xabar tarqatish boshlandi...</b>", parse_mode="HTML")
    
    async with aiosqlite.connect("bot_database.db") as db:
        cursor = await db.execute("SELECT user_id FROM users")
        users = await cursor.fetchall()
    
    success = 0
    failed = 0
    for (uid,) in users:
        try:
            await message.send_copy(chat_id=uid)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
            
    await status_msg.edit_text(
        f"✅ <b>Xabar tarqatish yakunlandi!</b>\n\n"
        f"📤 Yuborildi: <b>{success}</b> ta\n"
        f"❌ Xatolik (botni bloklaganlar): <b>{failed}</b> ta",
        parse_mode="HTML"
    )

# ==========================================
#          RENDER WEBSERVER & MAIN
# ==========================================
async def web_server():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()

async def main():
    await init_db()
    bot._me = await bot.get_me()
    print(f"Bot ishga tushdi: @{bot._me.username}")
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
