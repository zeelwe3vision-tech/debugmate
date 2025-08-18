
# # code 13/8

# from dataclasses import field
# from flask import Flask, request, jsonify, render_template, session
# from flask_session import Session
# import os, requests, re, json, random, traceback
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

# # ---------------- Load Environment Variables ----------------
# load_dotenv()
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# print(f"Loaded OPENROUTER_API_KEY: '{OPENROUTER_API_KEY}'")

# if not OPENROUTER_API_KEY:
#     raise ValueError("OPENROUTER_API_KEY not set — please check your .env")
# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# # ---------------- Initialize Clients ----------------
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'")
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config["SESSION_PERMANENT"] = False
# CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:5173"])
# Session(app)

# # Persistent ChromaDB
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
# # Known Supabase tables (schema)
# TABLES = {
#  "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status", 
#                 "assigned_to_emails", "client_name", "upload_documents", "project_scope", 
#                 "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility", 
#                 "role", "role_answers", "custom_questions", "custom_answers", "priority"],
#     "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
#     "user_memory": ["id", "user_id", "name", "known_facts"],
#     "user_perms": ["id", "name", "email", "password", "role", "permission_roles"],

# "fields ":{
#                 "project_name", "status", "tech_stack", "project_description",
#                 "start_date", "end_date", "assigned_to_emails", "client_name",
#                 "project_scope", "tech_stack_custom", "leader_of_project",
#                 "project_responsibility", "role_answers", "custom_questions",
#                 "custom_answers", "priority"}
   
# }



# # # ---------------- Memory Management ----------------
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

# # ---------------- Document Processing ----------------
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
#     if len(query.split()) <= 2:
#         return ""
#     try:
#         results = collection.query(query_texts=[query], n_results=k)
#         if results and results.get('documents'):
#             return "\n".join(results['documents'][0])
#     except:
#         return ""
#     return ""

#    # ---------------- build  ---------------- 
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
# # ---------------- AI Query Parsing ----------------
# def call_openrouter(messages, temperature=0.5, max_tokens=500):
#     """Centralized call to OpenRouter with error handling."""
#     try:
#         res = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {'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'}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "mistralai/mistral-7b-instruct",
#                 "messages": messages,
#                 "temperature": temperature,
#                 "max_tokens": max_tokens
#             },
#             timeout=15
#         )
#         if res.status_code != 200:
#             print(f"⚠️ OpenRouter API error {res.status_code}: {res.text}")
#             return None
#         data = res.json()
#         if "choices" not in data:
#             print("⚠️ Missing 'choices' in API response:", data)
#             return None
#         return data["choices"][0]["message"]["content"]
#     except Exception as e:
#         print("❌ Exception calling OpenRouter:", e)
#         traceback.print_exc()
#         return None

# def parse_user_query(user_input):
#     schema = "\n".join([f"{table}: {', '.join(cols)}" for table, cols in TABLES.items()])

#     # Force-match if user explicitly mentions 'project'
#     if "project" in user_input.lower():
#         return {
#             "operation": "select",
#             "table": "projects",
#             "fields": [
#                 "project_name", "status", "tech_stack", "project_description",
#                 "start_date", "end_date", "assigned_to_emails", "client_name",
#                 "project_scope", "tech_stack_custom", "leader_of_project",
#                 "project_responsibility", "role_answers", "custom_questions",
#                 "custom_answers", "priority"
#             ],
#             "filters": {"project_name": user_input.replace("details of", "").replace("project", "").strip()},
#             "limit": 10
#         }

#     # Else, fall back to LLM parsing
#     prompt = f"""You are connected to a Supabase database with these tables:
#     {schema}

#     User asked: "{user_input}"

#     Extract operation, table, fields, filters, limit.
#     If not matching, return {{ "operation": "none" }}.
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
#                 "temperature": 0.2,
#                 "max_tokens": 300
#             }
#         )
#         content = res.json()["choices"][0]["message"]["content"]
#         return literal_eval(content)
#     except:
#         return {"operation": "none"}


# # ---------------- llm response ----------------
# def llm_response(user_input):
#     memory = load_memory()
#     memory = update_user_memory(user_input, memory)
#     save_memory(memory)

#     parsed = parse_user_query(user_input)
#     if parsed.get("operation") == "none":
#         return {"reply": "🤖 I couldn't understand that request. Can you rephrase it?"}

#     reply = query_supabase(parsed)
#     session({"role": "assistant", "content": reply})
#     return {"reply": reply}

# # ---------------- Supabase Query ----------------

# # def query_supabase(parsed):
# #     try:
# #         table = parsed.get("table")
# #         filters = parsed.get("filters", {}) or {}
# #         operation = parsed.get("operation", "select")
# #         limit = parsed.get("limit", 10)
# #         fields = parsed.get("fields", ["*"])
# #         user_email = session.get("user_email", "")
# #         user_role = "Employee"

# #         # Get role from Supabase
# #         role_res = supabase.table("user_perms").select("role").eq("email", user_email).execute()
# #         if role_res.data:
# #             user_role = role_res.data[0].get("role", "Employee")

# #         print(f"🔍 Querying table: {table}, filters: {filters}, role: {user_role}, email: {user_email}")

# #         # -------------------------
# #         # Build initial query
# #         # -------------------------
# #         query = supabase.table(table).select("*")
# #         for field, value in filters.items():
# #             if not value:
# #                 continue
# #             if isinstance(value, dict) and "contains" in value:
# #                 query = query.contains(field, [value["contains"]])
# #             else:
# #                 query = query.ilike(field, f"%{value}%")

# #         # Role restrictions for projects
# #         if table == "projects" and user_role.lower() == "employee":
# #             query = query.contains("assigned_to_emails", [user_email])

# #         data = query.limit(limit).execute().data or []

# #         # -------------------------
# #         # Fuzzy Search Fallback
# #         # -------------------------
# #                # -------------------------
# #         # Fuzzy Search Fallback (for all project fields)
# #         # -------------------------
# #         if not data and table == "projects" and filters:
# #             print("🔍 No results — trying fuzzy search on all fields...")
            
# #             fuzzy_query = supabase.table(table).select("*")

# #             for field, original_value in filters.items():
# #                 if not original_value:
# #                     continue
                
# #                 # Extract keywords and remove filler words
# #                 filler_words = {"give", "only", "details", "about", "project", "projects", "info"}
# #                 keywords = [w for w in re.findall(r'\w+', str(original_value)) if w.lower() not in filler_words]

# #                 if keywords:
# #                     main_keyword = keywords[0]
# #                     print(f"🔍 Fuzzy search retry on field '{field}' with keyword: {main_keyword}")
# #                     fuzzy_query = fuzzy_query.ilike(field, f"%{main_keyword}%")

# #             # Apply role restriction for employees
# #             if user_role.lower() == "employee":
# #                 fuzzy_query = fuzzy_query.contains("assigned_to_emails", [user_email])

# #             data = fuzzy_query.limit(limit).execute().data or []

# #         # -------------------------
# #         # Return results
# #         # -------------------------
# #         if not data:
# #             return "⚠️ No matching records found."

# #         formatted = []
# #         for row in data:
# #             is_assigned = user_email in (row.get("assigned_to_emails") or [])
# #             if table == "projects" and not (is_assigned or user_role.lower() in ["admin", "hr", "manager"]):
# #                 details = [
# #                     f"Project Name: {row.get('project_name', 'N/A')}",
# #                     f"Status: {row.get('status', 'N/A')}",
# #                     "⚠️ You do not have permission to view full details."
# #                 ]
# #             else:
# #                 details = [
# #                     f"{k.replace('_', ' ').title()}: {v}"
# #                     for k, v in row.items()
# #                     if v not in [None, "", [], {}]
# #                 ]
# #             formatted.append("• " + "\n  ".join(details))

