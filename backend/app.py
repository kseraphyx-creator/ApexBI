import os
import json
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import firebase_admin
from firebase_admin import credentials, firestore
import anthropic

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-this")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

try:
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected successfully")
except Exception as e:
    print(f"⚠️ Firebase connection failed: {e}")
    db = None

anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY", "")
)

def success(data, status=200):
    return jsonify({"ok": True, "data": data}), status

def error(message, status=400):
    return jsonify({"ok": False, "error": message}), status

@app.route("/api/health", methods=["GET"])
def health():
    return success({
        "status": "APEX backend is running ✅",
        "version": "5.0.0",
        "firebase": "connected" if db else "disconnected"
    })

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    body = request.get_json()
    required = ["name", "biz", "email", "password"]
    for field in required:
        if not body.get(field):
            return error(f"Field '{field}' is required")
    email = body["email"].strip().lower()
    password = body["password"].strip()
    name = body["name"].strip()
    biz = body["biz"].strip()
    biz_type = body.get("bizType", "Kirana Store")
    city = body.get("city", "India")
    if len(password) < 6:
        return error("Password must be at least 6 characters")
    if not db:
        return error("Database not connected")
    existing = db.collection("users").where("email", "==", email).get()
    if len(existing) > 0:
        return error("Email already registered. Please sign in.")
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user_data = {
        "name": name, "biz": biz, "bizType": biz_type,
        "city": city, "email": email, "password": hashed_password,
        "createdAt": firestore.SERVER_TIMESTAMP
    }
    user_ref = db.collection("users").document()
    user_ref.set(user_data)
    user_id = user_ref.id
    token = create_access_token(identity=user_id)
    return success({
        "token": token,
        "user": {"id": user_id, "name": name, "biz": biz,
                 "bizType": biz_type, "city": city, "email": email}
    }, status=201)

@app.route("/api/auth/login", methods=["POST"])
def login():
    body = request.get_json()
    email = (body.get("email") or "").strip().lower()
    password = (body.get("password") or "").strip()
    if not email or not password:
        return error("Email and password are required")
    if not db:
        return error("Database not connected")
    users = db.collection("users").where("email", "==", email).get()
    if len(users) == 0:
        return error("Email or password is incorrect")
    user_doc = users[0]
    user_data = user_doc.to_dict()
    user_id = user_doc.id
    if not bcrypt.check_password_hash(user_data["password"], password):
        return error("Email or password is incorrect")
    token = create_access_token(identity=user_id)
    return success({
        "token": token,
        "user": {
            "id": user_id, "name": user_data.get("name"),
            "biz": user_data.get("biz"),
            "bizType": user_data.get("bizType", "Kirana Store"),
            "city": user_data.get("city", "India"), "email": email
        }
    })

@app.route("/api/data", methods=["GET"])
@jwt_required()
def get_data():
    user_id = get_jwt_identity()
    if not db:
        return error("Database not connected")
    doc = db.collection("business_data").document(user_id).get()
    if doc.exists:
        return success(doc.to_dict())
    return success(None)

@app.route("/api/data", methods=["POST"])
@jwt_required()
def save_data():
    user_id = get_jwt_identity()
    body = request.get_json()
    if not db:
        return error("Database not connected")
    db.collection("business_data").document(user_id).set(body)
    return success({"message": "Data saved successfully ✅"})

@app.route("/api/ai/chat", methods=["POST"])
@jwt_required()
def ai_chat():
    user_id = get_jwt_identity()
    body = request.get_json()
    message = (body.get("message") or "").strip()
    language = (body.get("language") or "english").lower()
    context = body.get("context", {})
    if not message:
        return error("Message is required")
    user_doc = db.collection("users").document(user_id).get() if db else None
    user_data = user_doc.to_dict() if user_doc and user_doc.exists else {}
    biz_type = user_data.get("bizType", "Kirana Store")
    city = user_data.get("city", "India")
    biz_name = user_data.get("biz", "Your Shop")
    name = user_data.get("name", "Shop Owner")
    context_str = ""
    if context:
        context_str = (
            f"Live business data:\n"
            f"- Revenue YTD: ₹{context.get('totalRevenue', 'N/A')}\n"
            f"- Expenses YTD: ₹{context.get('totalExpenses', 'N/A')}\n"
            f"- Profit Margin: {context.get('margin', 'N/A')}%\n"
            f"- Next month ML prediction: ₹{context.get('mlPrediction', 'N/A')}\n"
            f"- Top product: {context.get('topProduct', 'N/A')}\n\n"
        )
    if language == "hindi":
        lang_instruction = "IMPORTANT: Respond ENTIRELY in simple Hindi (Devanagari script)."
    else:
        lang_instruction = "Respond in simple English with occasional warm Hindi words."
    system_prompt = f"""You are APEX AI — a friendly expert advisor for Indian kirana stores.
Shop: {biz_name} | Type: {biz_type} | City: {city} | Owner: {name}
{context_str}{lang_instruction}
Answer in 3-4 sentences. Be specific and actionable. Use ₹ for currency."""
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": message}],
            system=system_prompt
        )
        return success({"reply": response.content[0].text})
    except Exception as e:
        return error(f"AI error: {str(e)}", 500)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"""
╔══════════════════════════════════════════╗
║   APEX Intelligence Backend v5.0         ║
║   Running on http://localhost:{port}         ║
╚══════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=True)