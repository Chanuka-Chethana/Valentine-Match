from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
import sqlite3
import uuid
import requests
import datetime # ### NEW: වෙලාව බලාගන්න ඕන නිසා

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- ප්‍රශ්න 10 (වෙනසක් නෑ) ---
QUESTIONS_DATA = [
    {"id": 1, "q": "1. මම වැඩියෙන්ම කන්න කැමති?", "opts": ["කොත්තු / Fried Rice 🥘", "Pizza / Burger 🍕", "බත් සහ කරි 🍛", "Short-eats / Rolls 🥐"]},
    {"id": 2, "q": "2. නිවාඩු දවසක මම කරන්න කැමති?", "opts": ["නිදාගන්න එක 😴", "ෆිල්ම් බලන එක 🎬", "Travel කරන්න ✈️", "Game ගහන්න 🎮"]},
    {"id": 3, "q": "3. මට කේන්ති ගියාම?", "opts": ["කෑ ගහනවා 🤬", "පොඩ්ඩක් අඬනවා 😢", "කට වහන් ඉන්නවා 🤐", "එහෙම තරහ යන්නෑ 😇"]},
    {"id": 4, "q": "4. මගේ නරකම පුරුද්ද?", "opts": ["Phone එක ඔබන එක 📱", "රෑ වෙලා නිදාගන්න එක 🦉", "සල්ලි නාස්ති කරන එක 💸", "කම්මැලි කම 🦥"]},
    {"id": 5, "q": "5. මම කැමතිම Social Media එක?", "opts": ["Instagram 📸", "TikTok 🎵", "WhatsApp 💬", "Facebook 📘"]},
    {"id": 6, "q": "6. මට ලොතරැයියක් ඇදුනොත්?", "opts": ["වාහනයක් ගන්නවා 🚗", "රට යනවා ✈️", "බැංකුවේ දානවා 💰", "කන්න වියදම් කරනවා 🍔"]},
    {"id": 7, "q": "7. මගේ Love Language එක?", "opts": ["තෑගි (Gifts) 🎁", "කාලය (Time) ⏳", "උදව් (Helping) 🤝", "වචන (Words) 🗣️"]},
    {"id": 8, "q": "8. මම කැමතිම Music?", "opts": ["Love Songs ❤️", "Rap / Hip-hop 🎤", "Old Hits / Classics 🎸", "Baila (බයිලා) 💃"]},
    {"id": 9, "q": "9. මගේ Dream Partner කොහොමද?", "opts": ["ලස්සන වෙන්න ඕන 💅", "සල්ලි තියෙන්න ඕන 💵", "හොඳ ගතිගුණ ❤️", "ආතල් එකේ ඉන්න කෙනෙක් 😂"]},
    {"id": 10, "q": "10. වලියක් ගියාම මුලින්ම Sorry කියන්නේ?", "opts": ["මම (Me) 🙋", "එයා (You) 👉", "අපි දෙන්නම නෑ 👊", "වලි යන්නෑ අපි 🕊️"]}
]

def init_db():
    conn = sqlite3.connect('valentine.db')
    c = conn.cursor()
    # පරණ Tables
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes 
                 (id TEXT PRIMARY KEY, creator_name TEXT, 
                  a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, 
                  a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT,
                  secret_msg TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (quiz_id TEXT, player_name TEXT, score INTEGER)''')

    # ### NEW: Chat Table එක අලුතෙන් එකතු කලා
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (room_id TEXT, sender TEXT, msg TEXT, time TEXT)''')
                 
    conn.commit()
    conn.close()

init_db()

# Telegram Function (වෙනසක් නෑ)
def send_telegram_msg(message):
    try:
        BOT_TOKEN = "YOUR_BOT_TOKEN" 
        CHAT_ID = "YOUR_CHAT_ID"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url, timeout=2)
    except:
        pass

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "questions": QUESTIONS_DATA})

@app.post("/create")
def create_quiz(creator_name: str = Form(...), 
                a1: str = Form(...), a2: str = Form(...), a3: str = Form(...), a4: str = Form(...), a5: str = Form(...),
                a6: str = Form(...), a7: str = Form(...), a8: str = Form(...), a9: str = Form(...), a10: str = Form(...),
                secret_msg: str = Form(...)):
    
    quiz_id = str(uuid.uuid4())[:6]
    conn = sqlite3.connect('valentine.db')
    c = conn.cursor()
    c.execute("INSERT INTO quizzes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
              (quiz_id, creator_name, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, secret_msg))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/leaderboard/{quiz_id}", status_code=303)

