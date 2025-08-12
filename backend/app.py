
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
# Session(app)
# CORS(app)

# chroma_client = chromadb.Client(Settings(allow_reset=True))
# try:
#     collection = chroma_client.create_collection("company_docs")
# except:
#     collection = chroma_client.get_collection("company_docs")

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
#     "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status", "assigned_role", "assigned_to", "client_name", "upload_documents", "project_scope", "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility", "role", "role_answers", "custom_questions", "custom_answers", "priority"],
#     "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
#     "user_memory": ["id", "user_id", "name", "known_facts"],
#     "user_perms": ["id", "name", "email", "password", "role", "permission_roles"]
# }

# def remove_emojis(text):
#     emoji_pattern = re.compile("[" +
#         u"\U0001F600-\U0001F64F" +
#         u"\U0001F300-\U0001F5FF" +
#         u"\U0001F680-\U0001F6FF" +
#         u"\U0001F1E0-\U0001F1FF" +
#         u"\U00002700-\U000027BF" +
#         u"\U000024C2-\U0001F251" + "]", flags=re.UNICODE)
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
#             doc_text = text.page_content
#             embedding = embeddings.embed_query(doc_text)  # 🔥 Generate embedding here
#             collection.add(
#                 documents=[doc_text],
#                 embeddings=[embedding],  # ✅ Must pass embedding
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
#         table = parsed.get("table")
#         filters = parsed.get("filters", {})
#         operation = parsed.get("operation", "select")
#         limit = parsed.get("limit", 5)

#         if isinstance(filters, list):
#             if len(filters) == 1 and isinstance(filters[0], dict):
#                 filters = filters[0]
#             else:
#                 return "❌ Invalid filters provided. Falling back to general knowledge."

#         query = supabase.table(table).select("*")
#         for field, value in filters.items():
#             query = query.ilike(field, f"%{value}%")

#         data = query.execute().data
#         if not data:
#             return "⚠️ No matching records found."

#         if operation == "count":
#             return f"📊 {len(data)} records found in '{table}'."

#         formatted = []
#         for row in data[:limit]:
#             lines = [f"{k.replace('_',' ').capitalize()}: {v}" for k, v in row.items() if v not in [None, '', [], {}]]
#             formatted.append("• " + "\n  ".join(lines))
#         return "\n\n---\n\n".join(formatted)
#     except Exception as e:
#         return f"❌ Supabase error: {str(e)}"

# def build_messages(user_input, context, memory):
#     name = memory.get("user_name", "")
#     if name:
#         user_input = f"{name} asked: {user_input}"

#     if context:
#         prompt = (
#             "You are a helpful assistant. You have access to internal documents. "
            
#             "Answer the user's question clearly and directly. Use the context below if it is relevant:\n\n"
#             f"{context}"
#         )
#     else:
#         prompt = "You are a helpful assistant. Answer clearly based on your general knowledge."

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
#         reply = ""

#         if parsed.get("operation") != "none":
#             reply = query_supabase(parsed)
#             if "❌" in reply or "⚠️" in reply or "No matching records" in reply:
#                 raise Exception("Fallback to LLM")
#         else:
#             raise Exception("Not a DB question")

#     except:
#         context = get_context(user_input)
#         messages = build_messages(user_input, context, memory)
#         res = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
#             json={"model": "mistralai/mistral-7b-instruct", "messages": messages, "temperature": 0.6, "max_tokens": 500}
#         )
#         reply = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else random.choice(CONFUSION_RESPONSES)

#     reply = remove_emojis(reply)
#     session["chat_history"].append({"role": "assistant", "content": reply})
#     session["chat_history"] = session["chat_history"][-5:]
#     return jsonify({"reply": reply})

# if __name__ == "__main__":
#     existing_ids = collection.get()["ids"]
#     if existing_ids:
#         collection.delete(ids=existing_ids)
#     load_documents()
#     app.run(debug=True)

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////  
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

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment or .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Flask setup
app = Flask(__name__)
app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# ChromaDB setup
chroma_client = chromadb.Client(Settings(allow_reset=True))
try:
    collection = chroma_client.create_collection("company_docs")
except:
    collection = chroma_client.get_collection("company_docs")

# Embedding model
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Config
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
    "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status", "assigned_role", "assigned_to", "client_name", "upload_documents", "project_scope", "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility", "role", "role_answers", "custom_questions", "custom_answers", "priority"],
    "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
    "user_memory": ["id", "user_id", "name", "known_facts"],
    "user_perms": ["id", "name", "email", "password", "role", "permission_roles"]
}

def remove_emojis(text):
    emoji_pattern = re.compile(
        "[" +
        u"\U0001F600-\U0001F64F" +
        u"\U0001F300-\U0001F5FF" +
        u"\U0001F680-\U0001F6FF" +
        u"\U0001F1E0-\U0001F1FF" +
        u"\U00002700-\U000027BF" +
        u"\U000024C2-\U0001F251" +
        "]+", flags=re.UNICODE)
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

