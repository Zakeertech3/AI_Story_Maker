# utils/config.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Application configuration
APP_CONFIG = {
    "app_name": "StoryChat",
    "app_icon": "📚",
    "default_model": "llama3-70b-8192",
    "alternative_models": ["llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
    "default_temperature": 0.7,
    "default_max_tokens": 1500,
    "default_word_count": 800,
    "file_storage_path": "stories",
    "genre_options": [
        "Fantasy", "Science Fiction", "Mystery", "Romance", 
        "Adventure", "Horror", "Historical Fiction", "Comedy",
        "Thriller", "Western", "Fairy Tale"
    ],
    "version": "1.1.0"
}

def load_api_key():
    """
    Load the API key from environment variables or Streamlit secrets.
    Returns the API key or None if not found.
    """
    # Try to load from .env file
    load_dotenv()
    
    # First check if API key is in environment variables (from .env)
    api_key = os.getenv("GROQ_API_KEY")
    
    # If not in environment, try Streamlit secrets (for cloud deployment)
    if not api_key and "groq" in st.secrets:
        api_key = st.secrets["groq"]["api_key"]
        
    return api_key

def get_api_key():
    """
    Get the API key, either from environment/secrets or user input.
    Returns the API key or None if not available.
    """
    # First try to load from environment or secrets
    api_key = load_api_key()
    
    # If not found, use from session state (user input)
    if not api_key and "user_api_key" in st.session_state:
        api_key = st.session_state.user_api_key
        
    return api_key

def get_model():
    """
    Get the model to use, either from session state or default.
    """
    if "model" in st.session_state:
        return st.session_state.model
    return APP_CONFIG["default_model"]

def ensure_storage_directory():
    """
    Ensures the stories storage directory exists.
    Returns the path to the storage directory.
    """
    storage_path = Path(APP_CONFIG["file_storage_path"])
    storage_path.mkdir(exist_ok=True, parents=True)
    return storage_path

def save_story_to_file(title, content, metadata=None):
    """
    Save a story to a JSON file.
    
    Parameters:
    - title: Story title
    - content: Story content
    - metadata: Dictionary of additional metadata (genre, characters, etc.)
    
    Returns:
    - Path to the saved file
    """
    storage_path = ensure_storage_directory()
    
    # Create a safe filename from the title
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
    safe_filename = f"{safe_title}_{int(st.session_state.get('story_id', 0))}.json"
    file_path = storage_path / safe_filename
    
    # Prepare story data
    story_data = {
        "title": title,
        "content": content,
        "timestamp": st.session_state.get("timestamp", ""),
        "metadata": metadata or {}
    }
    
    # Save to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(story_data, f, indent=2)
    
    return file_path

def load_saved_stories():
    """
    Load all saved stories from the storage directory.
    
    Returns:
    - List of story dictionaries
    """
    storage_path = ensure_storage_directory()
    stories = []
    
    for file_path in storage_path.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                story_data = json.load(f)
                story_data["file_path"] = str(file_path)
                stories.append(story_data)
        except Exception as e:
            st.error(f"Error loading story {file_path}: {str(e)}")
    
    # Sort by timestamp if available
    stories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return stories