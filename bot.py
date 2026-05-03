
import asyncio
import requests
import threading
import datetime
import random
from aiogram import Bot
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАЛАШТУВАННЯ ---
TOKEN = "8303473938:AAGKqvPiWxvrsNolIBenVgObrFb2i0PiCWk"
CHANNEL_ID = "@tonpricebloom" 
COIN = "TON"

# Унікальний ID для цього запуску (щоб бачити дублі в логах)
RUN_ID = random.randint(1000, 9999)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")
    def log_message(self, format, *args):
        return 

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    print(f"[{RUN_ID}] ✅ Сервер здоров'я запущено", flush=True)
    server.serve_forever()

bot = Bot(token=TOKEN)

def get_price(coin):
    url = f"https://api.mexc.com/api/v3/ticker/price?symbol={coin.upper()}USDT"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return float(r.json()["price"])
    except:
        pass
    return None

async def worker():
    print(f"[{RUN_ID}] 🚀 Моніторинг {COIN} запущено. Чекаю початку хвилини...", flush=True)
    last_posted_minute = -1 # Запам'ятовуємо хвилину останнього поста

    while True:
        now = datetime.datetime.now()
        current_minute = now.minute

        # Постимо лише якщо настала нова хвилина і ми в її перших секундах
        if current_minute != last_posted_minute:
            try:
                price = get_price(COIN)
                if price:
                    text = f"📊 Price #{COIN}:\n\n**{price:g} USDT**"
                    await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
                    print(f"[{RUN_ID}] ✅ Пост о {now.strftime('%H:%M:%S')}: {price:g} USDT", flush=True)
                    last_posted_minute = current_minute
            except Exception as e:
                print(f"[{RUN_ID}] ❌ Помилка: {e}", flush=True)
        
        # Перевіряємо час кожну секунду для точності
        await asyncio.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    asyncio.run(worker())
