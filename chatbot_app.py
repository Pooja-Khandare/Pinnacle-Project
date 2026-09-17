import re
import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_NAME = "travel_chatbot.db"

# Added comprehensive details for location, distance, stay, menu, shopping, and view
TRAVEL_DATA = {
    "locations": {
        "Puri": {
            "description": "Beachfront properties close to Jagannath Temple, offering peaceful sunrise views and traditional Odia hospitality.",
            "distance": "60 km from Bhubaneswar Airport (BBI) and 3 km from Puri Railway Station.",
            "stay": "Ocean-view luxury rooms and traditional cottages with modern amenities.",
            "menu": "Authentic Odia Thali, Dalma, Pitha, fresh sea-food items, and continental breakfast.",
            "shopping": "Handwoven Pipili applique works, Pattachitra paintings, and local handicraft seashell items.",
            "view": "Stunning golden beach sunrise views and panoramic ocean backdrops.",
            "tariffs": {"Standard": 1500, "Deluxe": 2500},
            "faq": {
                "check-in": "Check-in time is 12:00 PM and check-out is 10:00 AM.",
                "refund": "Free cancellation up to 48 hours prior to check-in date.",
                "food": "Complimentary traditional breakfast included for Deluxe tier."
            }
        },
        "North Bengal": {
            "description": "Scenic hill views, lush green tea gardens, and cozy mountain wooden cottages.",
            "distance": "80 km from Bagdogra Airport (IXB) and 15 km from Darjeeling station.",
            "stay": "Cozy wooden mountain cottages overlooking deep valley slopes.",
            "menu": "Himalayan Thukpa, Momos, local organic greens, and fresh Darjeeling tea.",
            "shopping": "Handmade woolen shawls, organic Darjeeling tea packets, and local wooden artifacts.",
            "view": "Majestic snow-capped mountain ranges and rolling green tea garden valleys.",
            "tariffs": {"Standard": 1800, "Deluxe": 2500},
            "faq": {
                "check-in": "Check-in time is 1:00 PM.",
                "refund": "Free cancellation up to 72 hours prior to check-in.",
                "food": "Bonfire arrangements and local Darjeeling tea tasting included."
            }
        },
        "Off Beat Locations": {
            "description": "Secluded nature stays surrounded by deep forests and mountains away from city crowds.",
            "distance": "120 km from nearest major city hub; private jeep transfers available.",
            "stay": "Eco-friendly mud cottages and tree-houses immersed in nature.",
            "menu": "Organic farm-to-table rustic meals, millet rotis, and herbal forest teas.",
            "shopping": "Tribal handmade bamboo crafts, organic honey, and wild forest herbs.",
            "view": "Deep dense forest canopy, starry night skies, and quiet river streams.",
            "tariffs": {"Standard": 1500, "Deluxe": 2200},
            "faq": {
                "check-in": "Check-in time is 11:00 AM.",
                "refund": "Strictly non-refundable within 5 days of check-in.",
                "food": "Organic farm-to-table meals prepared by local hosts."
            }
        }
    }
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            state TEXT,
            location TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            sender TEXT,
            message TEXT,
            options TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user_session(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT state, location, email, phone FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"state": row[0], "location": row[1], "email": row[2], "phone": row[3]}
    return None

def save_user_session(user_id, session):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, state, location, email, phone)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, session["state"], session.get("location"), session.get("email"), session.get("phone")))
    conn.commit()
    conn.close()

