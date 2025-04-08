# app.py
import streamlit as st
import json
import os
import time
import datetime
import uuid
import random
from pathlib import Path
from dotenv import load_dotenv

# Import from utils
from utils.config import (
    APP_CONFIG, get_api_key, get_model, 
    save_story_to_file, load_saved_stories,
    ensure_storage_directory
)
from utils.story_generator import StoryGenerator

# Load environment variables
load_dotenv()

# Initialize story state
def init_session_state():
    """Initialize session state variables"""
    # Core state variables
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "story_state" not in st.session_state:
        st.session_state.story_state = "welcome"
    
    if "genre" not in st.session_state:
        st.session_state.genre = None
    
    if "characters" not in st.session_state:
        st.session_state.characters = None
    
    if "setting" not in st.session_state:
        st.session_state.setting = None
    
    if "theme" not in st.session_state:
        st.session_state.theme = None
    
    if "title" not in st.session_state:
        st.session_state.title = None
    
    if "story_id" not in st.session_state:
        st.session_state.story_id = str(int(time.time()))
        
    if "timestamp" not in st.session_state:
        st.session_state.timestamp = datetime.datetime.now().isoformat()
    
    if "generated_story" not in st.session_state:
        st.session_state.generated_story = None
    
    if "saved_stories" not in st.session_state:
        st.session_state.saved_stories = load_saved_stories()
    
    # UI state
    if "show_api_settings" not in st.session_state:
        st.session_state.show_api_settings = not get_api_key()
    
    if "show_advanced_options" not in st.session_state:
        st.session_state.show_advanced_options = False
    
    if "model" not in st.session_state:
        st.session_state.model = APP_CONFIG["default_model"]
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = APP_CONFIG["default_temperature"]
    
    if "word_count" not in st.session_state:
        st.session_state.word_count = APP_CONFIG["default_word_count"]

def handle_input():
    """Handle user input submission"""
    if st.session_state.user_input and st.session_state.user_input.strip():
        # Get the current input value
        user_message = st.session_state.user_input
        
        # Process the message
        process_message(user_message)
        
        # The field will be cleared automatically as we're using the callback

