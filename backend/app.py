# give project details based on identity based access but not giving all project details and also not giving genral hi hello questions 
# from flask import Flask, request, jsonify, render_template, session
# from flask_session import Session
# import os, requests, re, json, random
# from dotenv import load_dotenv
# from langchain_community.document_loaders import TextLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import SentenceTransformerEmbeddings
# import chromadb
# from chromadb.config import Settings
# from supabase import create_client, Client
# from ast import literal_eval
# from flask_cors import CORS
# import traceback


# load_dotenv()
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment or .env file.")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# app = Flask(__name__)
# app.secret_key = 'your-secret-key'
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config["SESSION_PERMANENT"] = False
# CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:5173"])
# Session(app)

# # Use a persistent client to save the database to disk
# chroma_client = chromadb.PersistentClient(path="./chroma_db")
# collection = chroma_client.get_or_create_collection("company_docs")

# embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# MEMORY_FILE = "memory.json"
# CONFUSION_RESPONSES = [
#     "Hmm, I'm not quite sure what you mean. Could you rephrase it?",
#     "Can you please provide more details?",
#     "Let's try that again — can you explain it another way?",
#     "I'm here to help, but I need a bit more information from you.",
#     "Please clarify your question a little so I can assist better!"
# ]

# TABLES = {
#     "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status", 
#                 "assigned_to_emails", "client_name", "upload_documents", "project_scope", 
#                 "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility", 
#                 "role", "role_answers", "custom_questions", "custom_answers", "priority"],
#     "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
#     "user_memory": ["id", "user_id", "name", "known_facts"],
#     "user_perms": ["id", "name", "email", "password", "role", "permission_roles"]
# }

# def load_memory():
#     if os.path.exists(MEMORY_FILE):
#         with open(MEMORY_FILE, "r") as f:
#             return json.load(f)
#     return {}

# def save_memory(memory):
#     with open(MEMORY_FILE, "w") as f:
#         json.dump(memory, f, indent=2)

# def update_user_memory(user_input, memory):
#     match = re.search(r"\b(?:my name is|i am|i'm|this is|this side)\s+(\w+)", user_input, re.IGNORECASE)
#     if match:
#         memory["user_name"] = match.group(1).capitalize()
#     return memory

# def load_documents():
#     documents = []
#     if not os.path.exists("company_docs"):
#         return
#     for file in os.listdir("company_docs"):
#         path = os.path.join("company_docs", file)
#         if file.endswith(".pdf"):
#             loader = PyPDFLoader(path)
#         elif file.endswith(".txt"):
#             loader = TextLoader(path, encoding="utf-8")
#         else:
#             continue
#         documents.extend(loader.load())
#     if documents:
#         splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
#         texts = splitter.split_documents(documents)
#         for i, text in enumerate(texts):
#             collection.add(
#                 documents=[text.page_content],
#                 metadatas=[{"source": text.metadata.get("source", "company_docs")}],
#                 ids=[f"doc_{i}"]
#             )

# def get_context(query, k=3):
    
#     try:
#         results = collection.query(query_texts=[query], n_results=k)
#         if results and results['documents']:
#             return "\n".join(results['documents'][0])
#     except:
#         return ""
#     return ""

# def parse_user_query(user_input):
#     prompt = f"""
#     You are an AI that converts user questions into Supabase queries in JSON.

#     If the user asks:
#     - About login time or email → select from `employee_login`
#     - About remembered facts or chatbot memory → select from `user_memory`
#     - About their role or permissions → select from `user_perms`


#     User question: "{user_input}"

#     If the user is asking to list or fetch projects (e.g. "list out all projects", "my projects", "project list", "assigned work", etc), respond ONLY with a JSON like:

#     {{
#         "operation": "select",
#         "table": "projects",
#         "fields": ["project_name", "status","tech_stack","project_description","start_date","end_date","status","assigned_to_emails","client_name","upload_documents","project_scope","tech_stack","tech_stack_custom","leader_of_project","project_responsibility","role_answers","custom_questions","custom_answers","priority"],
#         "filters": {{}},
#         "limit": 10
#     }}

#     ❗️ If the question is about general world knowledge (e.g., city locations, definitions, greetings, jokes, etc) or can't be mapped to a valid table, respond with:
#     {{ "operation": "none" }}
#     """

