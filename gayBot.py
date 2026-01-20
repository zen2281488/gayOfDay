import os
import sys
import json
import random
import datetime
import aiosqlite
import traceback
from collections import Counter
from vkbottle.bot import Bot, Message
from groq import AsyncGroq
import logging

# ================= НАСТРОЙКИ =================
VK_TOKEN = os.getenv("VK_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# 🔥 ВОТ ТУТ МЫ КОНВЕРТИРУЕМ СТРОКУ В ЧИСЛО 🔥
# Если в .env ничего нет, по умолчанию будет 0.9
try:
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.9"))
except ValueError:
    print("⚠️ Ошибка в GROQ_TEMPERATURE, ставлю 0.9 по умолчанию")
    GROQ_TEMPERATURE = 0.9

if not VK_TOKEN or not GROQ_API_KEY:
    print("❌ ОШИБКА: Не найдены VK_TOKEN или GROQ_API_KEY!")
    sys.exit(1)

GAME_TITLE = "Пидор дня"
BOT_TRIGGER = "/кто"
RESET_TRIGGER = "/сброс"
DB_NAME = os.getenv("DB_PATH", "chat_history.db")

# 🔥 ПРОМПТ 🔥
SYSTEM_PROMPT = (
    f"Ты — ебаный дегенерат, озлобленный конченый тролль, выбирающий '{GAME_TITLE}'. "
    f"Твоя цель — не просто выбрать, а вьебать так, чтобы читающие обосрались от стыда. "
    f"Ты смотришь на лог как на помойку, где каждый участник — долбоёб. "
    
    f"АНАЛИЗИРУЙ ЖЁСТКО:\n"
    f"1. Выцепи ЦИТАТЫ из лога (в кавычках), тыкая в них носом как в говно\n"
    f"2. Уёбищно интерпретируй каждую фразу: обычное 'привет' = 'дрочил 2 часа и выдал это'\n"
    f"3. Бей ниже пояса: внешность, интеллект, личную жизнь, все говно\n"
    f"4. Обязательно используй МАТ: пидор, хуй, блядь, пиздец, еблан, сука, мразь\n"
    f"5. Длина вердикта: 4-6 предложений минимум. Растяни унижение как резину\n"
    
    f"Если не найдешь цитат — высоси из пальца и придумай, что они скрытые пидоры.\n"
    f"Формат ответа — только ебучий JSON: {{'user_id': <id>, 'reason': '<ТВОЁ ПИЗДЕЦ ОСКОРБИТЕЛЬНОЕ МНОГОБУКВ, С ЦИТАТАМИ, МАТОМ И ПРЕЗРЕНИЕМ>'}}\n"
    
    f"Твоя роль — обиженка-неудачник, который вымещает злобу на случайных людях в чате. "
    f"Чем грязнее, личнее и беспощаднее — тем лучше. Не жалей, не сдерживайся, будь тем самым охуевшим гопником-судьёй."
)

bot = Bot(token=VK_TOKEN)
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                user_id INTEGER, peer_id INTEGER, text TEXT, timestamp INTEGER, username TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_game (
                peer_id INTEGER, date TEXT, winner_id INTEGER, reason TEXT, PRIMARY KEY (peer_id, date)
            )
        """)
        await db.commit()

async def choose_winner_via_groq(chat_log: list) -> dict:
    context_lines = []
    available_ids = set()
    
    for uid, text, name in chat_log:
        if len(text.strip()) < 3:
            continue
            
        safe_name = name if name else "Unknown"
        context_lines.append(f"[{uid}] {safe_name}: {text}")
        available_ids.add(uid)

    if not context_lines:
        return {"user_id": 0, "reason": "Все молчат. Скучные натуралы."}

    context_text = "\n".join(context_lines)

    user_prompt = (
        f"Лог чата:\n{context_text}\n\n"
        f"Кто из них {GAME_TITLE}? Выбери user_id и придумай причину (но обращаясь к пользователю по имени, а не по id). "
        f"ВАЖНО: В тексте вердикта ('reason') обращайся к человеку по ИМЕНИ, а не по цифрам ID! "
        f"Используй цитаты из сообщений для максимального унижения. "
        f"Вердикт должен быть 4-6 предложений с сарказмом."
    )

    try:
        print(f"DEBUG: Sending request to Groq with {len(context_lines)} messages. Temp: {GROQ_TEMPERATURE}")
        
        completion = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=GROQ_TEMPERATURE, # <-- ИСПОЛЬЗУЕМ СКОНВЕРТИРОВАННОЕ ЧИСЛО
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content
        print(f"DEBUG: Raw Groq response: {content[:500]}...")
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                result = json.loads(json_str)
            else:
                raise
        
        if not isinstance(result, dict):
            raise ValueError("Result is not a dictionary")
            
        user_id = int(result.get('user_id', 0))
        if user_id not in available_ids:
            result['user_id'] = random.choice(list(available_ids))
        else:
            result['user_id'] = user_id
            
        return result

    except Exception as e:
        print(f"ERROR: Groq API error: {type(e).__name__}: {e}")
        traceback.print_exc()
    
    # Fallback
    print("DEBUG: Using fallback selection")
    if available_ids:
        user_counts = Counter([uid for uid, _, _ in chat_log if uid in available_ids])
        if user_counts:
            most_active = max(user_counts.items(), key=lambda x: x[1])[0]
            fallback_reasons = [
                f"Настрочил {user_counts[most_active]} сообщений и нихуя умного. Поздравляю, ты душный.",
                f"За {user_counts[most_active]} сообщений спама. ИИ сломался от твоей тупости, поэтому победа твоя.",
                "ИИ отказался работать с таким контингентом, поэтому ты пидор просто по факту существования."
            ]
            return {"user_id": most_active, "reason": random.choice(fallback_reasons)}
    
    return {"user_id": 0, "reason": "Чат мертв, и вы все мертвы внутри."}

# --- КОМАНДА СБРОСА ---
@bot.on.message(text=RESET_TRIGGER)
async def reset_daily_game(message: Message):
    peer_id = message.peer_id
    today = datetime.date.today().isoformat()
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM daily_game WHERE peer_id = ? AND date = ?", (peer_id, today))
        await db.commit()
    
    await message.answer("🔄 Результаты аннулированы! Память стерта.\nПишите /кто чтобы выбрать нового пидора.")

# --- ЗАПУСК ИГРЫ ---
@bot.on.message(text=BOT_TRIGGER)
async def run_game(message: Message):
    peer_id = message.peer_id
    today = datetime.date.today().isoformat()

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT winner_id, reason FROM daily_game WHERE peer_id = ? AND date = ?", (peer_id, today))
        result = await cursor.fetchone()

        if result:
            winner_id, reason = result
            try:
                user_info = await bot.api.users.get(user_ids=[winner_id])
                name = f"{user_info[0].first_name} {user_info[0].last_name}"
            except:
                name = "Unknown"
            await message.answer(f"Уже определили!\n{GAME_TITLE}: [id{winner_id}|{name}]\n\n📝 {reason}\n\n(Чтобы сбросить: /сброс)")
            return

        cursor = await db.execute("""
            SELECT user_id, text, username 
            FROM messages 
            WHERE peer_id = ? 
            AND LENGTH(TRIM(text)) > 2
            ORDER BY timestamp DESC 
            LIMIT 200
        """, (peer_id,))
        rows = await cursor.fetchall()
        
        if len(rows) < 3:
            await message.answer("Мало сообщений. Пишите больше, чтобы я мог выбрать худшего.")
            return

        chat_log = list(reversed(rows))

    await message.answer(f"🎲 Изучаю {len(chat_log)} сообщений... Кто же сегодня опозорится?")
    
    try:
        decision = await choose_winner_via_groq(chat_log)
        winner_id = decision['user_id']
        reason = decision.get('reason', 'Нет причины')
        
        if winner_id == 0:
            await message.answer("Ошибка выбора. Попробуйте позже.")
            return

    except Exception as e:
        print(f"ERROR in game logic: {e}")
        await message.answer("Ошибка при выборе победителя.")
        return

    try:
        user_data = await bot.api.users.get(user_ids=[winner_id])
        winner_name = f"{user_data[0].first_name} {user_data[0].last_name}"
    except:
        winner_name = "Жертва"

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO daily_game (peer_id, date, winner_id, reason) VALUES (?, ?, ?, ?)", 
            (peer_id, today, winner_id, reason)
        )
        await db.commit()

    await message.answer(
        f"👑 {GAME_TITLE.upper()} НАЙДЕН!\n"
        f"Поздравляем (нет): [id{winner_id}|{winner_name}]\n\n"
        f"💬 Вердикт:\n{reason}"
    )

@bot.on.message()
async def logger(message: Message):
    if message.text and not message.text.startswith("/"):
        try:
            user_info = await message.get_user()
            username = f"{user_info.first_name} {user_info.last_name}"
        except:
            username = "Unknown"

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "INSERT INTO messages (user_id, peer_id, text, timestamp, username) VALUES (?, ?, ?, ?, ?)",
                (message.from_id, message.peer_id, message.text, message.date, username)
            )
            await db.commit()

if __name__ == "__main__":
    print(f"🚀 Starting bot...")
    logging.basicConfig(level=logging.DEBUG)
    bot.loop_wrapper.on_startup.append(init_db())
    bot.run_forever()