def process_message(user_message):
    """Process the user message based on current state"""
    api_key = get_api_key()
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar first")
        return
        
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    
    # State machine for conversation flow
    if st.session_state.story_state == "welcome":
        # Welcome state - Ask for genre
        options = ", ".join(APP_CONFIG["genre_options"][:-1]) + ", or " + APP_CONFIG["genre_options"][-1]
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Great! Let's create a story together. What genre would you like? Choose from {options}, or suggest your own!"
        })
        st.session_state.story_state = "genre"
        
    elif st.session_state.story_state == "genre":
        # Genre state - Process genre and ask for characters
        st.session_state.genre = user_message
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"A {user_message} story sounds fun! Now, tell me about the main characters. Who should be in this story? Include their names, relationships, and a brief description."
        })
        st.session_state.story_state = "characters"
        
    elif st.session_state.story_state == "characters":
        # Characters state - Process characters and ask for setting
        st.session_state.characters = user_message
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Interesting characters! Next, describe the setting or world where this story takes place."
        })
        st.session_state.story_state = "setting"
        
    elif st.session_state.story_state == "setting":
        # Setting state - Process setting and ask for theme
        st.session_state.setting = user_message
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Great setting! Finally, do you have a theme or message you'd like to explore in this story? (Or type 'skip' to proceed without a theme)"
        })
        st.session_state.story_state = "theme"
        
    elif st.session_state.story_state == "theme":
        # Theme state - Process theme and ask for title
        if user_message.lower() != "skip":
            st.session_state.theme = user_message
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Would you like to provide a title for your story? (Or type 'skip' to let me generate one for you)"
        })
        st.session_state.story_state = "title"
        
    elif st.session_state.story_state == "title":
        # Title state - Process title and generate story
        if user_message.lower() != "skip":
            st.session_state.title = user_message
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Perfect! I'm working on your {st.session_state.genre} story{' titled ' + st.session_state.title if st.session_state.title else ''} about {st.session_state.characters} set in {st.session_state.setting}. This will take a moment..."
        })
        st.session_state.story_state = "generating"
        
    elif st.session_state.story_state == "display":
        # Display state - Handle feedback or requests about the story
        # Check for commands
        command = user_message.lower().strip()
        
        if "save" in command or "download" in command:
            # Save the story
            save_current_story()
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": f"✅ I've saved your story! You can find it in the sidebar. What would you like to do next? You can start a new story, or make changes to this one."
            })
        
        elif "new" in command or "another" in command or "start over" in command:
            # Start a new story
            reset_story_state()
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": f"Let's create a new story! What genre would you like for this one?"
            })
            st.session_state.story_state = "genre"
        
        elif any(word in command for word in ["revise", "change", "modify", "edit", "update", "rewrite"]):
            # Handle story revision request
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": f"I'll help you modify the story. Please tell me what changes you'd like to make."
            })
            st.session_state.story_state = "revising"
        
        else:
            # Default response
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": "What would you like to do with this story? You can save it, start a new one, or ask for specific changes."
            })
    
    elif st.session_state.story_state == "revising":
        # Revising state - Make changes to the story
        if st.session_state.generated_story:
            try:
                # Create generator
                api_key = get_api_key()
                generator = StoryGenerator(api_key)
                
                # Get the expansion
                revised_story = generator.expand_story(
                    st.session_state.generated_story["content"],
                    user_message,
                    model=st.session_state.model,
                    temperature=st.session_state.temperature
                )
                
                # Update the story
                st.session_state.generated_story["content"] = revised_story
                st.session_state.generated_story["metadata"]["last_revised"] = datetime.datetime.now().isoformat()
                
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": "I've updated your story with the requested changes. What would you like to do next?"
                })
                
                st.session_state.story_state = "display"
                
            except Exception as e:
                st.error(f"Failed to revise story: {str(e)}")
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": f"I'm sorry, I had trouble updating the story. Would you like to try again with a different request?"
                })

def generate_story_content():
    """Generate story content based on user inputs"""
    try:
        api_key = get_api_key()
        if not api_key:
            st.error("API key is required to generate a story")
            return False
            
        # Create story generator
        generator = StoryGenerator(api_key)
        
        # Generate the story
        story_result = generator.generate_story(
            title=st.session_state.title,
            genre=st.session_state.genre,
            characters=st.session_state.characters,
            setting=st.session_state.setting,
            theme=st.session_state.theme,
            word_count=st.session_state.word_count,
            temperature=st.session_state.temperature,
            model=st.session_state.model
        )
        
        # Store the result
        st.session_state.generated_story = story_result
        if not st.session_state.title and "title" in story_result:
            st.session_state.title = story_result["title"]
        
        # Add to chat history
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"📖 **{story_result['title']}**\n\n{story_result['content'][:200]}... *(full story shown below)*\n\nWhat would you like to do with this story? You can save it, start a new one, or ask for changes."
        })
        
        # Update state
        st.session_state.story_state = "display"
        return True
        
    except Exception as e:
        st.error(f"Failed to generate story: {str(e)}")
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"I'm sorry, I had trouble generating your story. Would you like to try again?"
        })
        # Revert to setting state
        st.session_state.story_state = "setting" 
        return False

def save_current_story():
    """Save the current story to a file"""
    if not st.session_state.generated_story:
        st.error("No story to save")
        return
    
    story = st.session_state.generated_story
    
    # Create metadata
    metadata = {
        "genre": st.session_state.genre,
        "characters": st.session_state.characters,
        "setting": st.session_state.setting,
        "theme": st.session_state.theme,
        "model": st.session_state.model,
        "temperature": st.session_state.temperature,
        "saved_at": datetime.datetime.now().isoformat()
    }
    
    # Save the story
    save_story_to_file(story["title"], story["content"], metadata)
    
    # Reload stories
    st.session_state.saved_stories = load_saved_stories()

