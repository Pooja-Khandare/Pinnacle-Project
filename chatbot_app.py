import re
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TRAVEL_DATA = {
    "Puri": {
        "description": "Puri is famous for Jagannath Temple, Golden Beach and nearby Konark Sun Temple.",
        "shopping": "You can shop at Swargadwar Market, Grand Road Market, Pipili Craft Village and local beach markets.",
        "food": "Dalma, Khaja, Seafood, Pitha and authentic Odia cuisine.",
        "places": "Jagannath Temple, Golden Beach, Konark Sun Temple, Chilika Lake and Swargadwar."
    },

    "North Bengal": {
        "description": "North Bengal is known for tea gardens, mountains and beautiful landscapes.",
        "shopping": "Darjeeling Tea, woolen products, handicrafts and local souvenirs.",
        "food": "Momos, Thukpa, Nepali dishes and Darjeeling tea.",
        "places": "Darjeeling, Kalimpong, Mirik, Lava and Lolegaon."
    },

    "Off Beat Locations": {
        "description": "Peaceful destinations surrounded by forests, rivers and nature.",
        "shopping": "Tribal handicrafts, bamboo products and local handmade goods.",
        "food": "Organic village meals and regional specialties.",
        "places": "Nature trails, eco-tourism villages, forests and rivers."
    }
}

sessions = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    user_id = data.get("user_id", "guest")
    message = data.get("message", "").strip()

    if user_id not in sessions:
        sessions[user_id] = {
            "state": "WELCOME"
        }

    session = sessions[user_id]

    if session["state"] == "WELCOME":
        session["state"] = "ASK_NAME"

        return jsonify({
            "reply": "👋 Hello! I'm Pinnacle Travel Bot. What is your name?"
        })

    elif session["state"] == "ASK_NAME":

        session["name"] = message
        session["state"] = "ASK_LOCATION"

        return jsonify({
            "reply": f"Nice to meet you {message}! 😊\n\nChoose a destination:\n• Puri\n• North Bengal\n• Off Beat Locations"
        })

    elif session["state"] == "ASK_LOCATION":

        chosen = None

        for loc in TRAVEL_DATA:
            if loc.lower() in message.lower():
                chosen = loc
                break

        if chosen:

            session["location"] = chosen
            session["state"] = "ASK_EMAIL"

            return jsonify({
                "reply": f"Great choice! 🌴 {chosen}\n\nPlease enter your email address."
            })

        return jsonify({
            "reply": "Please select Puri, North Bengal or Off Beat Locations."
        })

    elif session["state"] == "ASK_EMAIL":

        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", message):

            session["email"] = message
            session["state"] = "ASK_PHONE"

            return jsonify({
                "reply": "✅ Email accepted.\n\nPlease enter your 10-digit mobile number."
            })

        return jsonify({
            "reply": "❌ Invalid email format."
        })

    elif session["state"] == "ASK_PHONE":

        if re.match(r"^\d{10}$", message):

            session["phone"] = message
            session["state"] = "COMPLETED"

            return jsonify({
                "reply": f"✅ Registration completed!\n\nWelcome to {session['location']}.\nAsk me about shopping, food or places to visit."
            })

        return jsonify({
            "reply": "❌ Mobile number must contain exactly 10 digits."
        })

    elif session["state"] == "COMPLETED":

        location = session["location"]
        info = TRAVEL_DATA[location]

        msg = message.lower()

        if "shopping" in msg or "shop" in msg or "market" in msg:
            reply = info["shopping"]

        elif "food" in msg or "eat" in msg or "restaurant" in msg:
            reply = info["food"]

        elif "visit" in msg or "places" in msg or "tourist" in msg or "where" in msg:
            reply = info["places"]

        else:
            reply = info["description"]

        return jsonify({
            "reply": reply
        })

if __name__ == "__main__":
    app.run(debug=True)
    