#     try:
#         res = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "mistralai/mistral-7b-instruct",
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": 0.1,
#                 "max_tokens": 300
#             }
#         )
#         content = res.json()["choices"][0]["message"]["content"]
#         return literal_eval(content)
#     except:
#         return {"operation": "none"}

# def llm_response(user_input):
#     memory = load_memory()
#     memory = update_user_memory(user_input, memory)
#     save_memory(memory)

#     parsed = parse_user_query(user_input)
#     if parsed.get("operation") == "none":
#         return {"reply": "🤖 I couldn't understand that request. Can you rephrase it?"}

#     reply = query_supabase(parsed)
#     session["chat_history"].append({"role": "assistant", "content": reply})
#     session["chat_history"] = session["chat_history"][-5:]
#     return {"reply": reply}


# def normalize_date(value):
#     """
#     Attempts to normalize a date string to 'YYYY-MM-DD' format if possible.
#     Returns the original value if normalization fails.
#     """
#     import datetime
#     try:
#         # Try parsing common date formats
#         for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
#             try:
#                 dt = datetime.datetime.strptime(value, fmt)
#                 return dt.strftime("%Y-%m-%d")
#             except ValueError:
#                 continue
#     except Exception:
#         pass
#     return value

# def query_supabase(parsed):
#     try:
#         table = parsed.get("table")
#         filters = parsed.get("filters", {})
#         limit = parsed.get("limit", 10)

#         fields = parsed.get("fields", ["*"])
#         query = supabase.table(table).select(*fields)
#         try:
#             result = supabase.table(table).select("*").execute()
#         except Exception as e:
#             print("❌ Supabase timeout or error:", e)
#             return "⚠️ Supabase query failed due to a connection error."

#         for field, value in filters.items():
#             if not value:
#                 continue

#             # 🛠 Handle "contains" explicitly
#             if isinstance(value, dict) and "contains" in value:
#                 query = query.contains(field, [value["contains"]])
#             else:
#                 query = query.ilike(field, f"%{value}%")

#         print("🔎 Querying Supabase with filters:", filters)
#         result = query.execute()
#         data = result.data if hasattr(result, "data") else []

#         if not data:
#             return "⚠️ No matching records found."

#         formatted = []
#         seen_ids = set()  # ✅ Add this to avoid duplicates

#         for row in data[:limit]:
#             if row.get("id") in seen_ids:
#                 continue
#             seen_ids.add(row.get("id"))

#             lines = [
#                 f"{k.replace('_', ' ').capitalize()}: {v}"
#                 for k, v in row.items()
#                 if v not in [None, "", [], {}]
#             ]
#             formatted.append("• " + "\n  ".join(lines))


#         return "\n\n---\n\n".join(formatted)

#     except Exception as e:
#         print("❌ Supabase error:", e)
#         return f"❌ Supabase error: {str(e)}"


# def get_context(query, k=3):
#     if len(query.split()) <= 2:  # too short, likely not useful
#         return ""
#     try:
#         results = collection.query(query_texts=[query], n_results=k)
#         if results and results['documents']:
#             return "\n".join(results['documents'][0])
#     except:
#         return ""
#     return ""


# def build_messages(user_input, context, memory):
#     name = memory.get("user_name", "")
#     if name and not user_input.lower().startswith(name.lower()):
#         user_input = f"{name} asked: {user_input}"


#     session.setdefault("chat_history", [])
#     session["chat_history"].append({"role": "user", "content": user_input})

#     session["chat_history"] = session["chat_history"][-5:]
    
#     messages = [{"role": "system", "content": "You are a helpful assistant with access to internal documents."}]

#     if context:
#         messages.append({"role": "system", "content": f"Relevant context:\n{context}"})
    

    
#     messages.extend(session["chat_history"])
#     return messages


# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/set_session", methods=["POST"])
# def set_session():
#     data = request.get_json()
#     email = data.get("email")
#     name = data.get("name")

#     if email:
#         session["user_email"] = email
#         session["user_name"] = name
#         return jsonify({"message": "✅ Session set."})
#     return jsonify({"error": "❌ Email is required."}), 400


# @app.route("/clear_session", methods=["POST"])
# def clear_session():
#     session.clear()
#     return '', 204