# #         return "\n\n---\n\n".join(formatted)

# #     except Exception as e:
# #         print("❌ Supabase error:", e)
# #         traceback.print_exc()
# #         return f"❌ Supabase error: {str(e)}"
# # ---------------- Supabase Query ----------------
# # def query_supabase(parsed):
# #     try:
# #         table = parsed.get("table")
# #         filters = parsed.get("filters", {}) or {}
# #         operation = parsed.get("operation", "select")
# #         limit = parsed.get("limit", 10)
# #         fields = parsed.get("fields", ["*"])
# #         user_email = session.get("user_email", "")
# #         user_role = "Employee"

# #         # Get role from Supabase
# #         role_res = supabase.table("user_perms").select("role").eq("email", user_email).execute()
# #         if role_res.data:
# #             user_role = role_res.data[0].get("role", "Employee")

# #         print(f"🔍 Querying table: {table}, filters: {filters}, role: {user_role}, email: {user_email}")

# #         # Build query
# #         query = supabase.table(table).select("*")
# #         for field, value in filters.items():
# #             query = query.ilike(field, f"%{value}%")


# #         for field, value in filters.items():
# #             if not value:
# #                 continue
# #             if isinstance(value, dict) and "contains" in value:
# #                 # For array fields like assigned_to_emails
# #                 query = query.contains(field, [value["contains"]])
# #             else:
# #                 # Case-insensitive partial match
# #                 query = query.ilike(field, f"%{value}%")

# #         # Role restrictions for projects
# #         if table == "projects" and user_role.lower() == "employee":
# #             query = query.contains("assigned_to_emails", [user_email])

# #         data = query.limit(limit).execute().data or []
# #         if not data:
# #             return "⚠️ No matching records found."

# #         formatted = []
# #         for row in data:
# #             is_assigned = user_email in (row.get("assigned_to_emails") or [])
# #             if table == "projects" and not (is_assigned or user_role.lower() in ["admin", "hr", "manager"]):
# #                 details = [
# #                     f"Project Name: {row.get('project_name', 'N/A')}",
# #                     f"Status: {row.get('status', 'N/A')}",
# #                     "⚠️ You do not have permission to view full details."
# #                 ]
# #             else:
# #                 details = [
# #                     f"{k.replace('_', ' ').title()}: {v}"
# #                     for k, v in row.items()
# #                     if v not in [None, "", [], {}]
# #                 ]
# #             formatted.append("• " + "\n  ".join(details))

# #         return "\n\n---\n\n".join(formatted)

# #     except Exception as e:
# #         print("❌ Supabase error:", e)
# #         traceback.print_exc()
# #         return f"❌ Supabase error: {str(e)}"

# # ====================== ENHANCED SEARCH FILTERING ======================

# def query_supabase(parsed):
#     try:
#         table = parsed.get("table")
#         filters = parsed.get("filters", {}) or {}
#         operation = parsed.get("operation", "select")
#         limit = parsed.get("limit", 10)
#         fields = parsed.get("fields", ["*"])
#         user_email = session.get("user_email", "")
#         user_role = "Employee"

#         # Get role from Supabase (keep your existing role logic)
#         role_res = supabase.table("user_perms").select("role").eq("email", user_email).execute()
#         if role_res.data:
#             user_role = role_res.data[0].get("role", "Employee")

#         print(f"🔍 Querying table: {table}, filters: {filters}, role: {user_role}, email: {user_email}")

#         # Build query - ENHANCED FILTER HANDLING STARTS HERE
#         query = supabase.table(table).select(",".join(fields))
        
#         for field, value in filters.items():
#             if not value:
#                 continue
                
#             # Enhanced status filter (exact match)
#             if field == "status":
#                 query = query.eq(field, value.capitalize())
            
#             # Enhanced tech_stack filter (array contains)
#             elif field == "tech_stack":
#                 if isinstance(value, list):
#                     for tech in value:
#                         query = query.contains(field, [tech.strip()])
#                 else:
#                     query = query.contains(field, [value.strip()])
            
#             # Enhanced date filtering
#             elif field.endswith("_date"):
#                 if isinstance(value, dict):  # Date range
#                     if "start" in value:
#                         query = query.gte(field, value["start"])
#                     if "end" in value:
#                         query = query.lte(field, value["end"])
#                 else:  # Exact date
#                     query = query.eq(field, value)
            
#             # Default text search (improved with exact match for short queries)
#             else:
#                 if len(str(value)) <= 4:
#                     query = query.ilike(field, f"{value}%")  # Prefix match
#                 else:
#                     query = query.ilike(field, f"%{value}%")  # Fuzzy match

#         # Keep your existing role restrictions
#         if table == "projects" and user_role.lower() == "employee":
#             query = query.contains("assigned_to_emails", [user_email])

#         data = query.limit(limit).execute().data or []

#         # ENHANCED FUZZY SEARCH FALLBACK
#         if not data and table == "projects" and filters:
#             print("🔍 No results — trying enhanced fuzzy search...")
#             fuzzy_query = supabase.table(table).select(",".join(fields))
            
#             for field, value in filters.items():
#                 if not value:
#                     continue
                
#                 # Split into keywords and search each field
#                 keywords = re.findall(r'\w+', str(value))
#                 for keyword in keywords:
#                     if len(keyword) > 2:  # Ignore short words
#                         fuzzy_query = fuzzy_query.or_(f"{field}.ilike.%{keyword}%")
            
#             if user_role.lower() == "employee":
#                 fuzzy_query = fuzzy_query.contains("assigned_to_emails", [user_email])
            
#             data = fuzzy_query.limit(limit).execute().data or []

#         # Keep your existing response formatting
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


# # ---------------- Routes ----------------
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

# @app.route("/debug_session")
# def debug_session():
#     return jsonify(dict(session))

# # this is latest documents based chat rote
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

#         # 1️⃣ Special case: List all projects
#         if re.search(r"\b(list|show)\b.*\bprojects\b", user_input, re.IGNORECASE):
#             parsed = {
#                 "operation": "select",
#                 "table": "projects",
#                 "fields": ["*"],
#                 "filters": {},
#                 "limit": 20
#             }
#             return jsonify({"reply": query_supabase(parsed)})

#         # 2️⃣ Parse query dynamically
#         parsed = parse_user_query(user_input)
#         print(f"🛠 Parsed query: {parsed}")

#         # 3️⃣ If AI says no DB operation → fallback with document context
#         if not parsed or parsed.get("operation") != "select" or "table" not in parsed:
#             doc_context = get_context(user_input)
#             user_name = session.get("user_name", "")
#             system_info = f"You are a helpful assistant. Known user email: {user_email}, name: {user_name or 'not set'}."

           

#             # Include doc context if found
#             if doc_context:
#                 system_info += f"\n\nRelevant internal company documents:\n{doc_context}"

#             fallback_messages = [
#                 {"role": "system", "content": system_info},
#                 {"role": "user", "content": user_input}
#             ]
#             reply = call_openrouter(fallback_messages)
#             return jsonify({"reply": reply or "⚠️ Unable to process your request right now."})

#         # 4️⃣ Auto-add project name filter if mentioned
#         if parsed.get("table") == "projects" and parsed.get("filters", {field}).get(""):
#             original_val = parsed["filters"]["project_name"].strip()
#             match = re.search(r"\b([a-zA-Z0-9\s]+?)\s*(?:project|details|info)?$", original_val, re.IGNORECASE)
#             if match:
#                 clean_name = match.group(1).strip()
#                 if clean_name and clean_name.lower() not in ["give only", "only", "all"]:
#                     parsed["filters"]["project_name"] = clean_name
#                 else:
#                     parsed["filters"].pop("project_name")