@app.get("/quiz/{quiz_id}")
def take_quiz(request: Request, quiz_id: str):
    conn = sqlite3.connect('valentine.db')
    c = conn.cursor()
    c.execute("SELECT creator_name FROM quizzes WHERE id=?", (quiz_id,))
    res = c.fetchone()
    conn.close()
    
    if res:
        creator_name = res[0]
        custom_questions = []
        for item in QUESTIONS_DATA:
            q_text = item["q"]
            q_text = q_text.replace("මගේ", f"{creator_name}ගේ")
            q_text = q_text.replace("මට", f"{creator_name}ට")
            q_text = q_text.replace("මම", creator_name)
            custom_questions.append({"id": item["id"], "q": q_text, "opts": item["opts"]})
            
        return templates.TemplateResponse("quiz.html", {
            "request": request, "quiz_id": quiz_id, "creator": creator_name, "questions": custom_questions
        })
    return "Link Expired or Invalid!"

# main.py එකේ submit_quiz function එක හොයාගෙන මේක paste කරන්න

@app.post("/submit/{quiz_id}")
def submit_quiz(request: Request, quiz_id: str, player_name: str = Form(...), 
                a1: str = Form(...), a2: str = Form(...), a3: str = Form(...), a4: str = Form(...), a5: str = Form(...),
                a6: str = Form(...), a7: str = Form(...), a8: str = Form(...), a9: str = Form(...), a10: str = Form(...)):
    
    conn = sqlite3.connect('valentine.db')
    c = conn.cursor()
    c.execute("SELECT * FROM quizzes WHERE id=?", (quiz_id,))
    quiz = c.fetchone()
    
    answers = [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10]
    correct_answers = quiz[2:12] 
    
    score = 0
    for i in range(10):
        if answers[i] == correct_answers[i]:
            score += 1
            
    c.execute("INSERT INTO results VALUES (?, ?, ?)", (quiz_id, player_name, score))
    conn.commit()
    
    # Telegram Msg
    send_telegram_msg(f"💘 New Match ({player_name}): {score}/10")
    
    # --- LOGIC වෙනස් කළා ---
    room_id = None
    secret = None
    msg = ""

    if score == 10:
        msg = "WOW! PERFECT MATCH! 💍❤️"
        secret = quiz[12] # Secret Message එක පේන්නේ 10/10 නම් විතරයි
        room_id = f"{quiz_id}_{player_name}" # Chat Room එක හැදෙන්නේ 10/10 නම් විතරයි
    elif score >= 7:
        msg = "ළඟටම ආවා! ඒත් Chat එක Lock! 🔐"
    else:
        msg = "අපි යාළුවො විතරයි! Chat Locked 🔒"

    conn.close()

    return templates.TemplateResponse("result.html", {
        "request": request, "score": score, "player": player_name, 
        "msg": msg, "creator": quiz[1], "secret_msg": secret,
        "room_id": room_id  # <--- 10ක් ගත්තොත් විතරයි මේක යන්නේ. නැත්නම් None.
    })

@app.get("/leaderboard/{quiz_id}")
def view_results(request: Request, quiz_id: str):
    conn = sqlite3.connect('valentine.db')
    c = conn.cursor()
    c.execute("SELECT creator_name FROM quizzes WHERE id=?", (quiz_id,))
    creator = c.fetchone()[0]
    c.execute("SELECT player_name, score FROM results WHERE quiz_id=? ORDER BY score DESC", (quiz_id,))
    results = c.fetchall()
    conn.close()

    # ### NEW: Leaderboard එකට Room ID එකත් එක්ක Data යවනවා
    players_data = []
    for r in results:
        players_data.append({
            "name": r[0],
            "score": r[1],
            "room_id": f"{quiz_id}_{r[0]}" # Unique Room ID
        })

    share_link = f"{request.url.scheme}://{request.url.netloc}/quiz/{quiz_id}"
    
    # Template එකට 'players' කියලා යවනවා results වෙනුවට
    return templates.TemplateResponse("leaderboard.html", {
        "request": request, "players": players_data, "creator": creator, "share_link": share_link
    })

# --- ### NEW: CHAT ROUTES (මේ ටික අලුතෙන් එකතු කලේ) ---

@app.post("/send_chat")
def send_chat(room_id: str = Form(...), sender: str = Form(...), msg: str = Form(...)):
    conn = sqlite3.connect('valentine.db')
    c = conn.cursor()
    time = datetime.datetime.now().strftime("%H:%M")
    c.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (room_id, sender, msg, time))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/get_chat/{room_id}")
def get_chat(room_id: str):
    conn = sqlite3.connect('valentine.db')
    c = conn.cursor()
    c.execute("SELECT sender, msg, time FROM messages WHERE room_id=?", (room_id,))
    msgs = c.fetchall()
    conn.close()
    
    chat_list = [{"sender": m[0], "msg": m[1], "time": m[2]} for m in msgs]
    return JSONResponse(content=chat_list)