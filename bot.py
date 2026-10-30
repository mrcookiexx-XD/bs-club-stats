import json
import requests
from urllib.parse import quote
import os

# Мы берем данные из Secrets, в коде их нет!
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BS_API_TOKEN = os.environ['BS_API_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
CLUB_TAG = os.environ['CLUB_TAG']

STATE_FILE = 'state.json'

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'members': {}}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_club_data():
    url = f"https://api.brawlstars.com/v1/clubs/{quote(CLUB_TAG)}"
    headers = {"Authorization": f"Bearer {BS_API_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def get_player_data(player_tag):
    url = f"https://api.brawlstars.com/v1/players/{quote(player_tag)}"
    headers = {"Authorization": f"Bearer {BS_API_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'})

def main():
    state = load_state()
    prev_members = state.get('members', {})
    
    club_data = get_club_data()
    if not club_data:
        print("❌ Ошибка получения данных клуба")
        return
    
    curr_members = {m['tag']: m for m in club_data.get('members', [])}
    
    # Кто вышел
    for tag in set(prev_members.keys()) - set(curr_members.keys()):
        msg = f"🔴 <b>Игрок вышел из клуба!</b>\nНик: {prev_members[tag]['name']}\nТег: <code>{tag}</code>"
        send_telegram_message(msg)
        print(f"🔴 Вышел: {prev_members[tag]['name']}")
        
    # Кто зашел
    for tag in set(curr_members.keys()) - set(prev_members.keys()):
        m = curr_members[tag]
        ranked = "Н/Д"
        try:
            p_data = get_player_data(tag)
            if p_data:
                ranked = str(p_data.get('ranked', 'Н/Д'))
        except:
            pass
            
        msg = f"🟢 <b>Новый игрок в клубе!</b>\nНик: {m['name']}\nТег: <code>{tag}</code>\nКубки: {m['trophies']} 🏆\nРанг в ранговом: {ranked} 🎖️"
        send_telegram_message(msg)
        print(f"🟢 Зашел: {m['name']}")
        
    save_state({'members': {tag: {'name': m['name'], 'trophies': m['trophies']} for tag, m in curr_members.items()}})
    print("✅ Проверка завершена успешно!")

if __name__ == '__main__':
    main()