def query_supabase(parsed):
    try:
        table = parsed["table"]
        filters = parsed.get("filters", {})
        operation = parsed.get("operation", "select")
        limit = parsed.get("limit", 5)

        query = supabase.table(table).select("*")
        for field, value in filters.items():
            query = query.ilike(field, f"%{value}%")

        data = query.execute().data
        if not data:
            return "I couldn't find any records matching that. Can you double-check the project or name?"

        if operation == "count":
            return f"There are {len(data)} matching records in the '{table}' table."

        # Format response clearly for the user
        responses = []
        for row in data[:limit]:
            response = []
            for key, val in row.items():
                if val not in [None, '', [], {}]:
                    key_label = key.replace('_', ' ').capitalize()
                    response.append(f"{key_label}: {val}")
            responses.append("• " + "\n  ".join(response))
        return "\n\n---\n\n".join(responses)

    except Exception as e:
        return f"⚠️ There was a problem accessing Supabase:\n{str(e)}"


def build_messages(user_input, context, memory):
    name = memory.get("user_name", "")
    if name:
        user_input = f"{name} asked: {user_input}"
   

    if context:
        prompt = (
            "You are a helpful assistant. Your job is to answer the user question first, clearly and directly.\n"
            "Context may contain facts from company documents. Do not ignore the question. Do not apologize unless wrong."
        )

        user_message = f"Context:\n{context}\n\n{user_input}"
    else:
        prompt = (
            "do not make fack information and  do not fack give data."
            "You are a helpful assistant. Always answer the user's question clearly. "
            "Use your general knowledge if no internal documents are available."
        )

        user_message = user_input

    session.setdefault("chat_history", [])
    session["chat_history"].append({"role": "user", "content": user_input})
    session["chat_history"] = session["chat_history"][-5:]
    messages = [{"role": "system", "content": prompt}]
    messages.extend(session["chat_history"])
    return messages

@app.route("/")
def index():
    return render_template("index.html")


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
        return jsonify({"reply": reply})

    except Exception as e:
        print("Chat error:", e)
        return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})


if __name__ == "__main__":
    if collection.count() == 0:
        load_documents()
    app.run(debug=True)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FINAL FIXED app.py WITH DOCUMENT ACCESS ENABLED
# FINAL FIXED app.py WITH DOCUMENT ACCESS AND CONTEXT-AWARE LLM FALLBACK

from itertools import tee
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import os, requests, re, json, random
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader, text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
from supabase import create_client, Client
from ast import literal_eval
from flask_cors import CORS
from ast import literal_eval


load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment or .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = 'fN1MVyBfRpUprorTH27518HcFQc8wpQc4YXZiOYytpY'
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
Session(app)
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
from datetime import datetime, timedelta

def get_logged_in_user():
    user_email = session.get("user_email")
    if not user_email:
        return None, None

    result = supabase.table("employee_login") \
        .select("logout_time") \
        .eq("email", user_email) \
        .order("login_time", desc=True) \
        .limit(1) \
        .execute()

    if result.data and result.data[0]["logout_time"] is None:
        # ✅ Verified active login
        role_res = supabase.table("user_perms") \
            .select("role") \
            .eq("email", user_email) \
            .limit(1) \
            .execute()
        role = role_res.data[0]["role"] if role_res.data else "Employee"
        return user_email, role

    return None, None


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
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        texts = splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db")
        vectorstore.persist()
        for i, text in enumerate(texts):
            collection.add(
                documents=[text.page_content],
                metadatas=[{"source": text.metadata.get("source", "company_docs")}],
                ids=[f"doc_{i}"]
            )

def get_context(query, k=5):
    try:
        results = collection.query(query_texts=[query], n_results=k)
        if results and 'documents' in results and results['documents']:
            # Combine all matched documents, not just [0]
            context_docs = []
            for doc_list in results['documents']:
                context_docs.extend(doc_list)
            # Remove duplicates and empty strings
            context_docs = list(set(filter(None, context_docs)))
            return "\n\n".join(context_docs)
    except Exception as e:
        print("Context retrieval error:", str(e))
    return ""