# @app.route("/refresh_docs", methods=["POST"])
# def refresh_docs():
#     try:
#         existing_ids = collection.get()["ids"]
#         if existing_ids:
#             collection.delete(ids=existing_ids)
#         load_documents()
#         return jsonify({"message": "Documents refreshed successfully"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/debug_session")
# def debug_session():
#     return jsonify(dict(session))

# @app.route("/debug_projects")
# def debug_projects():
#     result = supabase.table("projects").select("*").contains("assigned_to_emails", ["@gmail.com"]).eq("assigned_role", "Employee").execute()
#     return jsonify(result.data)
# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json(force=True)
#         user_input = data.get("message", "").strip()
#         user_email = session.get("user_email")

#         if not user_email:
#             return jsonify({"reply": "❌ You are not logged in. Please login first."})
#         if not user_input:
#             return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})
#         if "what is my email" in user_input.lower() or "mail id" in user_input.lower():
#             return jsonify({"reply": f"📧 Your email is: {user_email}"})

#         # Load and update memory
#         memory = load_memory()
#         memory = update_user_memory(user_input, memory)
#         save_memory(memory)

#         # 👉 Try parsing the intent
#         parsed = parse_user_query(user_input)

#         if not parsed or parsed.get("operation") != "select" or "table" not in parsed:
#             context = get_context(user_input)
#             fallback_messages = build_messages(user_input, context, memory)
#             res = requests.post(
#                 "https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "mistralai/mistral-7b-instruct",
#                     "messages": fallback_messages,
#                     "temperature": 0.5,
#                     "max_tokens": 500
#                 }
#             )
#             reply = res.json()["choices"][0]["message"]["content"]
#             return jsonify({"reply": reply})


#         table = parsed.get("table")

#       # 🧠 Fetch user role
#         user_role_result = supabase.table("user_perms").select("role").eq("email", user_email).execute()
#         user_role = user_role_result.data[0]["role"] if user_role_result.data else "Employee"
#         # if table == "projects":
#         #     if user_role.lower() == "employee":
#         #         parsed["filters"]["assigned_to_emails"] = {"contains": user_email}
#         if table == "projects":
#             if user_role.lower() == "employee":
#                 parsed["filters"]["assigned_to_emails"] = {"contains": user_email}
#             elif user_role.lower() == "hr":
#                 parsed["filters"]["assigned_role"] = "employee"
#             elif user_role.lower() == "admin":
#                 pass
#             # Admin sees all projects — no filters


#         reply = query_supabase(parsed)
#         # Prevent accidental context leakage or repetition
#         if reply.strip() == user_input.strip():
#             reply = random.choice(CONFUSION_RESPONSES)


#         if parsed.get("table") in ["projects", "employee_login", "user_memory", "user_perms"]:
#             if not reply or "⚠️" in reply or "❌" in reply or "No matching" in reply:
#                 return jsonify({"reply": f"🔒 No data found in `{parsed.get('table')}` for your account."})

#         return jsonify({"reply": reply})

#     except Exception as e:
#         print("❌ Chat Exception:", e)
#         import traceback; traceback.print_exc()
#         try:
#             fallback_messages = build_messages(user_input, "", memory)
#             fallback_res = requests.post(
#                 "https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "mistralai/mistral-7b-instruct",
#                     "messages": fallback_messages,
#                     "temperature": 0.5,
#                     "max_tokens": 500
#                 }
#             )
#             reply = fallback_res.json()["choices"][0]["message"]["content"]
#         except:
#             reply = "⚠️ Internal server error. Please try again later."

#         return jsonify({"reply": reply})

# # @app.route("/chat", methods=["POST"])
# # def chat():
# #     try:
# #         data = request.get_json(force=True)
# #         user_input = data.get("message", "").strip()
# #         print("User input:", user_input)  # Debug

# #         if not user_input:
# #             return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

# #         memory = load_memory()
# #         memory = update_user_memory(user_input, memory)
# #         save_memory(memory)

# #         parsed = parse_user_query(user_input)
# #         print("Parsed:", parsed)  # Debug
# #         user_email = session.get("user_email")
# #         if not user_email:
# #             raise Exception("User not logged in")

# #         # ✅ STEP: Get role from Supabase
# #         role_data = supabase.table("user_perms").select("role").eq("email", user_email).execute()
# #         user_role = role_data.data[0]["role"] if role_data.data else "Employee"

