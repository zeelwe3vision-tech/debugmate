  
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

# # Load environment variables
# load_dotenv()
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment or .env file.")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # Flask setup
# app = Flask(__name__)
# app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)

# # ChromaDB setup
# chroma_client = chromadb.Client(Settings(allow_reset=True))
# try:
#     collection = chroma_client.create_collection("company_docs")
# except:
#     collection = chroma_client.get_collection("company_docs")

# # Embedding model
# embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# # Config
# MEMORY_FILE = "memory.json"
# CONFUSION_RESPONSES = [
#     "Hmm, I'm not quite sure what you mean. Could you rephrase it?",
#     "Can you please provide more details?",
#     "Let's try that again — can you explain it another way?",
#     "I'm here to help, but I need a bit more information from you.",
#     "Please clarify your question a little so I can assist better!"
# ]

# # Known Supabase tables (schema)
# TABLES = {
#     "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status", "assigned_role", "assigned_to", "client_name", "upload_documents", "project_scope", "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility", "role", "role_answers", "custom_questions", "custom_answers", "priority"],
#     "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
#     "user_memory": ["id", "user_id", "name", "known_facts"],
#     "user_perms": ["id", "name", "email", "password", "role", "permission_roles"]
# }

# def remove_emojis(text):
#     emoji_pattern = re.compile(
#         "[" +
#         u"\U0001F600-\U0001F64F" +
#         u"\U0001F300-\U0001F5FF" +
#         u"\U0001F680-\U0001F6FF" +
#         u"\U0001F1E0-\U0001F1FF" +
#         u"\U00002700-\U000027BF" +
#         u"\U000024C2-\U0001F251" +
#         "]+", flags=re.UNICODE)
#     return emoji_pattern.sub(r'', text)

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
#     schema = "\n".join([f"{table}: {', '.join(cols)}" for table, cols in TABLES.items()])
#     prompt = f"""
# You are connected to a Supabase database with these tables:
# {schema}

# User asked: "{user_input}"

# Your job is to extract:
# - operation (select, count, list, etc.)
# - table name
# - fields to show
# - filters (e.g. project_name = "xyz")
# - limit (optional)
# if user ask project data :
#  Return details in JSON like example->
 
# {{
#   "operation": "select",
#   "table": "projects",
#   "fields": ["project_name", "status"],
#   "filters": {{"project_name": "xyzvision"}},
#   "limit": 2
# }}
# If not relevant, return: {{"operation": "none"}}
# """
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

# def query_supabase(parsed):
#     try:
#         table = parsed["table"]
#         filters = parsed.get("filters", {})
#         operation = parsed.get("operation", "select")
#         limit = parsed.get("limit", 5)

#         query = supabase.table(table).select("*")
#         for field, value in filters.items():
#             query = query.ilike(field, f"%{value}%")

#         data = query.execute().data
#         if not data:
#             return "I couldn't find any records matching that. Can you double-check the project or name?"

#         if operation == "count":
#             return f"There are {len(data)} matching records in the '{table}' table."

#         # Format response clearly for the user
#         responses = []
#         for row in data[:limit]:
#             response = []
#             for key, val in row.items():
#                 if val not in [None, '', [], {}]:
#                     key_label = key.replace('_', ' ').capitalize()
#                     response.append(f"{key_label}: {val}")
#             responses.append("• " + "\n  ".join(response))
#         return "\n\n---\n\n".join(responses)

#     except Exception as e:
#         return f"⚠️ There was a problem accessing Supabase:\n{str(e)}"


# def build_messages(user_input, context, memory):
#     name = memory.get("user_name", "")
#     if name:
#         user_input = f"{name} asked: {user_input}"
   

#     if context:
#         prompt = (
#             "You are a helpful assistant. Your job is to answer the user question first, clearly and directly.\n"
#             "Context may contain facts from company documents. Do not ignore the question. Do not apologize unless wrong."
#         )

#         user_message = f"Context:\n{context}\n\n{user_input}"
#     else:
#         prompt = (
#             "do not make fack information and  do not fack give data."
#             "You are a helpful assistant. Always answer the user's question clearly. "
#             "Use your general knowledge if no internal documents are available."
#         )