def log_chat_message(user_id, sender, message, options=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_id, sender, message, options)
        VALUES (?, ?, ?, ?)
    ''', (user_id, sender, message, ",".join(options) if isinstance(options, list) else options))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get-history", methods=["POST"])
def get_history():
    data = request.json
    user_id = data.get("user_id")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message, options FROM chat_history WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    
    history = []
    for row in rows:
        opts = row[2].split(",") if row[2] else []
        history.append({"sender": row[0], "text": row[1], "options": opts})
        
    session = get_user_session(user_id)
    state = session["state"] if session else "WELCOME"
    
    conn.close()
    return jsonify({"history": history, "state": state})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")
    message = data.get("message", "").strip()

    session = get_user_session(user_id)
    if not session:
        session = {"state": "WELCOME", "location": None, "email": None, "phone": None}
        save_user_session(user_id, session)

    state = session["state"]
    reply_text = ""
    options = []

    if state == "WELCOME":
        session["state"] = "ASK_LOCATION"
        reply_text = "Welcome to Pinnacle Travel! 🌴 Please select your preferred target location:"
        options = ["Puri", "North Bengal", "Off Beat Locations"]
        save_user_session(user_id, session)
        log_chat_message(user_id, "Bot", reply_text, options)
        return jsonify({"state": session["state"], "reply": reply_text, "options": options})

    elif state == "ASK_LOCATION":
        matched_loc = None
        for loc in TRAVEL_DATA["locations"]:
            if loc.lower() in message.lower():
                matched_loc = loc
                break
        if matched_loc:
            session["location"] = matched_loc
            session["state"] = "CAPTURE_EMAIL"
            loc_info = TRAVEL_DATA["locations"][matched_loc]
            reply_text = f"Great choice! **{matched_loc}** - {loc_info['description']}\nTariffs: Standard (INR {loc_info['tariffs']['Standard']}), Deluxe (INR {loc_info['tariffs']['Deluxe']})\nPlease enter your valid Email Address:"
            options = []
        else:
            reply_text = "Please select a valid location from the options below:"
            options = ["Puri", "North Bengal", "Off Beat Locations"]
        
        save_user_session(user_id, session)
        log_chat_message(user_id, "You", message)
        log_chat_message(user_id, "Bot", reply_text, options)
        return jsonify({"state": session["state"], "reply": reply_text, "options": options})

    elif state == "CAPTURE_EMAIL":
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        log_chat_message(user_id, "You", message)
        if not re.match(email_pattern, message):
            reply_text = "❌ Invalid email format. Please enter a valid email address (e.g., user@gmail.com):"
            options = []
            log_chat_message(user_id, "Bot", reply_text, options)
            return jsonify({"state": session["state"], "reply": reply_text, "options": options})
        
        session["email"] = message
        session["state"] = "CAPTURE_PHONE"
        reply_text = "Thank you. Lastly, select country code and enter your 10-digit mobile number:"
        options = []
        save_user_session(user_id, session)
        log_chat_message(user_id, "Bot", reply_text, options)
        return jsonify({"state": session["state"], "reply": reply_text, "options": options})

    elif state == "CAPTURE_PHONE":
        cleaned_msg = re.sub(r'[\s-]', '', message)
        log_chat_message(user_id, "You", message)
        if not re.match(r'^\+\d{11,15}$', cleaned_msg):
            reply_text = "❌ Invalid phone number. Please enter a valid number with country code:"
            options = []
            log_chat_message(user_id, "Bot", reply_text, options)
            return jsonify({"state": session["state"], "reply": reply_text, "options": options})
        
        session["phone"] = cleaned_msg
        session["state"] = "COMPLETED"
        loc = session["location"]
        reply_text = f"Booking inquiry registered successfully for **{loc}**! Confirmation sent to {session['email']} & {session['phone']}. Our team will contact you shortly.\n\nYou can now ask about distance, stay, menu, shopping, view, check-in, or refund policy."
        options = ["Check-in info", "Refund policy", "Food details"]
        save_user_session(user_id, session)
        log_chat_message(user_id, "Bot", reply_text, options)
        return jsonify({"state": session["state"], "reply": reply_text, "options": options})

    elif state in ["COMPLETED", "POST_COMPLETION"]:
        session["state"] = "POST_COMPLETION"
        save_user_session(user_id, session)
        
        log_chat_message(user_id, "You", message)
        loc = session.get("location", "Puri")
        loc_data = TRAVEL_DATA["locations"].get(loc, TRAVEL_DATA["locations"]["Puri"])
        msg_lower = message.lower()
        
        # Expanded smart keyword matching for distance, stay, menu, shopping, view, and FAQs
        if "distance" in msg_lower or "far" in msg_lower or "travel" in msg_lower or "reach" in msg_lower:
            reply_text = f"**Distance Details for {loc}**: {loc_data['distance']}"
        elif "stay" in msg_lower or "room" in msg_lower or "property" in msg_lower or "accommodation" in msg_lower:
            reply_text = f"**Stay Options in {loc}**: {loc_data['stay']}"
        elif "menu" in msg_lower or "food" in msg_lower or "eat" in msg_lower or "breakfast" in msg_lower:
            reply_text = f"**Food & Menu Details for {loc}**: {loc_data['menu']}"
        elif "shop" in msg_lower or "market" in msg_lower or "buy" in msg_lower:
            reply_text = f"**Shopping Highlights in {loc}**: {loc_data['shopping']}"
        elif "view" in msg_lower or "scenery" in msg_lower or "sight" in msg_lower or "landscape" in msg_lower:
            reply_text = f"**Scenic Views in {loc}**: {loc_data['view']}"
        elif "check" in msg_lower or "time" in msg_lower:
            reply_text = f"**Check-in Info for {loc}**: {loc_data['faq']['check-in']}"
        elif "refund" in msg_lower or "cancel" in msg_lower:
            reply_text = f"**Refund Policy for {loc}**: {loc_data['faq']['refund']}"
        else:
            reply_text = f"Regarding your query about {loc}: {loc_data['description']} For custom requirements, our support team will reach out to you on {session.get('phone')}."

        options = ["Check-in info", "Refund policy", "Food details"]
        log_chat_message(user_id, "Bot", reply_text, options)
        return jsonify({"state": session["state"], "reply": reply_text, "options": options})

    return jsonify({"state": "COMPLETED", "reply": "Session completed.", "options": []})

@app.route("/end-chat", methods=["POST"])
def end_chat():
    data = request.json
    user_id = data.get("user_id")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ended"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)