# #         if parsed.get("operation") != "none":
# #             reply = query_supabase(parsed)
# #             print("Supabase reply:", reply)  # Debug
# #             if "❌" in reply or "⚠️" in reply or "No matching records" in reply:
# #                 raise Exception("Fallback to LLM")
# #         else:
# #             raise Exception("Not a DB question")

# #     except Exception as e:
# #         print("Exception:", e)  # Debug
# #         context = get_context(user_input)
# #         messages = build_messages(user_input, context, memory)
# #         res = requests.post(
# #             "https://openrouter.ai/api/v1/chat/completions",
# #             headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
# #             json={"model": "mistralai/mistral-7b-instruct", "messages": messages, "temperature": 0.6, "max_tokens": 500}
# #         )
# #         reply = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else random.choice(CONFUSION_RESPONSES)
    
# #     user_email = session.get("user_email")
# #     if not user_email:
# #         return jsonify({"reply": "❌ You are not logged in. Please login first."})

# #     reply = remove_emojis(reply)
# #     session["chat_history"].append({"role": "assistant", "content": reply})
# #     session["chat_history"] = session["chat_history"][-5:]
# #     return jsonify({"reply": reply})

# # @app.route("/chat", methods=["POST"])
# # def chat():
# #     try:
# #         data = request.get_json(force=True)
# #         user_input = data.get("message", "").strip()
# #         if not user_input:
# #             return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

# #         memory = load_memory()
# #         memory = update_user_memory(user_input, memory)
# #         save_memory(memory)

# #         parsed = parse_user_query(user_input)
# #         reply = ""

# #         # 🔐 Step 1: Get latest logged-in user from Supabase
# #         result = supabase.table("employee_login").select("email").order("login_time", desc=True).limit(1).execute()
# #         if not result.data:
# #             raise Exception("No active login")
# #         user_email = result.data[0]["email"]

# #         # 🔐 Step 2: Get that user's role
# #         user_data = supabase.table("user_perms").select("role").eq("email", user_email).execute()
# #         user_role = user_data.data[0]["role"] if user_data.data else "Employee"

# #         # ✅ Step 3: Filter project access based on role
# #         if parsed.get("operation") != "none" and parsed.get("table") == "projects":
# #             filters = parsed.get("filters", {})

# #             if user_role == "Employee":
# #                 filters["assigned_to"] = user_email
# #             elif user_role == "Hr":
# #                 filters["assigned_role"] = "Employee"
# #             # Admin gets full access

# #             parsed["filters"] = filters
# #             reply = query_supabase(parsed)

# #             # Fallback if query fails
# #             if "❌" in reply or "⚠️" in reply or "No matching records" in reply:
# #                 raise Exception("Fallback to LLM")
# #         elif parsed.get("operation") != "none":
# #             # Valid operation, but not about projects
# #             reply = query_supabase(parsed)
# #         else:
# #             raise Exception("Not a DB question")

# #     except Exception as e:
# #         context = get_context(user_input)
# #         messages = build_messages(user_input, context, memory)
# #         res = requests.post(
# #             "https://openrouter.ai/api/v1/chat/completions",
# #             headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
# #             json={"model": "mistralai/mistral-7b-instruct", "messages": messages, "temperature": 0.6, "max_tokens": 500}
# #         )
# #         reply = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else random.choice(CONFUSION_RESPONSES)

# #     reply = remove_emojis(reply)
# #     session["chat_history"].append({"role": "assistant", "content": reply})
# #     session["chat_history"] = session["chat_history"][-5:]
# #     return jsonify({"reply": reply})

# if __name__ == "__main__":
#     if collection.count() == 0:
#         load_documents()
#     app.run(debug=True)


# code 13/8
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import os, requests, re, json, random, traceback
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from chromadb.config import Settings
from supabase import create_client, Client
from ast import literal_eval
from flask_cors import CORS
import traceback

# ---------------- Load Environment Variables ----------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print(f"Loaded OPENROUTER_API_KEY: '{OPENROUTER_API_KEY}'")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set — please check your .env")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# ---------------- Initialize Clients ----------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'")
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:5173"])
Session(app)

# Persistent ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("company_docs")

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

