import difflib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import database
import llm_adapter

load_dotenv()

database.init_db()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.txt"
MEMORY_WINDOW = 12
MIN_PASSWORD_LENGTH = 8


def _read_system_prompt() -> str:
    try:
        text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
        return text or "You are CodeMind AI, a meticulous code review assistant."
    except FileNotFoundError:
        return "You are CodeMind AI, a meticulous code review assistant."


def _to_iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _serialize_chat(row: Dict) -> Dict:
    return {
        "id": row["id"],
        "title": row.get("title"),
        "language": row.get("language"),
        "created_at": _to_iso(row.get("created_at")),
        "updated_at": _to_iso(row.get("updated_at")),
        "last_message_preview": row.get("last_message_preview", ""),
    }


def _serialize_message(row: Dict) -> Dict:
    return {
        "id": row["id"],
        "role": row["role"],
        "language": row.get("language"),
        "content": row.get("content", ""),
        "display_content": row.get("display_content"),
        "code_snapshot": row.get("code_snapshot"),
        "code_diff": row.get("code_diff"),
        "created_at": _to_iso(row.get("created_at")),
    }


def _default_chat_title() -> str:
    stamp = datetime.now().strftime("Session %b %d, %H:%M")
    return f"New review ({stamp})"


def _derive_chat_title(language: str, code: str) -> str:
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    if lines:
        snippet = lines[0]
        if len(snippet) > 60:
            snippet = snippet[:57] + "..."
        return snippet
    return f"{language.title()} review"


def _detect_provider(api_key: Optional[str], requested: Optional[str] = None) -> str:
    if requested:
        return requested
    if api_key:
        lowered = api_key.lower()
        if api_key.startswith("sk-") or "openai" in lowered:
            return "openai"
        if "claude" in lowered or lowered.startswith("sk-ant-") or lowered.startswith("gsk_"):
            return "claude"
    return os.getenv("DEFAULT_PROVIDER", "gemini")


def _compute_diff(previous: Optional[str], current: str) -> Optional[str]:
    if not previous:
        return None
    diff_lines = difflib.unified_diff(
        previous.splitlines(),
        current.splitlines(),
        fromfile="previous",
        tofile="current",
        lineterm="",
        n=3,
    )
    diff_text = "\n".join(diff_lines).strip()
    return diff_text or None


def _normalize_email(value: Optional[str]) -> str:
    if not value:
        return ""
    return value.strip().lower()


def _compose_user_content(language: str, code: str, code_diff: Optional[str], notes: Optional[str]) -> str:
    segments: List[str] = []
    segments.append(f"Language: {language}")
    segments.append("Code to review:")
    segments.append(f"```{language}\n{code}\n```")
    if code_diff:
        segments.append("Key changes since previous submission:")
        segments.append(f"```diff\n{code_diff}\n```")
    if notes:
        segments.append("Developer notes:")
        segments.append(notes)
    return "\n\n".join(segment for segment in segments if segment.strip())


def _build_conversation(history: List[Dict]) -> List[Dict[str, str]]:
    system_prompt = _read_system_prompt()
    conversation: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    recent = history[-MEMORY_WINDOW:]
    for message in recent:
        conversation.append({"role": message["role"], "content": message.get("content", "")})
    return conversation


def _update_chat_metadata(chat: Dict, chat_id: str, language: str, code: str) -> None:
    updates = {}
    if chat.get("language") != language:
        updates["language"] = language
        chat["language"] = language
    default_title_prefix = "New review"
    if chat.get("title") is None or chat.get("title", "").startswith(default_title_prefix):
        updates["title"] = _derive_chat_title(language, code)
        chat["title"] = updates["title"]
    if updates:
        database.update_chat(chat_id, **updates)


@app.route("/")
def index():
    return render_template("index.html", auth_email=session.get("user_email"))


@app.route("/api/chats", methods=["GET"])
def list_chat_sessions():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    chats = database.list_chats(user_id)
    payload = [_serialize_chat(row) for row in chats]
    return jsonify({"data": payload})


@app.route("/api/chats", methods=["POST"])
def create_chat_session():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    title = data.get("title") or _default_chat_title()
    language = data.get("language")
    chat = database.create_chat(title, language, user_id=user_id)
    return jsonify({"chat": _serialize_chat(chat)}), 201


@app.route("/api/chats/<chat_id>", methods=["GET"])
def get_chat_session(chat_id: str):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    chat = database.get_chat(chat_id, user_id=user_id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    messages = database.get_chat_messages(chat_id)
    payload = {
        "chat": _serialize_chat(chat),
        "messages": [_serialize_message(message) for message in messages],
    }
    return jsonify(payload)


@app.route("/api/chats/<chat_id>/messages", methods=["POST"])
def create_chat_message(chat_id: str):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    chat = database.get_chat(chat_id, user_id=user_id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404

    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    if not code:
        return jsonify({"error": "Code snippet is required."}), 400
    language = (data.get("language") or chat.get("language") or "text").strip().lower()
    notes = (data.get("notes") or "").strip()
    api_key = data.get("api_key")
    provider = _detect_provider(api_key, data.get("provider"))

    history = database.get_chat_messages(chat_id)
    previous_code = next(
        (
            message.get("code_snapshot")
            for message in reversed(history)
            if message["role"] == "user" and message.get("code_snapshot")
        ),
        None,
    )
    code_diff = _compute_diff(previous_code, code)
    user_content = _compose_user_content(language, code, code_diff, notes)
    user_record = database.add_message(
        chat_id,
        "user",
        user_content,
        language=language,
        display_content=code,
        code_snapshot=code,
        code_diff=code_diff,
    )
    history.append(user_record)
    _update_chat_metadata(chat, chat_id, language, code)

    conversation = _build_conversation(history)

    def generate():
        assistant_chunks: List[str] = []
        try:
            for chunk in llm_adapter.analyze_code(conversation, provider=provider, api_key=api_key):
                assistant_chunks.append(chunk)
                yield chunk
        except Exception as exc:
            error_text = f"\n[CodeMind error]: {exc}\n"
            assistant_chunks.append(error_text)
            yield error_text
        finally:
            final_text = "".join(assistant_chunks).strip()
            if final_text:
                database.add_message(
                    chat_id,
                    "assistant",
                    final_text,
                    language=language,
                    display_content=final_text,
                )

    return Response(generate(), mimetype="text/plain")


@app.route("/analyze", methods=["POST"])
def legacy_analyze():
    return jsonify({"error": "This endpoint has been replaced by /api/chats. Please update your client."}), 410


@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = _normalize_email(data.get("email"))
    password = (data.get("password") or "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "Please provide a valid email address."}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": f"Password must be at least {MIN_PASSWORD_LENGTH} characters."}), 400

    if database.get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409

    password_hash = generate_password_hash(password)
    user = database.create_user(email, password_hash)
    session.permanent = True
    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    return jsonify({"email": user["email"], "authenticated": True}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = _normalize_email(data.get("email"))
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = database.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials. Please try again."}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    return jsonify({"email": user["email"], "authenticated": True})


@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"authenticated": False})


@app.route("/auth/status", methods=["GET"])
def auth_status():
    email = session.get("user_email")
    return jsonify({"authenticated": bool(email), "email": email or ""})


if __name__ == "__main__":
    app.run(debug=True)
