"""
Flask chat API routes for the offline chatbot.
Exposes:
  POST /api/chat/message { session_id, message } -> { reply, emotion, sentiment, emergency }
  GET  /api/chat/history?session_id=... -> chat history
  GET  /api/chat/stats -> aggregate counts by emotion
"""
from flask import Blueprint, request, jsonify, session
from services.chatbot_service import chatbot
import datetime
import sqlite3
import os

chat_bp = Blueprint('chat', __name__)

# SQLite persistence under backend/db/sathi_chat.db
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "sathi_chat.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    role TEXT,
    message TEXT,
    emotion TEXT,
    sentiment TEXT,
    timestamp TEXT
)""")
conn.commit()


def _require_login():
    if 'user_id' not in session:
        return False
    return True


@chat_bp.route('/message', methods=['POST'])
def post_message():
    if not _require_login():
        return jsonify({"error": "Unauthorized"}), 401
    body = request.get_json(force=True, silent=True) or {}
    # Bind chat session to authenticated user by default
    user_force_id = str(session.get('user_id'))
    session_id = body.get("session_id") or f"user-{user_force_id}"
    message = body.get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    # analyze
    emo = chatbot.analyze_emotion(message)
    sent = chatbot.analyze_sentiment(message)

    # generate reply (safety check)
    reply, emergency = chatbot.generate_reply(session_id, message)

    # persist user message
    cur.execute(
        "INSERT INTO chat_logs (session_id, role, message, emotion, sentiment, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, "user", message, str(emo.get("label")), str(sent.get("label")), datetime.datetime.now().isoformat()),
    )
    conn.commit()

    # persist bot message
    cur.execute(
        "INSERT INTO chat_logs (session_id, role, message, emotion, sentiment, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, "bot", reply, None, None, datetime.datetime.now().isoformat()),
    )
    conn.commit()

    return jsonify({
        "reply": reply,
        "emotion": emo,
        "sentiment": sent,
        "emergency": emergency,
    })


@chat_bp.route('/history', methods=['GET'])
def history():
    if not _require_login():
        return jsonify([]), 401
    user_force_id = str(session.get('user_id'))
    session_id = request.args.get('session_id') or f"user-{user_force_id}"
    cur.execute(
        "SELECT role, message, emotion, sentiment, timestamp FROM chat_logs WHERE session_id=? ORDER BY id ASC",
        (session_id,),
    )
    rows = cur.fetchall()
    data = [
        {"role": r[0], "message": r[1], "emotion": r[2], "sentiment": r[3], "timestamp": r[4]}
        for r in rows
    ]
    return jsonify(data)


@chat_bp.route('/stats', methods=['GET'])
def stats():
    if not _require_login():
        return jsonify([]), 401
    cur.execute("SELECT emotion, COUNT(*) FROM chat_logs WHERE emotion IS NOT NULL GROUP BY emotion")
    data = cur.fetchall()
    return jsonify([{"emotion": r[0], "count": r[1]} for r in data])


@chat_bp.route('/health', methods=['GET'])
def health():
    from services.chatbot_service import chatbot
    return jsonify(chatbot.health_status())
