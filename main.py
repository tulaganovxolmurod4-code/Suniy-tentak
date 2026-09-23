import os
import requests
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

def get_ai_response(prompt):
    if not GROQ_API_KEY:
        return "Xatolik: Render'da GROQ_API_KEY kiritilmagan!"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Siz aqlli, yordamchi 3D robot assistentsiz. O'zbek tilida qisqa, aniq va xushmuomala javob bering."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Groq xatosi ({response.status_code}): Kalitni tekshiring."
    except Exception as e:
        return f"Ulanish vaqti tugadi: {str(e)}"

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
            response = requests.get(url, timeout=35).json()
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
