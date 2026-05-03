import asyncio
import requests
from aiogram import Bot
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8303473938:AAFbgFCvvzLvK8ohaMBvvBaNkRyqxWhaHWM"
CHANNEL_ID = "@tonpricebloom"
COIN = "TON"

# --- ЦЕЙ БЛОК ДЛЯ ТОГО, ЩОБ RENDER НЕ ВИМИКАВ БОТА ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    server.serve_forever()
# ---------------------------------------------------

bot = Bot(token=TOKEN)

async def worker():
    while True:
        try:
            url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={COIN}USDT"
            r = requests.get(url, timeout=10)
            price = float(r.json()["result"]["list"][0]["lastPrice"])
            await bot.send_message(chat_id=CHANNEL_ID, text=f"📊 #{COIN}: {price:g} USDT", parse_mode="Markdown")
            print(f"Пост: {price}")
        except Exception as e:
            print(f"Помилка: {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    # Запускаємо веб-сервер у фоновому потоці
    threading.Thread(target=run_health_server, daemon=True).start()
    # Запускаємо бота
    asyncio.run(worker())
