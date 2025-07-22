import json
import os
from datetime import datetime
import re

MEMORY_FILE = 'user_memories.json'
USER_MEMORY_FILE = 'memory.json'

def load_memories():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memories(memories):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memories, f, indent=2)

def load_user_memory():
    if os.path.exists(USER_MEMORY_FILE):
        with open(USER_MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {"user_name": "", "user_role": "", "user_memory": []}

def save_user_memory(memory):
    with open(USER_MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def update_memory(title, knowledge_to_store, action='create', existing_knowledge_id=None):
    memories = load_memories()
    
    if action == 'create':
        memory_id = f"memory_{len(memories) + 1}"
        memories[memory_id] = {
            'title': title,
            'content': knowledge_to_store,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    elif action == 'update' and existing_knowledge_id:
        if existing_knowledge_id in memories:
            memories[existing_knowledge_id]['content'] = knowledge_to_store
            memories[existing_knowledge_id]['updated_at'] = datetime.now().isoformat()
    elif action == 'delete' and existing_knowledge_id:
        if existing_knowledge_id in memories:
            del memories[existing_knowledge_id]
    
    save_memories(memories)
    return True

def extract_and_store_memory(user_input, bot_response):
    """
    Automatically extract and store important information from conversations
    """
    memories = load_memories()
    user_memory = load_user_memory()
    
    # Extract user name if mentioned
    name_patterns = [
        r"\b(?:my name is|this is|i am|i'm|this side) (\w+)\b",
        r"\b(?:call me|you can call me) (\w+)\b",
        r"\b(?:i'm called|i am called) (\w+)\b"
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, user_input, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).capitalize()
            user_memory["user_name"] = name
            # Store as a memory too
            memory_id = f"memory_{len(memories) + 1}"
            memories[memory_id] = {
                'title': 'User Name',
                'content': f"The user's name is {name}.",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            break
    
    # Extract role information
    role_patterns = [
        r"\b(?:i am a|i'm a|i work as a|my role is|my job is) ([^.!?]+)",
        r"\b(?:i work in|i'm in|my department is) ([^.!?]+)",
        r"\b(?:my position is|my title is) ([^.!?]+)"
    ]
    
    for pattern in role_patterns:
        role_match = re.search(pattern, user_input, re.IGNORECASE)
        if role_match:
            role = role_match.group(1).strip()
            user_memory["user_role"] = role
            # Store as a memory
            memory_id = f"memory_{len(memories) + 1}"
            memories[memory_id] = {
                'title': 'User Role',
                'content': f"The user works as {role}.",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            break
    
    # Extract preferences and important information
    preference_patterns = [
        r"\b(?:i like|i prefer|i enjoy|i love) ([^.!?]+)",
        r"\b(?:i don't like|i hate|i dislike) ([^.!?]+)",
        r"\b(?:my favorite|my preferred) ([^.!?]+)",
        r"\b(?:i need|i want|i require) ([^.!?]+)"
    ]
    
    for pattern in preference_patterns:
        preference_match = re.search(pattern, user_input, re.IGNORECASE)
        if preference_match:
            preference = preference_match.group(1).strip()
            # Create a meaningful title
            if "like" in user_input.lower() or "love" in user_input.lower() or "enjoy" in user_input.lower():
                title = f"User Preference: {preference[:30]}..."
            elif "don't like" in user_input.lower() or "hate" in user_input.lower() or "dislike" in user_input.lower():
                title = f"User Dislike: {preference[:30]}..."
            elif "need" in user_input.lower() or "want" in user_input.lower() or "require" in user_input.lower():
                title = f"User Need: {preference[:30]}..."
            else:
                title = f"User Information: {preference[:30]}..."
            
            memory_id = f"memory_{len(memories) + 1}"
            memories[memory_id] = {
                'title': title,
                'content': f"User mentioned: {preference}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            break
    
    # Extract project or work-related information
    project_patterns = [
        r"\b(?:i'm working on|i am working on|my project is|current project) ([^.!?]+)",
        r"\b(?:i have a project|my task is|i need to) ([^.!?]+)",
        r"\b(?:deadline|due date) ([^.!?]+)"
    ]
    
    for pattern in project_patterns:
        project_match = re.search(pattern, user_input, re.IGNORECASE)
        if project_match:
            project_info = project_match.group(1).strip()
            memory_id = f"memory_{len(memories) + 1}"
            memories[memory_id] = {
                'title': 'Project Information',
                'content': f"Project/Task related: {project_info}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            break
    
    # Save all memories
    save_memories(memories)
    save_user_memory(user_memory)
    
    return memories

def get_relevant_memories(query, limit=3):
    """
    Get memories that might be relevant to the current query
    """
    memories = load_memories()
    relevant_memories = []
    
    query_lower = query.lower()
    
    for memory_id, memory in memories.items():
        title_lower = memory['title'].lower()
        content_lower = memory['content'].lower()
        
        # Simple keyword matching
        if any(keyword in title_lower or keyword in content_lower 
               for keyword in query_lower.split()):
            relevant_memories.append(memory)
    
    # Return most recent relevant memories
    relevant_memories.sort(key=lambda x: x['updated_at'], reverse=True)
    return relevant_memories[:limit]

def get_user_context():
    """
    Get current user context for the chatbot
    """
    user_memory = load_user_memory()
    memories = load_memories()
    
    context = []
    
    if user_memory.get("user_name"):
        context.append(f"User name: {user_memory['user_name']}")
    
    if user_memory.get("user_role"):
        context.append(f"User role: {user_memory['user_role']}")
    
    # Add recent memories
    recent_memories = sorted(memories.values(), key=lambda x: x['updated_at'], reverse=True)[:3]
    for memory in recent_memories:
        context.append(f"Memory: {memory['title']} - {memory['content']}")
    
    return context 