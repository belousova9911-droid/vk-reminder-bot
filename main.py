import os
import time
import threading
import datetime
import logging
from zoneinfo import ZoneInfo

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

# ================= НАСТРОЙКИ И ЛОГИРОВАНИЕ =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ГЛАВНОЕ: Бот сверяет время ТОЛЬКО по Перми.
TARGET_TZ = ZoneInfo("Asia/Yekaterinburg")

TOKEN = os.getenv("VK_TOKEN")
GROUP_ID_STR = os.getenv("GROUP_ID")
PEER_ID_STR = os.getenv("PEER_ID")

if not all([TOKEN, GROUP_ID_STR, PEER_ID_STR]):
    logger.error("❌ Не заданы переменные окружения: VK_TOKEN, GROUP_ID, PEER_ID")
    raise ValueError("Не заданы обязательные переменные окружения")

try:
    GROUP_ID = int(GROUP_ID_STR)
    PEER_ID = int(PEER_ID_STR)
except ValueError as e:
    logger.error(f"❌ GROUP_ID или PEER_ID не являются числами: {e}")
    raise

logger.info(f"✅ Конфигурация загружена. Целевой часовой пояс: Пермь ({TARGET_TZ})")

# Инициализация VK API
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# ================= СООБЩЕНИЯ =================

MORNING_MESSAGES = [
    """Доброе утро, команда! ☀️ Пусть день будет спокойным, чётким и продуктивным.
Цитата дня: „Маленькие шаги каждый день приводят к большим результатам“.
Вперёд — у нас всё получится! 💪""",
    """С добрым утром, ребята! 🌞 Сегодня отличный день, чтобы сделать всё по плану и даже чуть больше.
Цитата дня: „Дисциплина — это не ограничение свободы, а отсечение всего лишнего“.
Держим фокус и идём уверенно! 🤝""",
    """Привет, команда! ☕ Утро — время задать правильный ритм смене. Пусть всё идёт по чек-листам, без суеты и с отличным качеством.
Цитата дня: „Лучший способ предсказать будущее — создать его“.
Хорошей продуктивной смены! ✨""",
]

MESSAGES = {
    "09:00": """Доброе утро, команда! ☀️
Начинаем день с правильных приоритетов. Пусть всё идёт по плану!""",
    "11:30": """Привет, команда! 😊
Сейчас самое время отправить ЧЛ обхода производства.
Прикрепите фотоотчёт — мы всё видим и ценим вашу внимательность! 👍
Спасибо! 🫡""",
    "12:00": """Добрый день, команда! 🌞
К 12:00, пожалуйста, отправьте:
📊 часовик за предыдущий день;
🎯 цели и фокусы на текущую смену;
🗓 спланированный часовик на текущую смену.
Ждём файлы и скрины в чат. 📩""",
    "14:30": """Всем привет! 💛
В 14:30 — время отправить два важных отчёта:
🚶 ЧЛ Обхода производства;
🧽 ЧЛ Дезинфекции поверхностей.
Спасибо за вашу аккуратность! 👏
Присылайте в чат. 📸""",
    "15:30": """Привет, команда! 👋
Время отправить часовик с 11 до 15. Это важная точка контроля.
Спасибо, что фиксируете цифры! 🙏
Ждём отчёт в чат. 📈""",
    "16:30": """Добрый вечер, команда! 🌙
Напоминаю про ЧЛ Обхода — отправьте, пожалуйста, отчёт к 16:30.
Спасибо за вашу внимательность! 😊
Ждём фото в чат. 📸""",
    "17:00": """Привет! 👋
В 17:00 запланирована пятиминутка с командой.
Также ждём часовик за период 15–17.
Отчёты — в чат. 📩""",
    "18:30": """Вечер добрый, команда! ✨
Не забудьте отправить ЧЛ Дезинфекции к 18:30.
Чистота и безопасность — наша общая забота! ❤️
Присылайте фотоотчёт. 📸""",
    "20:30": """Ещё один контрольный момент: к 20:30 отправьте, пожалуйста, ЧЛ Обхода.
Даже если всё спокойно — фотофиксация важна. 💪
Ждём в чат. 📩""",
    "21:30": """Почти финиш! 🎉
К 21:30, пожалуйста, отправьте часовик за период 17–21.
Спасибо за точные цифры! 🙏
Ждём отчёт. 📉""",
}

CLOSING_MESSAGE = """Смена подходит к концу! 🌆
Пожалуйста, проконтролируйте закрытие смены и пришлите финальный фотоотчёт.
Спасибо всей команде за отличную работу! 💛
Дайте короткую обратную связь и не забудьте похвалить ребят. 👏
Спасибо за смену! 🤗"""