#         # 5️⃣ Query Supabase
#         reply = query_supabase(parsed)

#         # 6️⃣ If Supabase says "No matching records found", try documents as fallback
#         if reply.strip().startswith("⚠️ No matching records"):
#             doc_context = get_context(user_input)
#             if doc_context:
#                 user_name = session.get("user_name", "")
#                 system_info = f"You are a helpful assistant. Known user email: {user_email}, name: {user_name or 'not set'}.\n\nRelevant internal company documents:\n{doc_context}"
#                 fallback_messages = [
#                     {"role": "system", "content": system_info},
#                     {"role": "user", "content": user_input}
#                 ]
#                 reply = call_openrouter(fallback_messages) or reply

#         return jsonify({"reply": reply})

#     except Exception as e:
#         print("❌ Chat Exception:", e)
#         traceback.print_exc()
#         return jsonify({"reply": "⚠️ Internal server error. Please try again later."}), 500

# if __name__ == "__main__":
#     if collection.count() == 0:
#         load_documents()
#     app.run(debug=True)


# work all tables and full fuzzy search but not have identity based access
# from dataclasses import field
# from flask import Flask, request, jsonify, render_template, session
# from flask_session import Session
# import os, requests, re, json, random, traceback
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

# # ---------------- Load Environment Variables ----------------
# load_dotenv()
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# print(f"Loaded OPENROUTER_API_KEY: '{OPENROUTER_API_KEY}'")

# if not OPENROUTER_API_KEY:
#     raise ValueError("OPENROUTER_API_KEY not set — please check your .env")
# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# # ---------------- Initialize Clients ----------------
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'")
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config["SESSION_PERMANENT"] = False
# CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:5173"])
# Session(app)

# # Persistent ChromaDB
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
# # Known Supabase tables (schema)
# TABLES = {
#  "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status",
#                 "assigned_to_emails", "client_name", "upload_documents", "project_scope",
#                 "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility",
#                 "role", "role_answers", "custom_questions", "custom_answers", "priority"],
#     "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
#     "user_memory": ["id", "user_id", "name", "known_facts"],
#     "user_perms": ["id", "name", "email", "password", "role", "permission_roles"],

# "fields ":{
#                 "project_name", "status", "tech_stack", "project_description",
#                 "start_date", "end_date", "assigned_to_emails", "client_name",
#                 "project_scope", "tech_stack_custom", "leader_of_project",
#                 "project_responsibility", "role_answers", "custom_questions",
#                 "custom_answers", "priority"}
   
# }



# # # ---------------- Memory Management ----------------
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

# # ---------------- Document Processing ----------------
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
#     if len(query.split()) <= 2:
#         return ""
#     try:
#         results = collection.query(query_texts=[query], n_results=k)
#         if results and results.get('documents'):
#             return "\n".join(results['documents'][0])
#     except:
#         return ""
#     return ""


# def get_user_role(email):
#     """Fetch user role from Supabase"""
#     try:
#         res = supabase.table("user_perms").select("role").eq("email", email).execute()
#         return res.data[0].get("role", "Employee") if res.data else "Employee"
#     except:
#         return "Employee"

# def needs_database_query(llm_response):
#     """Determine if we need to query the database"""
#     triggers = [
#         "check the database",
#         "look up in the system",
#         "query the records",
#         "i don't have that information",
#         "data shows",
#         "fetch from database",
#         "from db",
#         "from database",
#     ]
#     return any(trigger in llm_response.lower() for trigger in triggers)

# def explain_database_results(user_input, db_results, user_context):
#     """Convert raw DB results to natural language"""
#     prompt = f"""Convert these database results into a friendly response:
    
#     User asked: "{user_input}"
#     User context: {user_context}
#     Database results:
#     {db_results}
    
#     Respond in 1-4 paragraphs using natural language, focusing on the key information.
#     respond in summary not in too long responce
#     if user ask for all project details give all project details alocated to that user"""
    
#     return call_openrouter([
#         {"role": "system", "content": "You are a helpful assistant that explains data."},
#         {"role": "user", "content": prompt}
#     ])

#    # ---------------- build mass ---------------- 
# def build_messages(user_input, context, memory):
#     name = memory.get("user_name", "")
#     if name:
#         user_input = f"{name} asked: {user_input}"
   

#     if context:
#         prompt = (
        
#             "You are a helpful assistant. Your job is to answer the user question first, clearly and directly.\n"
#             "Context may contain facts from company documents. Do not ignore the question. Do not apologize unless wrong."
#                 """
#     Format Supabase query results into a clean, human-readable response.
#     Dynamically adjusts structure based on query type and dataset.

#     Parameters:
#         data (list[dict]): List of records from Supabase query.
#         query_type (str): Type of query (projects, employees, memory, general).

#     Returns:
#         str: Formatted response for the chatbot.
#     """
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
# # ---------------- AI Query Parsing ----------------
# def call_openrouter(messages, temperature=0.5, max_tokens=500):
#     """Centralized call to OpenRouter with error handling."""
#     try:
#         res = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {'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'}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "mistralai/mistral-7b-instruct",
#                 "messages": messages,
#                 "temperature": temperature,
#                 "max_tokens": max_tokens
#             },
#             timeout=15
#         )
#         if res.status_code != 200:
#             print(f"⚠️ OpenRouter API error {res.status_code}: {res.text}")
#             return None
#         data = res.json()
#         if "choices" not in data:
#             print("⚠️ Missing 'choices' in API response:", data)
#             return None
#         return data["choices"][0]["message"]["content"]
#     except Exception as e:
#         print("❌ Exception calling OpenRouter:", e)
#         traceback.print_exc()
#         return None

# # ----------------- NEW: safe helpers for Supabase filtering -----------------
# def _is_int_like(val):
#     """Return True if value represents an integer (so we should use eq instead of ilike)."""
#     try:
#         if isinstance(val, int):
#             return True
#         s = str(val).strip()
#         # treat pure numeric strings as integers
#         return re.fullmatch(r"-?\d+", s) is not None
#     except:
#         return False

# def _apply_filter(query, field, value):
#     """
#     Apply type-aware filter to a supabase query builder:
#       - arrays (list or dict{'contains':...}) -> .contains
#       - ints -> .eq
#       - small tokens (<=4 chars) -> prefix ilike
#       - longer strings -> fuzzy ilike
#       - dict with start/end -> date range handling via gte/lte
#     """
#     # arrays / contains
#     if isinstance(value, dict) and "contains" in value:
#         contains_val = value["contains"]
#         if isinstance(contains_val, list):
#             for v in contains_val:
#                 query = query.contains(field, [v])
#         else:
#             query = query.contains(field, [contains_val])
#         return query

#     # date range
#     if isinstance(value, dict) and ("start" in value or "end" in value):
#         if "start" in value and value["start"]:
#             query = query.gte(field, value["start"])
#         if "end" in value and value["end"]:
#             query = query.lte(field, value["end"])
#         return query

#     # numeric exact match
#     if _is_int_like(value):
#         # use eq for integers to avoid ilike on numeric columns
#         try:
#             return query.eq(field, int(str(value).strip()))
#         except:
#             # fallback to text match if int cast fails (e.g., big int or uuid-like)
#             pass

#     # string fuzzy/prefix
#     if isinstance(value, str):
#         v = value.strip()
#         if len(v) <= 4:
#             return query.ilike(field, f"{v}%")
#         else:
#             return query.ilike(field, f"%{v}%")