MEMORY_FILE = "memory.json"
CONFUSION_RESPONSES = [
    "Hmm, I'm not quite sure what you mean. Could you rephrase it?",
    "Can you please provide more details?",
    "Let's try that again — can you explain it another way?",
    "I'm here to help, but I need a bit more information from you.",
    "Please clarify your question a little so I can assist better!"
]
# Known Supabase tables (schema)
TABLES = {
 "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status", 
                "assigned_to_emails", "client_name", "upload_documents", "project_scope", 
                "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility", 
                "role", "role_answers", "custom_questions", "custom_answers", "priority"],
    "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
    "user_memory": ["id", "user_id", "name", "known_facts"],
    "user_perms": ["id", "name", "email", "password", "role", "permission_roles"]
   
}

# # ---------------- Memory Management ----------------
# def load_memory():
#     if os.path.exists(MEMORY_FILE):
#         with open(MEMORY_FILE, "r") as f:
#             return json.load(f)
#     return {}

# def save_memory(memory):
#     with open(MEMORY_FILE, "w") as f:
#         json.dump(memory, f, indent=2)

# def update_user_memory(user_input, memory):
#     match = re.search(r"\b(?:my name is|i am|i'm|this is|this side)\s+(\w+)", user_input, re.IGNORECASE)
#     if match:
#         memory["user_name"] = match.group(1).capitalize()
#     return memory

# ---------------- Document Processing ----------------
def load_documents():
    documents = []
    if not os.path.exists("company_docs"):
        return
    for file in os.listdir("company_docs"):
        path = os.path.join("company_docs", file)
        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
        else:
            continue
        documents.extend(loader.load())
    if documents:
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
        texts = splitter.split_documents(documents)
        for i, text in enumerate(texts):
            collection.add(
                documents=[text.page_content],
                metadatas=[{"source": text.metadata.get("source", "company_docs")}],
                ids=[f"doc_{i}"]
            )

def get_context(query, k=3):
    if len(query.split()) <= 2:
        return ""
    try:
        results = collection.query(query_texts=[query], n_results=k)
        if results and results.get('documents'):
            return "\n".join(results['documents'][0])
    except:
        return ""
    return ""

# ---------------- AI Query Parsing ----------------
def call_openrouter(messages, temperature=0.5, max_tokens=500):
    """Centralized call to OpenRouter with error handling."""
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {'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'}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=15
        )
        if res.status_code != 200:
            print(f"⚠️ OpenRouter API error {res.status_code}: {res.text}")
            return None
        data = res.json()
        if "choices" not in data:
            print("⚠️ Missing 'choices' in API response:", data)
            return None
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Exception calling OpenRouter:", e)
        traceback.print_exc()
        return None

def parse_user_query(user_input):
    schema = "\n".join([f"{table}: {', '.join(cols)}" for table, cols in TABLES.items()])

    # Force-match if user explicitly mentions 'project'
    if "project" in user_input.lower():
        return {
            "operation": "select",
            "table": "projects",
            "fields": [
                "project_name", "status", "tech_stack", "project_description",
                "start_date", "end_date", "assigned_to_emails", "client_name",
                "project_scope", "tech_stack_custom", "leader_of_project",
                "project_responsibility", "role_answers", "custom_questions",
                "custom_answers", "priority"
            ],
            "filters": {"project_name": user_input.replace("details of", "").replace("project", "").strip()},
            "limit": 10
        }

    # Else, fall back to LLM parsing
    prompt = f"""You are connected to a Supabase database with these tables:
    {schema}

    User asked: "{user_input}"

    Extract operation, table, fields, filters, limit.
    If not matching, return {{ "operation": "none" }}.
    """

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 300
            }
        )
        content = res.json()["choices"][0]["message"]["content"]
        return literal_eval(content)
    except:
        return {"operation": "none"}


# ---------------- llm response ----------------
def llm_response(user_input):
    # memory = load_memory()
    # memory = update_user_memory(user_input, memory)
    # save_memory(memory)

    parsed = parse_user_query(user_input)
    if parsed.get("operation") == "none":
        return {"reply": "🤖 I couldn't understand that request. Can you rephrase it?"}

    reply = query_supabase(parsed)
    session({"role": "assistant", "content": reply})
    return {"reply": reply}

# ---------------- Supabase Query ----------------

# def query_supabase(parsed):
#     try:
#         table = parsed.get("table")
#         filters = parsed.get("filters", {}) or {}
#         operation = parsed.get("operation", "select")
#         limit = parsed.get("limit", 10)
#         fields = parsed.get("fields", ["*"])
#         user_email = session.get("user_email", "")
#         user_role = "Employee"