def parse_user_query(user_input):
    schema = "\n".join([f"{table}: {', '.join(cols)}" for table, cols in TABLES.items()])
    
    # Add the project-specific mappings
    field_mapping = {
        "tech stack": "tech_stack",
        "team": "assigned_to",
        "leader": "leader_of_project",
        "description": "project_description",
        "responsibility": "project_responsibility",
        "website": "project_name",
        "status": "status",
        "client": "client_name"
    }

    prompt = f"""
You are a helpful assistant for We3Vision Infotech. Use the following context to answer user questions clearly and politely.

Context:
{get_context(user_input)}

Question:
{user_input}

Answer in clear, format with bullets,numbering and table format if needed. 
move to next line after each key value pair.

You are a SQL reasoning assistant. The database has this schema:
{schema}

The user query is: "{user_input}"

Identify:
- operation (select/count/list)
- table (only use `projects`)
- fields to return (based on what user asks like leader, tech stack, etc.)
- filters (extract any names, values, or conditions user says like 'led by Bansi Patel')
- limit (optional)

Field Mapping:
{field_mapping}

For example:
User: show me projects led by Dhairya
Return:
{{
  "operation": "select",
  "table": "projects",
  "fields": ["project_name", "status", "leader_of_project"],
  "filters": {{"leader_of_project": "Dhairya"}},
  "limit": 5
}}

If not relevant to the database, return: {{"operation": "none"}}
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
    except Exception as e:
        print(f"Error in query parsing: {e}")
        return {"operation": "none"}


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

# Fuzzy match or partial match on project_name
def find_matching_project(user_input, projects_data):   
    for project in projects_data:
        if "website" in project["project_name"].lower():  # improve with fuzzy matching
            return project
    return None

def build_messages(user_input, context, memory):
    name = memory.get("user_name", "")
    if name:
        user_input = f"{name} asked: {user_input}"

    if context:
        prompt = (
            "You are a helpful assistant. You have access to internal documents. "
            "Answer in clear, format with bullets,numbering and table format if needed. "
            "move to next line after each key value pair. "
            "If the user asks about a project, use the context below to answer the question. "
            "If the user asks about a employee, use the context below to answer the question. "


            "Use the context below if it is relevant:\n\n"
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

@app.route("/set_session", methods=["POST"])
def set_session():
    email = request.json.get("email")
    session["user_email"] = email
    return jsonify({"message": "Session set"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_input = data.get("message", "").strip()
        if not user_input:
            return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})
        if "user_email" not in session:
            return jsonify({"message": "You are not logged in."}), 401
        # 🧠 Memory logic
        memory = load_memory()
        memory = update_user_memory(user_input, memory)
        save_memory(memory)

        # ✅ Get current user (email + role)
        user_email, user_role = get_logged_in_user()
        if not user_email:
             return jsonify({"reply": "hbhkh j kj jk k l❌ You are not currently logged in. Please login first to access project info."})

        # 🔐 Handle identity-specific questions
        if "my email" in user_input.lower() or "my mail" in user_input.lower():
            return jsonify({"reply": f"📧 Your email is: {user_email}"})
        if "my password" in user_input.lower() or "give me password" in user_input.lower():
            return jsonify({"reply": "❌ For security reasons, your password cannot be retrieved."})

        # 🧠 NLP → DB intent parsing
        parsed = parse_user_query(user_input)
        reply = ""

        if parsed.get("operation") != "none":
            # ✅ Add role-based filtering to project queries
            if parsed.get("table") == "projects":
                filters = parsed.get("filters", {})
                if user_role == "Employee":
                    filters["assigned_to"] = user_email
                elif user_role == "Hr":
                    filters["assigned_role"] = "Employee"
                parsed["filters"] = filters

            reply = query_supabase(parsed)

            if "❌" in reply or "⚠️" in reply or "No matching records" in reply:
                raise Exception("Fallback to LLM")
        else:
            raise Exception("Not a DB question")

    except Exception as e:
        print("Chat fallback error:", str(e))
        context = get_context(user_input)
        messages = build_messages(user_input, context, memory)
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={"model": "mistralai/mistral-7b-instruct", "messages": messages, "temperature": 0.6, "max_tokens": 500}
        )
        reply = res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else random.choice(CONFUSION_RESPONSES)

    reply = remove_emojis(reply)
    session.setdefault("chat_history", [])
    session["chat_history"].append({"role": "assistant", "content": reply})
    session["chat_history"] = session["chat_history"][-5:]
    
    return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

@app.route("/set_session", methods=["POST"])
def set_session():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "No email provided"}), 400
    session["user_email"] = email
    return jsonify({"message": f"Session set for {email}"}), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})


if __name__ == "__main__":
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
    load_documents()
    app.run(debug=True)

# ====================================================================================================================================================
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
# app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'

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
#         if table == "projects":
#             if user_role.lower() == "employee":
#                 parsed["filters"]["assigned_to_emails"] == {"contains": user_email}
#             else:
#                 reply="no data found"
#                 return jsonify({"reply": reply})

#         # if table == "projects":
#         #     if user_role.lower() == "employee":
#         #         parsed["filters"]["assigned_to_emails"] = {"contains": user_email}
#         #     elif user_role.lower() == "hr":
#         #         parsed["filters"]["assigned_role"] = "employee"
#         #     elif user_role.lower() == "admin":
#         #         pass
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



# "login kara pela chatbot ni khulatu"
# but logout kari ne pachhu khule chhe to e fix karvanu chhe record found sarkhu work kare chhe  logic vala ma j last kam karyu hatu 