# ================= ОТПРАВКА СООБЩЕНИЙ =================

def send_message(text: str):
    now_perm = datetime.datetime.now(TARGET_TZ)
    try:
        vk.messages.send(
            peer_id=PEER_ID,
            message=text,
            random_id=get_random_id()
        )
        logger.info(f"[Пермь {now_perm.strftime('%H:%M')}] ✅ Сообщение отправлено: {text[:40]}...")
    except Exception as e:
        logger.error(f"[Пермь {now_perm.strftime('%H:%M')}] ❌ Ошибка отправки: {e}")

def get_morning_message():
    now = datetime.datetime.now(TARGET_TZ)
    day_of_year = now.timetuple().tm_yday
    return MORNING_MESSAGES[day_of_year % len(MORNING_MESSAGES)]

def send_by_time(time_key: str):
    text = MESSAGES.get(time_key)
    if text:
        send_message(text)
    else:
        logger.warning(f"⚠️ Нет сообщения для времени {time_key}")

def send_closing():
    now = datetime.datetime.now(TARGET_TZ)
    weekday = now.weekday()
    
    is_weekday = weekday in (0, 1, 2, 3, 6)
    is_weekend = weekday in (4, 5)

    if (is_weekday and now.hour == 22 and now.minute == 20) or \
       (is_weekend and now.hour == 23 and now.minute == 20):
        send_message(CLOSING_MESSAGE)

# ================= ПЛАНИРОВЩИК =================

def run_scheduler():
    logger.info("🕒 Планировщик запущен. Следим за временем по Перми.")
    
    tasks = [
        (9, 0, "09:00"),
        (11, 30, "11:30"),
        (12, 0, "12:00"),
        (14, 30, "14:30"),
        (15, 30, "15:30"),
        (16, 30, "16:30"),
        (17, 0, "17:00"),
        (18, 30, "18:30"),
        (20, 30, "20:30"),
        (21, 30, "21:30"),
    ]

    last_sent = set()

    while True:
        try:
            now = datetime.datetime.now(TARGET_TZ)
            current_time_str = f"{now.hour:02d}:{now.minute:02d}"
            
            for hour, minute, msg_key in tasks:
                if now.hour == hour and now.minute == minute:
                    if current_time_str not in last_sent:
                        if msg_key == "09:00":
                            send_message(get_morning_message())
                        else:
                            send_by_time(msg_key)
                        last_sent.add(current_time_str)
                    break 
            
            send_closing()
            time.sleep(30)

        except Exception as e:
            logger.error(f"🛑 Критическая ошибка в планировщике: {e}")
            time.sleep(60)

# ================= ОБРАБОТКА КОМАНД (ИСПРАВЛЕНО!) =================

def handle_command(event):
    # Самая надёжная проверка: работаем и с объектом, и со словарем
    if event.type != VkBotEventType.MESSAGE_NEW:
        return

    # Получаем объект сообщения универсально
    message_obj = None
    
    # Вариант 1: если event — это объект vk_api (у него есть .object)
    if hasattr(event, 'object'):
        message_obj = event.object.message
    # Вариант 2: если event — это словарь (частая проблема на хостингах)
    elif isinstance(event, dict) and 'object' in event and 'message' in event['object']:
        message_obj = event['object']['message']
    else:
        return  # Неизвестный формат — просто пропускаем

    # Теперь безопасно достаём текст
    text_raw = None
    if isinstance(message_obj, dict):
        text_raw = message_obj.get('text', '')
    elif hasattr(message_obj, 'text'):
        text_raw = message_obj.text
    else:
        return

    text = str(text_raw or '').lower().strip()
    
    # Достаём peer_id тоже универсально
    peer_id = None
    if isinstance(message_obj, dict):
        peer_id = message_obj.get('peer_id')
    elif hasattr(message_obj, 'peer_id'):
        peer_id = message_obj.peer_id
    else:
        return

    # Команда /время — отвечаем только если сообщение пришло в наш чат
    if peer_id == PEER_ID and text == "/время":
        now = datetime.datetime.now(TARGET_TZ)
        time_str = now.strftime("%H:%M")
        response = f"Текущее время по Перми: {time_str}\nЧасовой пояс бота: Asia/Yekaterinburg"
        send_message(response)

# ================= ЗАПУСК =================

if __name__ == "__main__":
    logger.info("🚀 Бот запускается...")
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    logger.info("🎧 Long Poll слушатель запущен. Ожидание событий...")

    try:
        for event in longpoll.listen():
            handle_command(event)
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка Long Poll: {e}", exc_info=True)