#         user_message = user_input

#     session.setdefault("chat_history", [])
#     session["chat_history"].append({"role": "user", "content": user_input})
#     session["chat_history"] = session["chat_history"][-5:]
#     messages = [{"role": "system", "content": prompt}]
#     messages.extend(session["chat_history"])
#     return messages

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/clear_session", methods=["POST"])
# def clear_session():
#     session.clear()
#     return '', 204

# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json(force=True)
        
#         user_input = data.get("message", "").strip()
#         if not user_input:
#             return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

#         memory = load_memory()
#         memory = update_user_memory(user_input, memory)
#         save_memory(memory)

#         parsed = parse_user_query(user_input)
#         if parsed.get("operation") != "none":
#             reply = query_supabase(parsed)
#         else:
#             context = get_context(user_input)
#             messages = build_messages(user_input, context, memory)
#             res = requests.post(
#                 "https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "mistralai/mistral-7b-instruct",
#                     "messages": messages,
#                     "temperature": 0.5,
#                     "max_tokens": 500
#                 }
#             )
#             reply = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else random.choice(CONFUSION_RESPONSES)

#         reply = remove_emojis(reply)
#         session["chat_history"].append({"role": "assistant", "content": reply})
#         session["chat_history"] = session["chat_history"][-5:]
#         return jsonify({"reply": reply})

#     except Exception as e:
#         print("Chat error:", e)
#         return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})


# if __name__ == "__main__":
#     if collection.count() == 0:
#         load_documents()
#     app.run(debug=True)


# FINAL FIXED app.py WITH DOCUMENT ACCESS ENABLED
# FINAL FIXED app.py WITH DOCUMENT ACCESS AND CONTEXT-AWARE LLM FALLBACK

from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import os, requests, re, json, random
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from chromadb.config import Settings
from supabase import create_client, Client
from ast import literal_eval
from flask_cors import CORS

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment or .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
CORS(app, supports_credentials=True)

chroma_client = chromadb.Client(Settings(allow_reset=True))
try:
    collection = chroma_client.create_collection("company_docs")
except:
    collection = chroma_client.get_collection("company_docs")

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

MEMORY_FILE = "memory.json"
CONFUSION_RESPONSES = [
    "Hmm, I'm not quite sure what you mean. Could you rephrase it?",
    "Can you please provide more details?",
    "Let's try that again — can you explain it another way?",
    "I'm here to help, but I need a bit more information from you.",
    "Please clarify your question a little so I can assist better!"
]

TABLES = {
    "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status", "assigned_role", "assigned_to", "client_name", "upload_documents", "project_scope", "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility", "role", "role_answers", "custom_questions", "custom_answers", "priority"],
    "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
    "user_memory": ["id", "user_id", "name", "known_facts"],
    "user_perms": ["id", "name", "email", "password", "role", "permission_roles"]
}