#     # fallback equality
#     return query.eq(field, value)

# # ---------------- Enhanced parse_user_query (LLM-driven, no hardcoding) ----------------
# def parse_user_query(user_input):
#     """
#     Use the LLM to pick the best table and map user constraints to actual columns.
#     Returns a dict: {"operation":"select","table":..., "fields":[...], "filters":{...}, "limit":int}
#     If the LLM can't map, returns {"operation":"none"}.
#     """
#     # Build schema description from TABLES
#     schema_lines = []
#     for t, cols in TABLES.items():
#         if isinstance(cols, list):
#             schema_lines.append(f"{t}: {', '.join(cols)}")
#     schema = "\n".join(schema_lines)

#     system = (
#         "You are a strict database query interpreter. Convert the user's natural-language request into a single-table structured query.\n"
#         "Rules:\n"
#         "1) Choose exactly ONE table from the provided schema that best fits the user's intent.\n"
#         "2) Output a Python dict with keys: operation ('select'), table (one of the schema tables), fields (list of column names from that table or ['*']), filters (dict), limit (int <= 50).\n"
#         "3) Use only column names that exist in the chosen table. Map simple synonyms to the correct column name.\n"
#         "4) For array columns, use {'contains': value}. For date ranges use {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}.\n"
#         "5) If you cannot confidently map constraints to specific columns, put them into {'free_text': '<terms>'}.\n"
#         "6) Return a valid Python dict literal only. Do not return JSON or extraneous text.\n"

        
#     )

#     examples = f"""
# Schema:
# {schema}

# Example 1:
# User: show completed projects for client harsh sir
# Return: {{"operation":"select","table":"projects","fields":["*"],"filters":{{"status":"Completed","client_name":"harsh sir"}}, "limit":20}}

# Example 2:
# User: who logged in today
# Return: {{"operation":"select","table":"employee_login","fields":["*"],"filters":{{"login_time":{{"start":"2025-08-15","end":"2025-08-15"}}}}, "limit":20}}

# Example 3:
# User: list users with role admin
# Return: {{"operation":"select","table":"user_perms","fields":["*"],"filters":{{"role":"admin"}}, "limit":20}}

# Example 4:
# User: search memory for zeel
# Return: {{"operation":"select","table":"user_memory","fields":["*"],"filters":{{"name":"zeel"}}, "limit":20}}

# Example 5:
# User: projects using react
# Return: {{"operation":"select","table":"projects","fields":["*"],"filters":{{"tech_stack":{{"contains":"React"}}}}, "limit":20}}

# Example 6:
# User: anything about new ai initiative
# Return: {{"operation":"select","table":"projects","fields":["*"],"filters":{{"free_text":"new ai initiative"}}, "limit":20}}
# """

#     prompt = f"{system}\n\n{examples}\nUser: {user_input}\nReturn:"

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
#             },
#             timeout=15
#         )
#         content = res.json()["choices"][0]["message"]["content"]
#         parsed = literal_eval(content)

#         # Basic sanity checks & defaults
#         if not isinstance(parsed, dict):
#             return {"operation": "none"}
#         if parsed.get("operation") != "select":
#             parsed["operation"] = "select"
#         table = parsed.get("table")
#         if table not in TABLES:
#             return {"operation": "none"}
#         if "fields" not in parsed or not parsed["fields"]:
#             parsed["fields"] = ["*"]
#         if "filters" not in parsed or not isinstance(parsed["filters"], dict):
#             parsed["filters"] = {}
#         if "limit" not in parsed or not isinstance(parsed["limit"], int):
#             parsed["limit"] = 20
#         parsed["limit"] = min(parsed["limit"], 50)
#         return parsed
#     except Exception as e:
#         print("❌ parse_user_query error:", e)
#         return {"operation": "none"}

# # ---------------- llm response ----------------
# def llm_response(user_input):
#     memory = load_memory()
#     memory = update_user_memory(user_input, memory)
#     save_memory(memory)

#     parsed = parse_user_query(user_input)
#     if parsed.get("operation") == "none":
#         return {"reply": "🤖 I couldn't understand that request. Can you rephrase it?"}

#     reply = query_supabase(parsed)
#     session({"role": "assistant", "content": reply})
#     return {"reply": reply}


# # --- Greeting prompt handling logic ---
# import random
# import re
# from datetime import datetime

# def handle_greetings(user_message: str, user_name: str = None):
#     """
#     Detect greetings more dynamically and generate varied, contextual replies.
#     """

#     # Normalize user input
#     normalized = user_message.lower().strip()

#     # Regex-based detection for greetings (covers hi, hello, hey, gm, ga, ge, etc.)
#     greeting_patterns = [
#         r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgood\s*morning\b",
#         r"\bgood\s*afternoon\b", r"\bgood\s*evening\b", r"\bgm\b", r"\bga\b", r"\bge\b"
#     ]

#     if any(re.search(pattern, normalized) for pattern in greeting_patterns):

#         # Time-based context
#         current_hour = datetime.now().hour
#         if current_hour < 12:
#             tod = "morning"
#         elif current_hour < 18:
#             tod = "afternoon"
#         else:
#             tod = "evening"

#         # Personalized if name is available
#         if user_name:
#             templates = [
#                 f"Good {tod}, {user_name}! 🌞 How’s your day going?",
#                 f"Hey {user_name}! 👋 Hope you’re having a great {tod}.",
#                 f"Hi {user_name}, always nice to chat with you 😊",
#                 f"Hello {user_name}! 🌟 What can I do for you today?",
#                 f"Hey {user_name}, welcome back! 🚀"
#             ]
#         else:
#             templates = [
#                 f"Good {tod}! 🌞 How can I help you?",
#                 f"Hey there! 👋 Hope you’re having a great {tod}.",
#                 "Hi! 😊 What would you like to know today?",
#                 "Hello! 🌟 How can I assist you?",
#                 "Hey! 🚀 Always happy to help."
#             ]

#         return random.choice(templates)

#     return None

# # ====================== ROLE-BASED QUERY FILTERING ======================

# def query_supabase(parsed):
#     """
#     Run a structured query against Supabase with automatic access-control filters.
#     Restrictions apply ONLY to Supabase queries.
#     """
#     try:
#         table = parsed.get("table")
#         filters = parsed.get("filters", {}) or {}
#         limit = parsed.get("limit", 10)
#         fields = parsed.get("fields", ["*"])
#         user_email = session.get("user_email")
#         user_role = get_user_role(user_email)

#         print(f"🔍 Query request: table={table}, filters={filters}, role={user_role}, email={user_email}")

#         # --- Build base query ---
#         select_clause = ",".join(fields) if fields != ["*"] else "*"
#         query = supabase.table(table).select(select_clause)

#         # --- Apply user-specified filters ---
#         free_text = None
#         if "free_text" in filters:
#             free_text = str(filters.pop("free_text")).strip()
#         for field, value in filters.items():
#             if value:
#                 query = _apply_filter(query, field, value)

#         # ==========================================================
#         # 🔒 Role-based access enforcement
#         # ==========================================================
#         role = (user_role or "Employee").lower()

#         if role == "admin":
#             pass  # unrestricted access

#         elif role == "hr":
#             # unrestricted access to employees + projects
#             pass

#         elif role == "manager":
#             if table == "projects":
#                 # Restrict to projects managed by this user
#                 query = query.contains("leader_of_project", [user_email])

#         else:
#             # Employee or unknown role
#             if table == "projects":
#                 query = query.contains("assigned_to_emails", [user_email])
#             elif table == "employee_login":
#                 # Employees should not see other employees' login info
#                 query = query.eq("email", user_email)