#         # Get role from Supabase
#         role_res = supabase.table("user_perms").select("role").eq("email", user_email).execute()
#         if role_res.data:
#             user_role = role_res.data[0].get("role", "Employee")

#         print(f"🔍 Querying table: {table}, filters: {filters}, role: {user_role}, email: {user_email}")

#         # -------------------------
#         # Build initial query
#         # -------------------------
#         query = supabase.table(table).select("*")
#         for field, value in filters.items():
#             if not value:
#                 continue
#             if isinstance(value, dict) and "contains" in value:
#                 query = query.contains(field, [value["contains"]])
#             else:
#                 query = query.ilike(field, f"%{value}%")

#         # Role restrictions for projects
#         if table == "projects" and user_role.lower() == "employee":
#             query = query.contains("assigned_to_emails", [user_email])

#         data = query.limit(limit).execute().data or []

#         # -------------------------
#         # Fuzzy Search Fallback
#         # -------------------------
#                # -------------------------
#         # Fuzzy Search Fallback (for all project fields)
#         # -------------------------
#         if not data and table == "projects" and filters:
#             print("🔍 No results — trying fuzzy search on all fields...")
            
#             fuzzy_query = supabase.table(table).select("*")

#             for field, original_value in filters.items():
#                 if not original_value:
#                     continue
                
#                 # Extract keywords and remove filler words
#                 filler_words = {"give", "only", "details", "about", "project", "projects", "info"}
#                 keywords = [w for w in re.findall(r'\w+', str(original_value)) if w.lower() not in filler_words]

#                 if keywords:
#                     main_keyword = keywords[0]
#                     print(f"🔍 Fuzzy search retry on field '{field}' with keyword: {main_keyword}")
#                     fuzzy_query = fuzzy_query.ilike(field, f"%{main_keyword}%")

#             # Apply role restriction for employees
#             if user_role.lower() == "employee":
#                 fuzzy_query = fuzzy_query.contains("assigned_to_emails", [user_email])

#             data = fuzzy_query.limit(limit).execute().data or []

#         # -------------------------
#         # Return results
#         # -------------------------
#         if not data:
#             return "⚠️ No matching records found."

#         formatted = []
#         for row in data:
#             is_assigned = user_email in (row.get("assigned_to_emails") or [])
#             if table == "projects" and not (is_assigned or user_role.lower() in ["admin", "hr", "manager"]):
#                 details = [
#                     f"Project Name: {row.get('project_name', 'N/A')}",
#                     f"Status: {row.get('status', 'N/A')}",
#                     "⚠️ You do not have permission to view full details."
#                 ]
#             else:
#                 details = [
#                     f"{k.replace('_', ' ').title()}: {v}"
#                     for k, v in row.items()
#                     if v not in [None, "", [], {}]
#                 ]
#             formatted.append("• " + "\n  ".join(details))

#         return "\n\n---\n\n".join(formatted)

#     except Exception as e:
#         print("❌ Supabase error:", e)
#         traceback.print_exc()
#         return f"❌ Supabase error: {str(e)}"
# ---------------- Supabase Query ----------------
def query_supabase(parsed):
    try:
        table = parsed.get("table")
        filters = parsed.get("filters", {}) or {}
        operation = parsed.get("operation", "select")
        limit = parsed.get("limit", 10)
        fields = parsed.get("fields", ["*"])
        user_email = session.get("user_email", "")
        user_role = "Employee"

        # Get role from Supabase
        role_res = supabase.table("user_perms").select("role").eq("email", user_email).execute()
        if role_res.data:
            user_role = role_res.data[0].get("role", "Employee")

        print(f"🔍 Querying table: {table}, filters: {filters}, role: {user_role}, email: {user_email}")

        # Build query
        query = supabase.table(table).select("*")
        for field, value in filters.items():
            query = query.ilike(field, f"%{value}%")


        for field, value in filters.items():
            if not value:
                continue
            if isinstance(value, dict) and "contains" in value:
                # For array fields like assigned_to_emails
                query = query.contains(field, [value["contains"]])
            else:
                # Case-insensitive partial match
                query = query.ilike(field, f"%{value}%")

        # Role restrictions for projects
        if table == "projects" and user_role.lower() == "employee":
            query = query.contains("assigned_to_emails", [user_email])

        data = query.limit(limit).execute().data or []
        if not data:
            return "⚠️ No matching records found."

        formatted = []
        for row in data:
            is_assigned = user_email in (row.get("assigned_to_emails") or [])
            if table == "projects" and not (is_assigned or user_role.lower() in ["admin", "hr", "manager"]):
                details = [
                    f"Project Name: {row.get('project_name', 'N/A')}",
                    f"Status: {row.get('status', 'N/A')}",
                    "⚠️ You do not have permission to view full details."
                ]
            else:
                details = [
                    f"{k.replace('_', ' ').title()}: {v}"
                    for k, v in row.items()
                    if v not in [None, "", [], {}]
                ]
            formatted.append("• " + "\n  ".join(details))

        return "\n\n---\n\n".join(formatted)

    except Exception as e:
        print("❌ Supabase error:", e)
        traceback.print_exc()
        return f"❌ Supabase error: {str(e)}"