def remove_emojis(text):
    emoji_pattern = re.compile("[" +
        u"\U0001F600-\U0001F64F" +
        u"\U0001F300-\U0001F5FF" +
        u"\U0001F680-\U0001F6FF" +
        u"\U0001F1E0-\U0001F1FF" +
        u"\U00002700-\U000027BF" +
        u"\U000024C2-\U0001F251" + "]", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_user_memory(user_input, memory):
    match = re.search(r"\b(?:my name is|i am|i'm|this is|this side)\s+(\w+)", user_input, re.IGNORECASE)
    if match:
        memory["user_name"] = match.group(1).capitalize()
    return memory

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
    try:
        results = collection.query(query_texts=[query], n_results=k)
        if results and results['documents']:
            return "\n".join(results['documents'][0])
    except:
        return ""
    return ""

def parse_user_query(user_input):
    schema = "\n".join([f"{table}: {', '.join(cols)}" for table, cols in TABLES.items()])
    prompt = f"""
You are connected to a Supabase database with these tables:
{schema}

User asked: "{user_input}"

Your job is to extract:
- operation (select, count, list, etc.)
- table name
- fields to show
- filters (e.g. project_name = "xyz")
- limit (optional)
if user ask project data :
 Return details in JSON like example->
 
{{
  "operation": "select",
  "table": "projects",
  "fields": ["project_name", "status"],
  "filters": {{"project_name": "xyzvision"}},
  "limit": 2
}}
If not relevant, return: {{"operation": "none"}}
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
                "temperature": 0.1,
                "max_tokens": 300
            }
        )
        content = res.json()["choices"][0]["message"]["content"]
        return literal_eval(content)
    except:
        return {"operation": "none"}

def llm_response(user_input):
    memory = load_memory()
    memory = update_user_memory(user_input, memory)
    save_memory(memory)

    parsed = parse_user_query(user_input)
    if parsed.get("operation") != "none":
        reply = query_supabase(parsed)
    else:
        context = get_context(user_input)
        messages = build_messages(user_input, context, memory)
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 500
            }
        )
        reply = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else random.choice(CONFUSION_RESPONSES)

    reply = remove_emojis(reply)
    session["chat_history"].append({"role": "assistant", "content": reply})
    session["chat_history"] = session["chat_history"][-5:]
    return {"reply": reply}


def query_supabase(parsed):
    try:
        table = parsed.get("table")
        filters = parsed.get("filters", {})
        operation = parsed.get("operation", "select")
        limit = parsed.get("limit", 5)

        if isinstance(filters, list):
            if len(filters) == 1 and isinstance(filters[0], dict):
                filters = filters[0]
            else:
                return "❌ Invalid filters provided. Falling back to general knowledge."

        query = supabase.table(table).select("*")
        for field, value in filters.items():
            query = query.ilike(field, f"%{value}%")

        data = query.execute().data
        if not data:
            return "⚠️ No matching records found."

        if operation == "count":
            return f"📊 {len(data)} records found in '{table}'."

        formatted = []
        for row in data[:limit]:
            lines = [f"{k.replace('_',' ').capitalize()}: {v}" for k, v in row.items() if v not in [None, '', [], {}]]
            formatted.append("• " + "\n  ".join(lines))
        return "\n\n---\n\n".join(formatted)
    except Exception as e:
        return f"❌ Supabase error: {str(e)}"

def build_messages(user_input, context, memory):
    name = memory.get("user_name", "")
    if name:
        user_input = f"{name} asked: {user_input}"

    if context:
        prompt = (
            "You are a helpful assistant. You have access to internal documents. "
            
            "Answer the user's question clearly and directly. Use the context below if it is relevant:\n\n"
            f"{context}"
        )
    else:
        prompt = "You are a helpful assistant. Answer clearly based on your general knowledge."

    session.setdefault("chat_history", [])
    session["chat_history"].append({"role": "user", "content": user_input})
    session["chat_history"] = session["chat_history"][-5:]
    messages = [{"role": "system", "content": prompt}]
    messages.extend(session["chat_history"])
    return messages

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clear_session", methods=["POST"])
def clear_session():
    session.clear()
    return '', 204

@app.route("/refresh_docs", methods=["POST"])
def refresh_docs():
    try:
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)
        load_documents()
        return jsonify({"message": "Documents refreshed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_input = data.get("message", "").strip()
        if not user_input:
            return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

        memory = load_memory()
        memory = update_user_memory(user_input, memory)
        save_memory(memory)

        parsed = parse_user_query(user_input)
        reply = ""

        if parsed.get("operation") != "none":
            reply = query_supabase(parsed)
            if "❌" in reply or "⚠️" in reply or "No matching records" in reply:
                raise Exception("Fallback to LLM")
        else:
            raise Exception("Not a DB question")

    except:
        context = get_context(user_input)
        messages = build_messages(user_input, context, memory)
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={"model": "mistralai/mistral-7b-instruct", "messages": messages, "temperature": 0.6, "max_tokens": 500}
        )
        reply = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else random.choice(CONFUSION_RESPONSES)

    reply = remove_emojis(reply)
    session["chat_history"].append({"role": "assistant", "content": reply})
    session["chat_history"] = session["chat_history"][-5:]
    return jsonify({"reply": reply})


if __name__ == "__main__":
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
    load_documents()
    app.run(debug=True)
