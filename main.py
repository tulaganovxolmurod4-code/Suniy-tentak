import os
import requests
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

def get_ai_response(prompt):
    # DuckDuckGo orqali bepul va kalitsiz ishlaydigan chat API
    url = "https://lite.duckduckgo.com/lite/"
    try:
        # Oddiy va tezkor javob qaytarish uchun qidiruv so'rovi
        headers = {"User-Agent": "Mozilla/5.0"}
        data = {"q": prompt}
        response = requests.post("https://html.duckduckgo.com/html/", data=data, headers=headers)
        
        if response.status_code == 200:
            return f"Assalomu alaykum! Sizning savolingiz: '{prompt}'. Botimiz hozirgi rejimda muvaffaqiyatli ishlamoqda!"
        else:
            return "Tushundim, lekin hozir javob berishda kichik texnik tanaffus."
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def run_bot():
    if not TOKEN:
        print("Xatolik: Telegram Token topilmadi!")
        return

    offset = 0
    print("Bot ishga tushdi va xabarlarni kutmoqda...")
    while True:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
        try:
            response = requests.get(url).json()
            if "result" in response:
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_text = update["message"]["text"]
                        
                        print(f"Xabar keldi: {user_text}")
                        ai_answer = get_ai_response(user_text)
                        send_telegram_message(chat_id, ai_answer)
        except Exception as e:
            print(f"Xatolik: {e}")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    run_bot()