# ---------------- Routes ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_session", methods=["POST"])
def set_session():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    if email:
        session["user_email"] = email
        session["user_name"] = name
        return jsonify({"message": "✅ Session set."})
    return jsonify({"error": "❌ Email is required."}), 400

@app.route("/debug_session")
def debug_session():
    return jsonify(dict(session))

# this is latest documents based chat rote
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_input = data.get("message", "").strip()
        user_email = session.get("user_email")

        if not user_email:
            return jsonify({"reply": "❌ You are not logged in. Please login first."})
        if not user_input:
            return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

        # 1️⃣ Special case: List all projects
        if re.search(r"\b(list|show)\b.*\bprojects\b", user_input, re.IGNORECASE):
            parsed = {
                "operation": "select",
                "table": "projects",
                "fields": ["*"],
                "filters": {},
                "limit": 20
            }
            return jsonify({"reply": query_supabase(parsed)})

        # 2️⃣ Parse query dynamically
        parsed = parse_user_query(user_input)
        print(f"🛠 Parsed query: {parsed}")

        # 3️⃣ If AI says no DB operation → fallback with document context
        if not parsed or parsed.get("operation") != "select" or "table" not in parsed:
            doc_context = get_context(user_input)
            user_name = session.get("user_name", "")
            system_info = f"You are a helpful assistant. Known user email: {user_email}, name: {user_name or 'not set'}."

            # Include doc context if found
            if doc_context:
                system_info += f"\n\nRelevant internal company documents:\n{doc_context}"

            fallback_messages = [
                {"role": "system", "content": system_info},
                {"role": "user", "content": user_input}
            ]
            reply = call_openrouter(fallback_messages)
            return jsonify({"reply": reply or "⚠️ Unable to process your request right now."})

        # 4️⃣ Auto-add project name filter if mentioned
        if parsed.get("table") == "projects" and parsed.get("filters", {}).get("project_name"):
            original_val = parsed["filters"]["project_name"].strip()
            match = re.search(r"\b([a-zA-Z0-9\s]+?)\s*(?:project|details|info)?$", original_val, re.IGNORECASE)
            if match:
                clean_name = match.group(1).strip()
                if clean_name and clean_name.lower() not in ["give only", "only", "all"]:
                    parsed["filters"]["project_name"] = clean_name
                else:
                    parsed["filters"].pop("project_name")

        # 5️⃣ Query Supabase
        reply = query_supabase(parsed)

        # 6️⃣ If Supabase says "No matching records found", try documents as fallback
        if reply.strip().startswith("⚠️ No matching records"):
            doc_context = get_context(user_input)
            if doc_context:
                user_name = session.get("user_name", "")
                system_info = f"You are a helpful assistant. Known user email: {user_email}, name: {user_name or 'not set'}.\n\nRelevant internal company documents:\n{doc_context}"
                fallback_messages = [
                    {"role": "system", "content": system_info},
                    {"role": "user", "content": user_input}
                ]
                reply = call_openrouter(fallback_messages) or reply

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Chat Exception:", e)
        traceback.print_exc()
        return jsonify({"reply": "⚠️ Internal server error. Please try again later."}), 500


# this /chat() code is working but not fetch exactly project details from supabase
# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json(force=True)
#         user_input = data.get("message", "").strip()
#         if not user_input:
#             return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

