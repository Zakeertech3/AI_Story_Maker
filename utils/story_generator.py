# utils/story_generator.py
import time
import re
from datetime import datetime
import streamlit as st
from groq import Groq
from utils.config import APP_CONFIG, get_model

class StoryGenerator:
    def __init__(self, api_key):
        """
        Initialize the story generator with an API key.
        
        Parameters:
        - api_key: Groq API key
        """
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
    
    def generate_story(self, title, genre, characters, setting, theme=None, word_count=None, temperature=None, model=None):
        """
        Generate a story using the Groq API.
        
        Parameters:
        - title: Story title (or None to auto-generate)
        - genre: Story genre
        - characters: Description of characters
        - setting: Description of setting
        - theme: Optional theme or central message
        - word_count: Approximate number of words for the story
        - temperature: Creativity parameter (0.0 to 1.0)
        - model: Groq model to use
        
        Returns:
        - Dictionary containing the story text and metadata
        """
        try:
            # Set defaults from config if not provided
            word_count = word_count or APP_CONFIG["default_word_count"]
            temperature = temperature or APP_CONFIG["default_temperature"]
            model = model or get_model()
            
            # Generate title if not provided
            title_prompt = ""
            if not title:
                title_prompt = "Generate a creative and captivating title for this story."
            
            # Track start time for performance monitoring
            start_time = time.time()
            
            # Prepare the prompt
            prompt = f"""
            {"Write a {genre.lower()} story with the following parameters:" if genre else "Write a story with the following parameters:"}
            
            {f"Title: {title}" if title else title_prompt}
            Characters: {characters}
            Setting: {setting}
            {f"Theme: {theme}" if theme else ""}
            
            The story should be approximately {word_count} words long.
            Include dialogue, descriptive language, and a satisfying plot arc.
            Format the story with proper paragraphs and a clear beginning, middle, and end.
            """
            
            # Generate story using Groq API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative storyteller. Your task is to write engaging, original stories based on user parameters. Make your stories vivid, emotionally resonant, and memorable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(word_count * 2, 4096),  # Adjust as needed, with a reasonable maximum
                temperature=temperature
            )
            
            # Calculate completion time
            completion_time = time.time() - start_time
            story_text = response.choices[0].message.content
            
            # Extract title if it was auto-generated
            if not title:
                # Try to find the title at the beginning of the text
                title_match = re.search(r'^(?:Title:\s*|\s*#\s*|\s*)(.*?)(?:\n|$)', story_text, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    title = "Untitled Story"
                
                # Remove the title line from the story text
                story_text = re.sub(r'^(?:Title:\s*|\s*#\s*|\s*)(.*?)(?:\n|$)', '', story_text, flags=re.IGNORECASE)
            
            # Prepare result with metadata
            result = {
                "title": title,
                "content": story_text.strip(),
                "metadata": {
                    "genre": genre,
                    "characters": characters,
                    "setting": setting,
                    "theme": theme,
                    "model": model,
                    "temperature": temperature,
                    "word_count": word_count,
                    "generation_time": round(completion_time, 2),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return result
        
        except Exception as e:
            st.error(f"Story generation failed: {str(e)}")
            raise Exception(f"Story generation failed: {str(e)}")
    
    def expand_story(self, original_story, expansion_request, model=None, temperature=None):
        """
        Expand or modify an existing story based on user request.
        
        Parameters:
        - original_story: Original story text
        - expansion_request: What the user wants to expand or modify
        - model: Groq model to use
        - temperature: Creativity parameter
        
        Returns:
        - Updated story text
        """
        try:
            # Set defaults from config if not provided
            temperature = temperature or APP_CONFIG["default_temperature"]
            model = model or get_model()
            
            # Prepare the prompt
            prompt = f"""
            Here is an existing story:
            
            {original_story}
            
            Please {expansion_request}. Maintain the same style, tone, and characters.
            Return the full updated story with your changes incorporated seamlessly.
            """
            
            # Generate expansion using Groq API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative storyteller. Your task is to expand or modify existing stories based on user requests while maintaining narrative consistency."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(len(original_story.split()) * 2, 4096),  # Twice the original length, with a maximum
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            st.error(f"Story expansion failed: {str(e)}")
            raise Exception(f"Story expansion failed: {str(e)}")


def generate_story(api_key, title, genre, characters, setting, word_count=None):
    """
    Legacy function for backwards compatibility.
    Generate a story using the Groq API.
    
    Parameters:
    - api_key: Groq API key
    - title: Story title
    - genre: Story genre
    - characters: Description of characters
    - setting: Description of setting
    - word_count: Approximate number of words for the story
    
    Returns:
    - Generated story text
    """
    generator = StoryGenerator(api_key)
    result = generator.generate_story(
        title=title,
        genre=genre,
        characters=characters,
        setting=setting,
        word_count=word_count or APP_CONFIG["default_word_count"]
    )
    return result["content"]