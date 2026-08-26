import os
import time
import threading
import schedule
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime
from zoneinfo import ZoneInfo          # ← эта строка обязательна

# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
PEER_ID = int(os.getenv("PEER_ID"))

if not all([TOKEN, GROUP_ID, PEER_ID]):
    raise ValueError("Не заданы VK_TOKEN, GROUP_ID или PEER_ID")

# Часовой пояс Перми
PERM_TZ = ZoneInfo("Asia/Yekaterinburg")

# ================== ИНИЦИАЛИЗАЦИЯ ==================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

def send_test():
    """Отправляет 'тест' каждые 10 минут, начиная с 11:00 по Перми"""
    now = datetime.now(PERM_TZ)
    
    # Отправляем только с 11:00 по Перми
    if now.hour < 11:
        return
    
    try:
        vk.messages.send(
            peer_id=PEER_ID,
            message="тест",
            random_id=0
        )
        print(f"[{now.strftime('%H:%M:%S')} Пермь] Отправлено: тест")
    except Exception as e:
        print(f"[{now.strftime('%H:%M:%S')} Пермь] Ошибка отправки: {e}")

def run_scheduler():
    """Планировщик в отдельном потоке"""
    schedule.every(10).minutes.do(send_test)
    
    # Проверяем сразу при запуске
    send_test()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# ================== ЗАПУСК ==================
print("Бот запускается...")
print(f"Текущее время по Перми: {datetime.now(PERM_TZ).strftime('%H:%M:%S')}")

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

print("Планировщик запущен (время по Перми). Long Poll слушает...")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.object.message:
        pass