#         # --- Validate session ---
#         user_email = session.get("user_email")
#         if not user_email:
#             return jsonify({"reply": "❌ You are not logged in. Please login first."}), 401

#         # --- Keep memory ---
#         # memory = load_memory()
#         # memory = update_user_memory(user_input, memory)
#         # save_memory(memory)

#         # --- 1️⃣ Special case: list all projects ---
#         if ("list" in user_input.lower() or "show" in user_input.lower()) and "projects" in user_input.lower():
#             result = supabase.table("projects").select("*").execute()
#             if result.data:
#                 lines = []
#                 for p in result.data:
#                     name = p.get("project_name", "Unnamed Project")
#                     status = p.get("status", "Unknown")
#                     client = p.get("client_name", "N/A")
#                     lines.append(f"• {name} — Status: {status} — Client: {client}")
#                 return jsonify({"reply": "Here are all projects:\n" + "\n".join(lines)})
#             else:
#                 return jsonify({"reply": "⚠️ No projects found."})

#         # --- 2️⃣ Special case: specific project details ---
#         # --- Special case: specific project details ---
#         if "project name:" in user_input.lower():
#             project_name = user_input.split("project name:")[-1].strip()
#             if project_name:
#                 # Get user role
#                 role_res = supabase.table("user_perms").select("role").eq("email", user_email).execute()
#                 role = role_res.data[0]["role"] if role_res.data else "Employee"

#                 # Search ONLY projects matching name AND assigned to the user (unless HR/admin)
#                 query = supabase.table("projects").select("*").ilike("project_name", f"%{project_name}%")

#                 if role.lower() == "employee":
#                     # Restrict to projects assigned to this user
#                     query = query.contains("assigned_to_emails", [user_email])

#                 elif role.lower() == "hr":
#                     # HR can see employee projects
#                     query = query.ilike("assigned_role", "employee")

#                 result = query.execute()

#                 if not result.data:
#                     # Check if project exists but not assigned to this user
#                     exists_check = supabase.table("projects").select("project_name").ilike("project_name", f"%{project_name}%").execute()
#                     if exists_check.data:
#                         return jsonify({"reply": f"⚠️ You do not have permission to view details for '{project_name}'."})
#                     return jsonify({"reply": f"⚠️ No project found with name '{project_name}'."})

#                 # Format output for matched + allowed project(s)
#                 formatted = []
#                 for row in result.data:
#                     lines = [
#                         f"{k.replace('_', ' ').title()}: {v}"
#                         for k, v in row.items()
#                         if v not in [None, "", [], {}]
#                     ]
#                     formatted.append("• " + "\n  ".join(lines))
#                 return jsonify({"reply": "\n\n---\n\n".join(formatted)})


#         # --- 3️⃣ Normal AI parse + Supabase query ---
#         parsed = parse_user_query(user_input)
#         if parsed.get("operation") == "select" and "table" in parsed:
#             # Apply role-based filtering
#             if parsed["table"] == "projects":
#                 role_res = supabase.table("user_perms").select("role").eq("email", user_email).execute()
#                 role = role_res.data[0]["role"] if role_res.data else "Employee"
#                 if role.lower() == "employee":
#                     parsed["filters"]["assigned_to_emails"] = {"contains": user_email}
#                 elif role.lower() == "hr":
#                     parsed["filters"]["assigned_role"] = "employee"

#             reply = query_supabase(parsed)
#             return jsonify({"reply": reply})

#         # --- 4️⃣ Fallback to AI small-talk ---
#         user_name = session.get("user_name", "")
#         system_info = f"You are a helpful assistant. Known user email: {user_email or 'not set'}, name: {user_name or 'not set'}."
#         fallback_messages = [
#             {"role": "system", "content": system_info},
#             {"role": "user", "content": user_input}
#         ]
#         reply = call_openrouter(fallback_messages)
#         if not reply:
#             return jsonify({"reply": "⚠️ Language model service error. Please try again later."}), 500
#         return jsonify({"reply": reply})

#     except Exception as e:
#         print("❌ Chat Exception:", e)
#         traceback.print_exc()
#         return jsonify({"reply": "⚠️ Internal server error. Please try again later."}), 500

if __name__ == "__main__":
    if collection.count() == 0:
        load_documents()
    app.run(debug=True)