#         # ==========================================================
#         # Free-text fallback OR search
#         # ==========================================================
#         if free_text:
#             cols = [c for c in TABLES.get(table, []) if isinstance(c, str)]
#             if cols:
#                 or_parts = [f"{c}.ilike.%{free_text}%" for c in cols]
#                 or_clause = ",".join(or_parts)
#                 query = query.or_(or_clause)

#         # --- Execute query ---
#         data = query.limit(limit).execute().data or []

#         # --- Fallback fuzzy search if no results ---
#         if not data and (filters or free_text):
#             print("⚠️ No results. Trying fuzzy fallback...")
#             fuzzy_query = supabase.table(table).select(select_clause)
#             tokens = []
#             for v in filters.values():
#                 if isinstance(v, str):
#                     tokens.extend(re.findall(r'\w+', v))
#                 elif isinstance(v, dict) and "contains" in v:
#                     c = v["contains"]
#                     if isinstance(c, str):
#                         tokens.extend(re.findall(r'\w+', c))
#             if free_text:
#                 tokens.extend(re.findall(r'\w+', free_text))
#             tokens = [t for t in tokens if len(t) > 2]
#             if tokens:
#                 cols = [c for c in TABLES.get(table, []) if isinstance(c, str)]
#                 for token in set(tokens):
#                     token_clause = ",".join([f"{c}.ilike.%{token}%" for c in cols])
#                     fuzzy_query = fuzzy_query.or_(token_clause)

#                 # Apply role rules again
#                 if role == "manager" and table == "projects":
#                     fuzzy_query = fuzzy_query.contains("leader_of_project", [user_email])
#                 elif role not in ["admin", "hr"] and table == "projects":
#                     fuzzy_query = fuzzy_query.contains("assigned_to_emails", [user_email])
#                 elif role not in ["admin", "hr"] and table == "employee_login":
#                     fuzzy_query = fuzzy_query.eq("email", user_email)

#                 data = fuzzy_query.limit(limit).execute().data or []

#         if not data:
#             return "⚠️ No matching records found."

#         # --- Format results ---
#         formatted = []
#         for row in data:
#             details = []
#             for k, v in row.items():
#                 if v in [None, "", [], {}]:
#                     continue
#                 if isinstance(v, (list, dict)):
#                     v = json.dumps(v, ensure_ascii=False)
#                 details.append(f"{k.replace('_', ' ').title()}: {v}")
#             formatted.append("• " + "\n  ".join(details))

#         return "\n\n---\n\n".join(formatted)

#     except Exception as e:
#         print("❌ Supabase error:", e)
#         traceback.print_exc()
#         return f"❌ Supabase error: {str(e)}"



# # ---------------- Routes ----------------
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

# @app.route("/debug_session")
# def debug_session():
#     return jsonify(dict(session))

# # this is latest documents based chat rote
# # Update the chat route with these improvements
# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json(force=True)
#         user_input = data.get("message", "").strip()
#         user_email = session.get("user_email")

#         if not user_email:
#             return jsonify({"reply": "❌ You need to login first to use the chatbot."})
#         if not user_input:
#             return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})


#         greeting_response = handle_greetings(user_input)
#         if greeting_response is not None:   # only trigger on greetings
#             return jsonify({"reply": greeting_response})

#         # Get user info for context
#         user_name = session.get("user_name", "")
#         user_role = get_user_role(user_email)

     
#         # Step 1: Always get relevant document context
#         doc_context = get_context(user_input)

        

#         # Step 2: Prepare system message with rich context
#         system_message = f"""You are a helpful AI assistant for our company. 
# Current user: {user_name} ({user_email}), Role: {user_role}.
# {f"Relevant documents:\n{doc_context}" if doc_context else ""}

# Available database tables:
# {json.dumps({table: list(cols) for table, cols in TABLES.items()}, indent=2)}


# Respond conversationally while providing accurate information."""

#         # Step 3: Build message history
#         conv_hist = session.get("conversation_history", [])
#         messages = [
#             {"role": "system", "content": system_message},
#             *conv_hist[-4:],  # Keep last 4 messages as context
#             {"role": "user", "content": user_input}
#         ]

#         # Step 4: Call LLM
#         llm_response = call_openrouter(
#             messages,
#             temperature=0.5,
#             max_tokens=1000
#         ) or ""

#         # Step 5: Decide whether to hit DB (LLM says to, or parse will identify a DB query)
#         parsed = parse_user_query(user_input)
#         db_answer = None
#         if parsed.get("operation") == "select" and parsed.get("table") in TABLES:
#             # If parse suggests DB usage, run it
#             db_answer = query_supabase(parsed)
#         elif needs_database_query(llm_response):
#             # If LLM says "check the DB" but parse failed, attempt a free-text project search across tables
#             # We'll attempt simple free_text queries against all tables (industry fallback)
#             combined = []
#             tokens = " ".join(re.findall(r'\w+', user_input))
#             for tbl in TABLES.keys():
#                 try:
#                     parsed_try = {"operation": "select", "table": tbl, "fields": ["*"], "filters": {"free_text": tokens}, "limit": 5}
#                     res_try = query_supabase(parsed_try)
#                     if res_try and not res_try.startswith("⚠️"):
#                         combined.append(f"--- {tbl} ---\n{res_try}")
#                 except:
#                     continue
#             if combined:
#                 db_answer = "\n\n".join(combined)

#         # Step 6: If we got DB results, ask LLM to explain them conversationally
#         if db_answer and not db_answer.startswith("⚠️"):
#             explain_prompt = f"""Please convert these database results into a helpful reply for the user.\n\nUser question: {user_input}\n\nDatabase results:\n{db_answer}"""
#             explained = call_openrouter([
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": explain_prompt}
#             ])
#             llm_response = explained or db_answer

#         # Step 7: Save to conversation history and return
#         conv_hist.append({"role": "user", "content": user_input})
#         conv_hist.append({"role": "assistant", "content": llm_response})
#         session["conversation_history"] = conv_hist[-20:]

#         return jsonify({"reply": llm_response})

#     except Exception as e:
#         print("Chat error:", traceback.format_exc())
#         return jsonify({"reply": "Sorry, I encountered an error. Please try again."})

        
# if __name__ == "__main__":
#     if collection.count() == 0:
#         load_documents()
#     app.run(debug=True)




# =========================================================================================18/8 unstrutre ================================================================================================================


# role base and identity based access but not have proper structure in reply 
# from dataclasses import field
# from flask import Flask, request, jsonify, render_template, session
# from flask_session import Session
# import os, requests, re, json, random, traceback
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


# # ---------------- Load Environment Variables ----------------
# load_dotenv()
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# print(f"Loaded OPENROUTER_API_KEY: '{OPENROUTER_API_KEY}'")

# if not OPENROUTER_API_KEY:
#     raise ValueError("OPENROUTER_API_KEY not set — please check your .env")
# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# # ---------------- Initialize Clients ----------------
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5hZHhyZXhwZmNwbm9jbnNqamJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjAwNzMsImV4cCI6MjA2NzAzNjA3M30.5T0hxDZabIJ_mTrtKpra3beb7OwnnvpNcUpuAhd28Mw'")
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config["SESSION_PERMANENT"] = False
# CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:5173"])
# Session(app)

# # Persistent ChromaDB
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

