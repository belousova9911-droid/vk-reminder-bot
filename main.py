import os
import time
import threading
import schedule
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime

# ================== НАСТРОЙКИ (через переменные окружения) ==================
TOKEN = os.getenv("vk1.a.bdwEBSnWHqwRb1dVhD55g92MJq8rl2WrOj0onZHZTymVFt0l_pF7yKZf-Bp5Pn3k_or48t493-K2Kfkhbv-qbsI7Z_T3YNs60HJty5TBPnUyRXS-QEUdfcyssP6u2lHdB31SSg79BYbqRd5XIHtlwCl3JOZWgoL1KbEmHjhRjDAa6QSu6Un5DULs1qtIy5aVmUiVJgfBpYDmmMX5F6dm1g")          # Токен группы
GROUP_ID = int(os.getenv("241055687"))  # ID группы (без минуса)
PEER_ID = int(os.getenv("2000000001))    # Куда слать (peer_id чата)

if not all([TOKEN, GROUP_ID, PEER_ID]):
    raise ValueError("Не заданы VK_TOKEN, GROUP_ID или PEER_ID")

# ================== ИНИЦИАЛИЗАЦИЯ ==================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

def send_test():
    """Отправляет сообщение 'тест', но только начиная с 11:00"""
    now = datetime.now()
    
    # Отправляем только после 11:00
    if now.hour < 11:
        return
    
    try:
        vk.messages.send(
            peer_id=PEER_ID,
            message="тест",
            random_id=0
        )
        print(f"[{now.strftime('%H:%M:%S')}] Отправлено: тест")
    except Exception as e:
        print(f"[{now.strftime('%H:%M:%S')}] Ошибка отправки: {e}")

def run_scheduler():
    """Запускает планировщик в отдельном потоке"""
    # Каждые 10 минут
    schedule.every(10).minutes.do(send_test)
    
    # Сразу при старте тоже проверим (если уже после 11:00)
    send_test()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# ================== ЗАПУСК ==================
print("Бот запускается...")

# Планировщик в фоне
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

print("Планировщик запущен. Long Poll слушает...")

# Long Poll (держим процесс живым)
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.object.message:
        # Здесь можно добавить обработку команд, если понадобится
        pass