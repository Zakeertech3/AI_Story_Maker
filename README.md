# 📚 StoryChat – Your AI Storytelling Companion

Welcome to **StoryChat**, an AI-powered web app that turns your ideas into captivating stories!  
Using advanced language models from [Groq Cloud](https://console.groq.com/), this app helps you generate custom tales based on your genre, characters, setting, and theme.

![StoryChat Banner](https://github.com/user-attachments/assets/81fabc90-30d3-4966-bbb5-884acb23072a) <!-- Replace with your actual image path -->


🔗 Live Demo: https://storymakerai.streamlit.app/
---

## ✨ Features

👉 Chat-based interactive storytelling  
👉 Choose from genres like Fantasy, Sci-Fi, Romance, Thriller, etc.  
👉 Customize characters, settings, themes, and story titles  
👉 Select AI model and creativity level (temperature)  
👉 Auto-generate story titles if skipped  
👉 Save and revisit your stories anytime  
👉 Revise existing stories based on your feedback  
👉 Built with Streamlit + Groq API  

---

## 🗄 Demo Output Screenshots

### 🔒 Before Entering API Key

![Before API Key](https://github.com/user-attachments/assets/a86028ef-c8c1-4306-aa3e-18393e96be41)

### ✅ After Entering API Key

![After API Key - 1](https://github.com/user-attachments/assets/3a1c8ad6-6c9d-4c17-af2a-eccbca49cef2)

![After API Key - 2](https://github.com/user-attachments/assets/6af98e23-b190-42fc-b963-4c9fb8a25f93)

---

## 🚀 Getting Started

### 📁 Clone this repository

```bash
git clone https://github.com/Zakeertech3/AI_Story_Maker.git
cd AI_Story_Maker
```

### 🧱 Install dependencies

We recommend using a virtual environment.

```bash
pip install -r requirements.txt
```

### 🔐 Set your API key

Create a `.env` file in the project root with your [Groq API key](#🔑-how-to-get-your-groq-api-key):

```
GROQ_API_KEY=your_groq_api_key_here
```

Alternatively, you can enter it directly in the Streamlit sidebar at runtime.

---

## 💻 Run the App

```bash
streamlit run app.py
```

Once the app starts, it will guide you through an interactive chat to build your story.

---

## 🔑 How to Get Your Groq API Key

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)  
2. Log in or sign up for a free account  
3. Click **"Create API Key"**  
4. Copy the generated key and paste it into your `.env` file or enter it in the sidebar

> 🧠 Tip: Your API key lets you access Groq's blazing-fast inference models like LLaMA 3, Mixtral, Gemma, and more.

---

## ⚙️ Customization

You can modify:
- Default word count, temperature, and model in [`utils/config.py`](utils/config.py)
- Genre list and storage folder
- Prompt templates in [`utils/story_generator.py`](utils/story_generator.py)

---

## 📂 Folder Structure

```
📁 storychat/
│
├── app.py                  # Streamlit app UI and logic
├── requirements.txt        # Dependencies
├── .env                    # Your Groq API key (not committed)
│
├── utils/
│   ├── config.py           # App configuration and storage
│   └── story_generator.py  # Story generation logic using Groq
│
├── stories/                # Folder where stories are saved as JSON
```

---

## 🤝 Contributing

Contributions and feature ideas are welcome!  
Feel free to open issues or submit pull requests.

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

- [Groq API](https://groq.com/)
- [Streamlit](https://streamlit.io/)
- All the AI storytellers and creative minds out there! 🌟

---

## 📬 Contact

Feel free to connect via [LinkedIn](https://www.linkedin.com/in/mohammed-zakeer/) or open an issue for any queries or feedback.