# # Known Supabase tables (schema)
# TABLES = {
#     "projects": ["id", "project_name", "project_description", "start_date", "end_date", "status",
#                  "assigned_to_emails", "client_name", "upload_documents", "project_scope",
#                  "tech_stack", "tech_stack_custom", "leader_of_project", "project_responsibility",
#                  "role", "role_answers", "custom_questions", "custom_answers", "priority"],
#     "employee_login": ["id", "email", "login_time", "name", "logout_time", "pass"],
#     "user_memory": ["id", "user_id", "name", "known_facts"],
#     "user_perms": ["id", "name", "email", "password", "role", "permission_roles"],
#     "fields ": {
#         "project_name", "status", "tech_stack", "project_description",
#         "start_date", "end_date", "assigned_to_emails", "client_name",
#         "project_scope", "tech_stack_custom", "leader_of_project",
#         "project_responsibility", "role_answers", "custom_questions",
#         "custom_answers", "priority"
#     }
# }

# # Tables that must be access-controlled by role/email
# ACCESS_CONTROLLED = {"projects", "employee_login"}



# # -------------------- ACCESS CONTROL LOGIC --------------------

# class AccessControl:
#     """
#     Role + Identity Based Access Control
#     - Admin, HR → full access to all projects
#     - Employee, Others → restricted to their assigned projects only
#     """

#     def __init__(self):
#         self.role_policies = {
#             "Admin": {"scope": "all"},
#             "HR": {"scope": "all"},
#             "Employee": {"scope": "self"},
#             "Others": {"scope": "self"},
#         }

#     def get_policy(self, role: str):
#         """Return access policy for the role"""
#         return self.role_policies.get(role, {"scope": "self"})

#     def apply_project_filters(self, query, role: str, user_email: str):
#         """
#         Modify query based on role & identity
#         """
#         policy = self.get_policy(role)

#         # Admin/HR → unrestricted access
#         if policy["scope"] == "all":
#             return query

#         # Employees/Others → restricted
#         if policy["scope"] == "self":
#             return query.eq("assigned_to", user_email)

#         return query


# access_control = AccessControl()


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

# # ---------------- Document Processing ----------------
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
#     if len(query.split()) <= 2:
#         return ""
#     try:
#         results = collection.query(query_texts=[query], n_results=k)
#         if results and results.get('documents'):
#             return "\n".join(results['documents'][0])
#     except:
#         return ""
#     return ""

# def get_user_role(email):
#     """Fetch user role from Supabase; default to 'Employee'."""
#     try:
#         res = supabase.table("user_perms").select("role").eq("email", email).execute()
#         return res.data[0].get("role", "Employee") if res.data else "Employee"
#     except:
#         return "Employee"

# def needs_database_query(llm_response):
#     """Determine if we need to query the database (LLM hints only)."""
#     triggers = [
#         "check the database",
#         "look up in the system",
#         "query the records",
#         "i don't have that information",
#         "data shows",
#         "fetch from database",
#         "from db",
#         "from database",
#     ]
#     return any(trigger in llm_response.lower() for trigger in triggers)

# def explain_database_results(user_input, db_results, user_context):
#     """Convert raw DB results to natural language (LLM not restricted)."""
#     prompt = f"""Convert these database results into a friendly response:

# User asked: "{user_input}"
# User context: {user_context}
# Database results:
# {db_results}

# Respond in 1-4 paragraphs using natural language, focusing on the key information.
# respond in summary not in too long responce
# if user ask for all project details give all project details alocated to that user"""
#     return call_openrouter([
#         {"role": "system", "content": "You are a helpful assistant that explains data."},
#         {"role": "user", "content": prompt}
#     ])

# # ---------------- build messages ----------------
# def build_messages(user_input, context, memory):
#     name = memory.get("user_name", "")
#     if name:
#         user_input = f"{name} asked: {user_input}"

#     if context:
#         prompt = (
#             "You are a helpful assistant. Your job is to answer the user question first, clearly and directly.\n"
#             "Context may contain facts from company documents. Do not ignore the question. Do not apologize unless wrong."
#             """
#     Format Supabase query results into a clean, human-readable response.
#     Dynamically adjusts structure based on query type and dataset.

#     Parameters:
#         data (list[dict]): List of records from Supabase query.
#         query_type (str): Type of query (projects, employees, memory, general).

#     Returns:
#         str: Formatted response for the chatbot.
#     """
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

# # ---------------- OpenRouter ----------------
# def call_openrouter(messages, temperature=0.5, max_tokens=500):
#     """Centralized call to OpenRouter with error handling."""
#     try:
#         res = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {'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'}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "mistralai/mistral-7b-instruct",
#                 "messages": messages,
#                 "temperature": temperature,
#                 "max_tokens": max_tokens
#             },
#             timeout=15
#         )
#         if res.status_code != 200:
#             print(f"⚠️ OpenRouter API error {res.status_code}: {res.text}")
#             return None
#         data = res.json()
#         if "choices" not in data:
#             print("⚠️ Missing 'choices' in API response:", data)
#             return None
#         return data["choices"][0]["message"]["content"]
#     except Exception as e:
#         print("❌ Exception calling OpenRouter:", e)
#         traceback.print_exc()
#         return None

# # ---------------- Helpers for Supabase filtering ----------------
# def _is_int_like(val):
#     """Return True if value represents an integer (so we should use eq instead of ilike)."""
#     try:
#         if isinstance(val, int):
#             return True
#         s = str(val).strip()
#         return re.fullmatch(r"-?\d+", s) is not None
#     except:
#         return False

# def _apply_filter(query, field, value):
#     """
#     Apply type-aware filter to a supabase query builder:
#       - arrays (list or dict{'contains':...}) -> .contains
#       - ints -> .eq
#       - small tokens (<=4 chars) -> prefix ilike
#       - longer strings -> fuzzy ilike
#       - dict with start/end -> date range handling via gte/lte
#     """
#     # arrays / contains
#     if isinstance(value, dict) and "contains" in value:
#         contains_val = value["contains"]
#         if isinstance(contains_val, list):
#             for v in contains_val:
#                 query = query.contains(field, [v])
#         else:
#             query = query.contains(field, [contains_val])
#         return query

#     # date range
#     if isinstance(value, dict) and ("start" in value or "end" in value):
#         if "start" in value and value["start"]:
#             query = query.gte(field, value["start"])
#         if "end" in value and value["end"]:
#             query = query.lte(field, value["end"])
#         return query

#     # numeric exact match
#     if _is_int_like(value):
#         try:
#             return query.eq(field, int(str(value).strip()))
#         except:
#             pass

#     # string fuzzy/prefix
#     if isinstance(value, str):
#         v = value.strip()
#         if len(v) <= 4:
#             return query.ilike(field, f"{v}%")
#         else:
#             return query.ilike(field, f"%{v}%")

#     # fallback equality
#     return query.eq(field, value)

# # ---------------- AI Query Parsing (LLM-driven) ----------------
# def parse_user_query(user_input):
#     """
#     Use the LLM to pick the best table and map user constraints to actual columns.
#     Returns a dict: {"operation":"select","table":..., "fields":[...], "filters":{...}, "limit":int}
#     If the LLM can't map, returns {"operation":"none"}.
#     """
#     # Build schema description from TABLES
#     schema_lines = []
#     for t, cols in TABLES.items():
#         if isinstance(cols, list):
#             schema_lines.append(f"{t}: {', '.join(cols)}")
#     schema = "\n".join(schema_lines)

#     system = (
#         "You are a strict database query interpreter. Convert the user's natural-language request into a single-table structured query.\n"
#         "Rules:\n"
#         "1) Choose exactly ONE table from the provided schema that best fits the user's intent.\n"
#         "2) Output a Python dict with keys: operation ('select'), table (one of the schema tables), fields (list of column names from that table or ['*']), filters (dict), limit (int <= 50).\n"
#         "3) Use only column names that exist in the chosen table. Map simple synonyms to the correct column name.\n"
#         "4) For array columns, use {'contains': value}. For date ranges use {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}.\n"
#         "5) If you cannot confidently map constraints to specific columns, put them into {'free_text': '<terms>'}.\n"
#         "6) Return a valid Python dict literal only. Do not return JSON or extraneous text.\n"
#     )

