
import asyncio
import requests
import threading
import sys
from aiogram import Bot
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАЛАШТУВАННЯ ---
TOKEN = "8303473938:AAHV_PpGGr8O2AHOEgrIG-1GIvxdV8nh5os"
CHANNEL_ID = "@tonpricebloom" 
COIN = "TON"
INTERVAL = 60  # Постити раз на хвилину

# --- СЕРВЕР ДЛЯ RENDER (ЩОБ БОТ НЕ ЗАСИНАВ) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return # Вимикаємо зайві логи сервера в консолі

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    print("✅ Веб-сервер здоров'я запущено на порту 8080", flush=True)
    server.serve_forever()

# --- ЛОГІКА БОТА ---
bot = Bot(token=TOKEN)

def get_price(coin):
    # Використовуємо MEXC, бо він стабільніше працює на Render
    url = f"https://api.mexc.com/api/v3/ticker/price?symbol={coin.upper()}USDT"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return float(r.json()["price"])
        else:
            print(f"⚠️ Помилка біржі: {r.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ Помилка мережі при запиті ціни: {e}", flush=True)
    return None

async def worker():
    print(f"🚀 Початок моніторингу {COIN}...", flush=True)
    while True:
        try:
            price = get_price(COIN)
            if price is not None:
                text = f"📊 Поточна ціна #{COIN}:\n\n**{price:g} USDT**"
                await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
                print(f"✅ Успішно надіслано: {price:g} USDT", flush=True)
            else:
                print("❌ Не вдалося отримати ціну, спробую через хвилину", flush=True)
        except Exception as e:
            print(f"❌ Помилка Telegram: {e}", flush=True)
        
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    # 1. Запускаємо сервер у фоновому потоці
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # 2. Запускаємо основний цикл бота
    print("🤖 Бот стартує...", flush=True)
    asyncio.run(worker())