def reset_story_state():
    """Reset story state for a new story"""
    st.session_state.genre = None
    st.session_state.characters = None
    st.session_state.setting = None
    st.session_state.theme = None
    st.session_state.title = None
    st.session_state.generated_story = None
    st.session_state.story_id = str(int(time.time()))
    st.session_state.timestamp = datetime.datetime.now().isoformat()

def toggle_advanced_options():
    """Toggle advanced options visibility"""
    st.session_state.show_advanced_options = not st.session_state.show_advanced_options

def set_model():
    """Set the model to use"""
    st.session_state.model = st.session_state.selected_model

def set_temperature():
    """Set the temperature to use"""
    st.session_state.temperature = st.session_state.selected_temperature

def set_word_count():
    """Set the word count to use"""
    st.session_state.word_count = st.session_state.selected_word_count

def main():
    # Page configuration with app name from config
    st.set_page_config(
        page_title=f"{APP_CONFIG['app_name']} - AI Storytelling", 
        page_icon=APP_CONFIG['app_icon'], 
        layout="wide",
        menu_items={
            'Get Help': 'https://groq.com/docs',
            'About': f"{APP_CONFIG['app_name']} v{APP_CONFIG['version']} - An AI-powered storytelling application"
        }
    )
    
    # Initialize all session state variables
    init_session_state()
    
    # Header with version
    st.title(f"{APP_CONFIG['app_icon']} {APP_CONFIG['app_name']}")
    st.caption(f"Chat with an AI storyteller to create your custom story • v{APP_CONFIG['version']}")
    
    # Check API key availability
    api_key = get_api_key()
    if not api_key and not st.session_state.show_api_settings:
        st.session_state.show_api_settings = True
    
    # Sidebar with saved stories and settings
    with st.sidebar:
        # Stories section
        st.header("Your Stories")
        
        # If we have saved stories, display them
        if st.session_state.saved_stories:
            # Add a new story button at the top
            if st.button("➕ New Story", use_container_width=True, type="primary"):
                reset_story_state()
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": f"Let's create a new story! What genre would you like?"
                })
                st.session_state.story_state = "genre"
                st.rerun()
            
            # Display saved stories
            st.subheader("Saved Stories")
            for i, story in enumerate(st.session_state.saved_stories):
                # Create a clickable card for each story
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(f"📖 {story['title']}", key=f"load_{i}", use_container_width=True):
                            # Load the story data
                            st.session_state.generated_story = story
                            st.session_state.genre = story.get('metadata', {}).get('genre')
                            st.session_state.characters = story.get('metadata', {}).get('characters')
                            st.session_state.setting = story.get('metadata', {}).get('setting')
                            st.session_state.theme = story.get('metadata', {}).get('theme')
                            st.session_state.title = story['title']
                            
                            # Update chat history to show the loaded story
                            st.session_state.chat_history.append({
                                "role": "assistant", 
                                "content": f"📖 I've loaded '{story['title']}'. What would you like to do with it? You can edit it, use it as inspiration for a new story, or start fresh."
                            })
                            st.session_state.story_state = "display"
                            st.rerun()
                    
                    # Show metadata in a tooltip/expander
                    with st.expander("ℹ️", expanded=False):
                        if 'metadata' in story:
                            st.write(f"**Genre:** {story['metadata'].get('genre', 'Unknown')}")
                            st.write(f"**Created:** {story['metadata'].get('saved_at', 'Unknown').split('T')[0]}")
        else:
            st.info("Start chatting to create your first story!")
        
        # Divider before settings
        st.divider()
        
        # Advanced Options (model selection, temperature, etc.)
        st.subheader("Story Settings")
        if st.button("Advanced Options", key="toggle_advanced", use_container_width=True):
            toggle_advanced_options()
            st.rerun()
        
        if st.session_state.show_advanced_options:
            with st.container():
                # Model selection
                st.selectbox(
                    "AI Model",
                    options=([st.session_state.model] + [
                        m for m in APP_CONFIG["alternative_models"] 
                        if m != st.session_state.model
                    ]),
                    key="selected_model",
                    on_change=set_model
                )
                
                # Temperature slider
                st.slider(
                    "Creativity",
                    min_value=0.0, max_value=1.0, step=0.1,
                    value=st.session_state.temperature,
                    key="selected_temperature",
                    on_change=set_temperature,
                    help="Higher values create more varied and creative outputs"
                )
                
                # Word count slider
                st.slider(
                    "Story Length",
                    min_value=300, max_value=2000, step=100,
                    value=st.session_state.word_count,
                    key="selected_word_count",
                    on_change=set_word_count,
                    help="Approximate word count for the generated story"
                )
        
        # API Key Settings
        if not api_key or st.session_state.show_api_settings:
            st.divider()
            st.subheader("API Settings")
            
            if api_key:
                st.success("✅ API key configured")
                if st.button("Hide API Settings", use_container_width=True):
                    st.session_state.show_api_settings = False
                    st.rerun()
            else:
                st.warning("⚠️ API key required")
                user_api_key = st.text_input("Enter Groq API Key", type="password")
                if user_api_key:
                    st.session_state.user_api_key = user_api_key
                    st.session_state.show_api_settings = False  # Hide after setting
                    st.success("API key set for this session")
                    st.rerun()
    
    # Main content area
    main_container = st.container()
    
    # Generate story if in generating state
    if st.session_state.story_state == "generating":
        try:
            # Display a spinner while generating
            with st.spinner("Generating your story... This may take a moment."):
                # Generate the story
                success = generate_story_content()
                if success:
                    st.rerun()  # Refresh to display the story
        except Exception as e:
            st.error(f"Failed to generate story: {str(e)}")
            
    # Display chat interface in the main container
    with main_container:
        # Display chat history
        if st.session_state.chat_history:
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.chat_message("user").markdown(message["content"])
                else:  # assistant
                    st.chat_message("assistant").markdown(message["content"])
        
        # Display story if in display state
        if st.session_state.story_state == "display" and st.session_state.generated_story:
            story = st.session_state.generated_story
            
            # Display full story in an expander
            with st.expander("📖 Full Story", expanded=True):
                st.markdown(f"## {story['title']}")
                st.markdown(story["content"])
                
                # Story metadata and controls
                col1, col2 = st.columns(2)
                with col1:
                    if 'metadata' in story:
                        metadata = story['metadata']
                        st.caption(f"Genre: {metadata.get('genre', 'Not specified')}")
                        if metadata.get('generation_time'):
                            st.caption(f"Generation time: {metadata.get('generation_time')} seconds")
                        if metadata.get('model'):
                            st.caption(f"Model: {metadata.get('model')}")
                
                with col2:
                    # Action buttons
                    if st.button("Save Story", key="save_button"):
                        save_current_story()
                        st.success("✅ Story saved!")
                    
                    if st.button("Start New Story", key="new_button"):
                        reset_story_state()
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": f"Let's create a new story! What genre would you like?"
                        })
                        st.session_state.story_state = "genre"
                        st.rerun()
        
        # Input at the bottom - only show if we have an API key
        if get_api_key():
            # Display different prompts based on state
            placeholder = "Type your message here..."
            if st.session_state.story_state == "genre":
                placeholder = "Enter a genre (e.g., Fantasy, Sci-Fi, Mystery)..."
            elif st.session_state.story_state == "characters":
                placeholder = "Describe your characters..."
            elif st.session_state.story_state == "setting":
                placeholder = "Describe the setting or world..."
            elif st.session_state.story_state == "theme":
                placeholder = "Enter a theme or message (or 'skip')..."
            elif st.session_state.story_state == "title":
                placeholder = "Enter a title (or 'skip' to auto-generate)..."
            elif st.session_state.story_state == "revising":
                placeholder = "Describe what changes you'd like to make..."
            
            # Initial welcome message if no chat history
            if not st.session_state.chat_history:
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": "Hello! I'm your AI storyteller. I can help you create custom stories. Would you like to start crafting a story together?"
                })
            
            # Chat input
            st.chat_input(
                placeholder=placeholder,
                key="user_input",
                on_submit=handle_input
            )
        else:
            st.warning("⚠️ Please enter your Groq API key in the sidebar to continue.")

if __name__ == "__main__":
    main()