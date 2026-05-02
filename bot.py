import asyncio
import requests
from aiogram import Bot

# --- НАЛАШТУВАННЯ ---
TOKEN = "8303473938:AAFbgFCvvzLvK8ohaMBvvBaNkRyqxWhaHWM"
CHANNEL_ID = "@tonpricebloom"
COIN_ID = "the-open-network"  # Для CoinGecko TON називається саме так
INTERVAL = 60

bot = Bot(token=TOKEN)


class CoinGeckoParser:
    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/simple/price"

    def get_price(self, coin_id):
        params = {
            "ids": coin_id,
            "vs_currencies": "usd"
        }
        try:
            # CoinGecko зазвичай пропускає запити навіть з хостингів
            response = requests.get(self.url, params=params, timeout=15)

            if response.status_code != 200:
                print(f"CoinGecko Error: {response.status_code}")
                return None

            data = response.json()

            # Структура відповіді: {'the-open-network': {'usd': 5.45}}
            if coin_id in data:
                return float(data[coin_id]["usd"])
            else:
                print(f"ID {coin_id} не знайдено")
                return None

        except Exception as e:
            print(f"Помилка запиту: {e}")
            return None


async def post_price_to_channel():
    parser = CoinGeckoParser()
    print(f"Бот запущено. Моніторинг {COIN_ID} через CoinGecko...")

    while True:
        price = parser.get_price(COIN_ID)

        if price is not None:
            text = f"💎 Price #TON:\n\n**{price:g} USD**"
            try:
                await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
                print(f"Успішно відправлено: {price:g}")
            except Exception as e:
                print(f"Помилка Telegram: {e}")
        else:
            print("Ціну не отримано, чекаю наступної спроби...")

        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(post_price_to_channel())
    except KeyboardInterrupt:
        print("\nБот вимкнений.")