

from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os, json, re, random, requests
from datetime import datetime

# ---------------- Env & App Setup ----------------
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FLASK_SECRET = os.getenv("FLASK_SECRET", "change-me")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set in .env")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

app = Flask(__name__)
app.secret_key = FLASK_SECRET
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000", "http://localhost:5173"]
)

# ---------------- Supabase Client ----------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Memory Store ----------------
MEMORY_FILE = "memory.json"

def load_mem():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_mem(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

# memory schema: { "<user_email>": { "facts": [...], "last_seen": "ISO" } }
user_memory = load_mem()

def remember(user_email: str, text: str):
    """
    Extract simple user facts like name, preferences.
    """
    if not user_email:
        return
    entry = user_memory.get(user_email, {"facts": [], "last_seen": None})

    patterns = [
        r"\bmy name is\s+([A-Za-z][A-Za-z\s\-]{1,40})",
        r"\bi am\s+([A-Za-z][A-Za-z\s\-]{1,40})",
        r"\bi'm\s+([A-Za-z][A-Za-z\s\-]{1,40})",
        r"\bi like\s+([A-Za-z0-9 ,.&\-]{1,60})",
        r"\bmy role is\s+([A-Za-z][A-Za-z\s\-]{1,40})",
        r"\bcall me\s+([A-Za-z][A-Za-z\s\-]{1,40})",
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            fact = m.group(0).strip()
            if fact not in entry["facts"]:
                entry["facts"].append(fact)

    entry["last_seen"] = datetime.utcnow().isoformat()
    user_memory[user_email] = entry
    save_mem(user_memory)

def get_user_role(email: str) -> str:
    """
    Fetch role for a user from Supabase (table: user_perms with columns: email, role).
    Defaults to 'Employee' if no row found.
    """
    try:
        res = supabase.table("user_perms").select("role").eq("email", email).limit(1).execute()
        if res.data and isinstance(res.data, list) and len(res.data) > 0:
            role = (res.data[0].get("role") or "").strip()
            return role if role else "Employee"
    except Exception as e:
        print("Supabase role fetch error:", e)
    return "Employee"

# ---------------- Intent Detection ----------------
def detect_intent(user_query: str) -> str:
    q = user_query.lower()
    if any(word in q for word in ["code", "function", "script", "program", "sql", "api", "class", "loop"]) or "```" in q:
        return "coding"
    if any(word in q for word in ["error", "traceback", "exception", "bug", "fix", "issue"]):
        return "debugging"
    if any(word in q for word in ["solve", "integral", "derivative", "equation", "calculate", "sum", "matrix", "theorem"]):
        return "math"
    return "general"

# ---------------- LLM ----------------
def call_openrouter(messages, model='openai/gpt-4o-mini', temperature=0.5, max_tokens=1000):
    url = "https://openrouter.ai/api/v1/chat/completions"
    mdl = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": mdl,
        "messages": messages,
        "temperature": float(os.getenv("OPENROUTER_TEMPERATURE", temperature)),
        "max_tokens": max_tokens
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        data = resp.json()
        if resp.status_code != 200:
            print("OpenRouter error:", resp.status_code, data)
            return f"⚠️ LLM error: {data.get('error', {}).get('message', 'Unknown error')}"
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OpenRouter exception:", e)
        return f"⚠️ LLM exception: {str(e)}"

# ---------------- Smalltalk Helpers ----------------
CONFUSION = [
    "Hmm, could you rephrase that?",
    "I didn’t quite get that — can you clarify?",
    "Can you share a bit more detail?",
]

def greet_reply(name=None):
    tod = "day"
    h = datetime.now().hour
    if h < 12: tod = "morning"
    elif h < 18: tod = "afternoon"
    else: tod = "evening"
    base = f"Good {tod}"
    return f"{base}, {name}!" if name else f"{base}! How can I help you?"

def maybe_greeting(text):
    t = text.lower().strip()
    if re.search(r"\b(hi|hello|hey|good\s*(morning|afternoon|evening)|gm|ga|ge)\b", t):
        return True
    return False

# ---------------- Routes ----------------
@app.route("/set_session", methods=["POST"])
def set_session():
    try:
        data = request.get_json(force=True)
        email = (data.get("email") or "").strip()
        name = (data.get("name") or "").strip()

        if not email:
            return jsonify({"error": "Email is required"}), 400

        session["user_email"] = email
        session["user_name"] = name
        return jsonify({"message": "✅ Session set", "email": email, "name": name})
    except Exception as e:
        return jsonify({"error": f"Failed to set session: {str(e)}"}), 500

@app.route("/debug_session", methods=["GET"])
def debug_session():
    return jsonify({
        "user_email": session.get("user_email"),
        "user_name": session.get("user_name")
    })

@app.route("/chat", methods=["POST"])
def chat():
    try:
        payload = request.get_json(silent=True) or {}
        user_query = (payload.get("query") or payload.get("message") or "").strip()

        user_email = session.get("user_email")
        user_name = session.get("user_name")

        if not user_email:
            return jsonify({"reply": "❌ Please login first. Session email not found."}), 401
        if not user_query:
            return jsonify({"reply": random.choice(CONFUSION)}), 400

        # role from Supabase
        role = get_user_role(user_email)

        # update memory from current message
        remember(user_email, user_query)

        # gather memory facts
        facts = user_memory.get(user_email, {}).get("facts", [])

        # quick smalltalk
        if maybe_greeting(user_query):
            return jsonify({"reply": greet_reply(user_name)})

        # detect intent
        intent = detect_intent(user_query)

        # dynamic system prompt
        if intent == "coding":
            sys_role = "You are an expert coding assistant. Always return runnable code snippets in triple backticks ```language``` and include a short explanation."
        elif intent == "debugging":
            sys_role = "You are a debugging assistant. Analyze errors carefully and return corrected code snippets with explanations."
        elif intent == "math":
            sys_role = "You are a math tutor. Solve problems step-by-step and clearly show the final answer."
        else:
            sys_role = "You are a helpful assistant. Answer naturally, clearly, and in a human-friendly way."

        # build LLM system message
        sys = (
            f"{sys_role}\n\n"
            "Context info:\n"
            f"- User email: {user_email}\n"
            f"- User name: {user_name or 'Unknown'}\n"
            f"- User role: {role}\n"
            f"- Known user facts: {facts if facts else 'None'}\n"
            "Keep answers concise, clear, and friendly."
        )

        messages = [
            {"role": "system", "content": sys},
            {"role": "user", "content": user_query}
        ]

        reply = call_openrouter(messages)
        return jsonify({
            "reply": reply,
            "intent": intent,
            "user": {"email": user_email, "name": user_name, "role": role},
            "memory_facts": facts
        })

    except Exception as e:
        print("Chat error:", e)
        return jsonify({"reply": f"⚠️ Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