#     examples = f"""
# Schema:
# {schema}

# Example 1:
# User: show completed projects for client harsh sir
# Return: {{"operation":"select","table":"projects","fields":["*"],"filters":{{"status":"Completed","client_name":"harsh sir"}}, "limit":20}}

# Example 2:
# User: who logged in today
# Return: {{"operation":"select","table":"employee_login","fields":["*"],"filters":{{"login_time":{{"start":"2025-08-15","end":"2025-08-15"}}}}, "limit":20}}

# Example 3:
# User: list users with role admin
# Return: {{"operation":"select","table":"user_perms","fields":["*"],"filters":{{"role":"admin"}}, "limit":20}}

# Example 4:
# User: search memory for zeel
# Return: {{"operation":"select","table":"user_memory","fields":["*"],"filters":{{"name":"zeel"}}, "limit":20}}

# Example 5:
# User: projects using react
# Return: {{"operation":"select","table":"projects","fields":["*"],"filters":{{"tech_stack":{{"contains":"React"}}}}, "limit":20}}

# Example 6:
# User: anything about new ai initiative
# Return: {{"operation":"select","table":"projects","fields":["*"],"filters":{{"free_text":"new ai initiative"}}, "limit":20}}
# """
#     prompt = f"{system}\n\n{examples}\nUser: {user_input}\nReturn:"

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
#                 "temperature": 0.2,
#                 "max_tokens": 300
#             },
#             timeout=15
#         )
#         content = res.json()["choices"][0]["message"]["content"]
#         parsed = literal_eval(content)

#         # Basic sanity checks & defaults
#         if not isinstance(parsed, dict):
#             return {"operation": "none"}
#         if parsed.get("operation") != "select":
#             parsed["operation"] = "select"
#         table = parsed.get("table")
#         if table not in TABLES:
#             return {"operation": "none"}
#         if "fields" not in parsed or not parsed["fields"]:
#             parsed["fields"] = ["*"]
#         if "filters" not in parsed or not isinstance(parsed["filters"], dict):
#             parsed["filters"] = {}
#         if "limit" not in parsed or not isinstance(parsed["limit"], int):
#             parsed["limit"] = 20
#         parsed["limit"] = min(parsed["limit"], 50)
#         return parsed
#     except Exception as e:
#         print("❌ parse_user_query error:", e)
#         return {"operation": "none"}

# # ---------------- LLM response ----------------
# def llm_response(user_input):
#     memory = load_memory()
#     memory = update_user_memory(user_input, memory)
#     save_memory(memory)

#     parsed = parse_user_query(user_input)
#     if parsed.get("operation") == "none":
#         return {"reply": "🤖 I couldn't understand that request. Can you rephrase it?"}

#     reply = query_supabase(parsed)
#     session({"role": "assistant", "content": reply})
#     return {"reply": reply}

# # --- Greeting prompt handling logic ---
# import random
# import re
# from datetime import datetime

# def handle_greetings(user_message: str, user_name: str = None):
#     """Detect greetings and generate varied, contextual replies."""
#     normalized = user_message.lower().strip()
#     greeting_patterns = [
#         r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgood\s*morning\b",
#         r"\bgood\s*afternoon\b", r"\bgood\s*evening\b", r"\bgm\b", r"\bga\b", r"\bge\b"
#     ]
#     if any(re.search(pattern, normalized) for pattern in greeting_patterns):
#         current_hour = datetime.now().hour
#         if current_hour < 12:
#             tod = "morning"
#         elif current_hour < 18:
#             tod = "afternoon"
#         else:
#             tod = "evening"
#         if user_name:
#             templates = [
#                 f"Good {tod}, {user_name}! 🌞 How’s your day going?",
#                 f"Hey {user_name}! 👋 Hope you’re having a great {tod}.",
#                 f"Hi {user_name}, always nice to chat with you 😊",
#                 f"Hello {user_name}! 🌟 What can I do for you today?",
#                 f"Hey {user_name}, welcome back! 🚀"
#             ]
#         else:
#             templates = [
#                 f"Good {tod}! 🌞 How can I help you?",
#                 f"Hey there! 👋 Hope you’re having a great {tod}.",
#                 "Hi! 😊 What would you like to know today?",
#                 "Hello! 🌟 How can I assist you?",
#                 "Hey! 🚀 Always happy to help."
#             ]
#         return random.choice(templates)
#     return None

# # ====================== STRONG ROLE-BASED QUERY FILTERING ======================
# def _apply_access_controls(table: str, query, role: str, user_email: str):
#     """
#     Enforce RBAC/IBAC ONLY on Supabase data fetching.
#     Rules:
#       - Admin: unrestricted across all tables.
#       - HR: unrestricted for 'projects' and 'employee_login'.
#       - Manager: 'projects' restricted to those they manage (leader_of_project contains user_email).
#       - Employee/Other: 'projects' where assigned_to_emails contains user_email;
#                         'employee_login' only their own record.
#       - Other tables: no additional restrictions (unless specified above).
#     """
#     r = (role or "Employee").strip().lower()
#     t = (table or "").strip().lower()

#     # Admin: no restriction
#     if r == "admin":
#         return query

#     # HR: unrestricted on projects and employee_login
#     if r == "hr":
#         return query

#     # Manager: restrict projects to those they lead
#     if r == "manager":
#         if t == "projects":
#             return query.contains("leader_of_project", [user_email])
#         if t == "employee_login":
#             # Not specified: default to self only
#             return query.eq("email", user_email)
#         return query

#     # Employee/Other: strict
#     if r in ["employee", "other"]:
#         if t == "projects":
#             return query.contains("assigned_to_emails", [user_email])
#         if t == "employee_login":
#             return query.eq("email", user_email)
#         return query

#     # Fallback: treat as Employee
#     if t == "projects":
#         return query.contains("assigned_to_emails", [user_email])
#     if t == "employee_login":
#         return query.eq("email", user_email)
#     return query



# def format_results_as_table(data: list[dict]) -> str:
#     """
#     Converts list of dicts into a Markdown table string.
#     """
#     if not data:
#         return "⚠️ No matching records found."

#     # Extract headers
#     headers = list(data[0].keys())

#     # Build markdown table
#     table = "| " + " | ".join(headers) + " |\n"
#     table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

#     for row in data:
#         row_vals = [str(row.get(h, "")) for h in headers]
#         table += "| " + " | ".join(row_vals) + " |\n"

#     return table



# def query_supabase(parsed):
#     """
#     Run a structured query against Supabase with automatic access-control filters.
#     Restrictions apply ONLY to Supabase queries (LLM responses are unrestricted).
#     """
#     try:
#         table = parsed.get("table")
#         filters = parsed.get("filters", {}) or {}
#         limit = parsed.get("limit", 10)
#         fields = parsed.get("fields", ["*"])
#         user_email = session.get("user_email")
#         user_role = get_user_role(user_email)

#         print(f"🔍 Query request: table={table}, filters={filters}, role={user_role}, email={user_email}")

#         # --- Build base query ---
#         select_clause = ",".join(fields) if fields != ["*"] else "*"
#         query = supabase.table(table).select(select_clause)

#         # --- Apply user-specified filters (structured) ---
#         free_text = None
#         if "free_text" in filters:
#             free_text = str(filters.pop("free_text")).strip()
#         for field, value in filters.items():
#             if value is None or value == "":
#                 continue
#             query = _apply_filter(query, field, value)

#         # --- Apply RBAC/IBAC only for access-controlled tables ---
#         if table in ACCESS_CONTROLLED:
#             query = _apply_access_controls(table, query, user_role, user_email)
            

#         # --- Free-text OR across all columns ---
#         if free_text:
#             cols = [c for c in TABLES.get(table, []) if isinstance(c, str)]
#             if cols:
#                 or_parts = [f"{c}.ilike.%{free_text}%" for c in cols]
#                 or_clause = ",".join(or_parts)
#                 query = query.or_(or_clause)

#         # --- Execute query ---
#         data = query.limit(limit).execute().data or []

#         # --- Fallback fuzzy search if no results (re-apply RBAC) ---
#         if not data and (filters or free_text):
#             print("🔎 No results — attempting fuzzy fallback...")
#             fuzzy_query = supabase.table(table).select(select_clause)

#             # Apply tokens over all columns
#             tokens = []
#             for v in filters.values():
#                 if isinstance(v, str):
#                     tokens.extend(re.findall(r'\w+', v))
#                 elif isinstance(v, dict) and "contains" in v:
#                     c = v["contains"]
#                     if isinstance(c, str):
#                         tokens.extend(re.findall(r'\w+', c))
#             if free_text:
#                 tokens.extend(re.findall(r'\w+', free_text))
#             tokens = [t for t in tokens if len(t) > 2]

#             if tokens:
#                 cols = [c for c in TABLES.get(table, []) if isinstance(c, str)]
#                 for token in set(tokens):
#                     token_clause = ",".join([f"{c}.ilike.%{token}%" for c in cols])
#                     fuzzy_query = fuzzy_query.or_(token_clause)

#             # Re-apply RBAC for fallback
#             if table in ACCESS_CONTROLLED:
#                 fuzzy_query = _apply_access_controls(table, fuzzy_query, user_role, user_email)

#             data = fuzzy_query.limit(limit).execute().data or []

#         if not data:
#             return "⚠️ No matching records found."

#         # --- Format results (LLM visibility is NOT restricted) ---
#         formatted = []
#         for row in data:
#             details = []
#             for k, v in row.items():
#                 if v in [None, "", [], {}]:
#                     continue
#                 if isinstance(v, (list, dict)):
#                     try:
#                         v = json.dumps(v, ensure_ascii=False)
#                     except:
#                         v = str(v)
#                 details.append(f"{k.replace('_', ' ').title()}: {v}")
#             formatted.append("• " + "\n  ".join(details))

#         return "\n\n---\n\n".join(formatted)

#     except Exception as e:
#         print("❌ Supabase error:", e)
#         traceback.print_exc()
#         # Fallback: safer exact-match attempt with RBAC reapplied
#         try:
#             table = parsed.get("table")
#             filters = parsed.get("filters", {}) or {}
#             fallback_query = supabase.table(table).select("*")
#             for field, value in filters.items():
#                 if isinstance(value, dict) and "contains" in value:
#                     fallback_query = fallback_query.contains(field, [value["contains"]])
#                 elif _is_int_like(value):
#                     fallback_query = fallback_query.eq(field, int(str(value).strip()))
#                 else:
#                     fallback_query = fallback_query.eq(field, str(value).strip())
#             # Re-apply RBAC in fallback
#             if table in ACCESS_CONTROLLED:
#                 user_email = session.get("user_email")
#                 user_role = get_user_role(user_email)
#                 fallback_query = _apply_access_controls(table, fallback_query, user_role, user_email)

#             data = fallback_query.limit(parsed.get("limit", 10)).execute().data or []
#             if not data:
#                 return "⚠️ No matching records found."
#             formatted = []
#             for row in data:
#                 details = [
#                     f"{k.replace('_', ' ').title()}: {v}"
#                     for k, v in row.items()
#                     if v not in [None, "", [], {}]
#                 ]
#                 formatted.append("• " + "\n  ".join(details))
#             return "\n\n---\n\n".join(formatted)
#         except Exception as e2:
#             print("Fallback query also failed:", e2)
#             traceback.print_exc()
#             return f"❌ Supabase error: {str(e)}"

# # ---------------- Routes ----------------
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

# @app.route("/debug_session")
# def debug_session():
#     return jsonify(dict(session))

# # Chat route
# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json(force=True)
#         user_input = data.get("message", "").strip()
#         user_email = session.get("user_email")

#         if not user_email:
#             return jsonify({"reply": "❌ You need to login first to use the chatbot."})
#         if not user_input:
#             return jsonify({"reply": random.choice(CONFUSION_RESPONSES)})

#         greeting_response = handle_greetings(user_input)
#         if greeting_response is not None:
#             return jsonify({"reply": greeting_response})

#         # Get user info for context (LLM remains unrestricted)
#         user_name = session.get("user_name", "")
#         user_role = get_user_role(user_email)

#         # Step 1: Document context (unrestricted)
#         doc_context = get_context(user_input)

#         # Step 2: System message
#         system_message = f"""You are a helpful AI assistant for our company.
# Current user: {user_name} ({user_email}), Role: {user_role}.
# {f"Relevant documents:\n{doc_context}" if doc_context else ""}

# Available database tables:
# {json.dumps({table: list(cols) for table, cols in TABLES.items()}, indent=2)}

# Respond conversationally while providing accurate information."""


#         # Step 3: Build history
#         conv_hist = session.get("conversation_history", [])
#         messages = [
#             {"role": "system", "content": system_message},
#             *conv_hist[-4:],
#             {"role": "user", "content": user_input}
#         ]

#         # Step 4: LLM call (unrestricted)
#         llm_resp_text = call_openrouter(
#             messages,
#             temperature=0.6,
#             max_tokens=1000
#         ) or ""

#         # Step 5: Decide DB usage
#         parsed = parse_user_query(user_input)
#         db_answer = None
#         if parsed.get("operation") == "select" and parsed.get("table") in TABLES:
#             db_answer = query_supabase(parsed)
#         elif needs_database_query(llm_resp_text):
#             combined = []
#             tokens = " ".join(re.findall(r'\w+', user_input))
#             for tbl in TABLES.keys():
#                 try:
#                     parsed_try = {"operation": "select", "table": tbl, "fields": ["*"], "filters": {"free_text": tokens}, "limit": 5}
#                     res_try = query_supabase(parsed_try)
#                     if res_try and not res_try.startswith("⚠️"):
#                         combined.append(f"--- {tbl} ---\n{res_try}")
#                 except:
#                     continue
#             if combined:
#                 db_answer = "\n\n".join(combined)

#         # Step 6: If DB results, have LLM explain (LLM still unrestricted)
#         if db_answer and not db_answer.startswith("⚠️"):
#             explain_prompt = f"""Please convert these database results into a helpful reply for the user.

# User question: {user_input}

# Database results:
# {db_answer}"""
#             explained = call_openrouter([
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": explain_prompt}
#             ])
#             llm_resp_text = explained or db_answer

#         # Step 7: Save conversation
#         conv_hist.append({"role": "user", "content": user_input})
#         conv_hist.append({"role": "assistant", "content": llm_resp_text})
#         session["conversation_history"] = conv_hist[-20:]

#         return jsonify({"reply": llm_resp_text})

#     except Exception as e:
#         print("Chat error:", traceback.format_exc())
#         return jsonify({"reply": "Sorry, I encountered an error. Please try again."})

# if __name__ == "__main__":
#     if collection.count() == 0:
#         load_documents()
#     app.run(debug=True)
