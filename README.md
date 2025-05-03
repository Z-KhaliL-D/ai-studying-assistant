# ai-studying-assistant

The **AI Studying Assistant** is an interactive tool built with Streamlit that helps you deeply understand, visualize, and test your knowledge using your own PDF study materials. It combines advanced AI features with user-friendly interaction to provide:

-  Mind Map generation
-  Chat-based learning
-  Automated quizzes

---

## 📁Project Structure & File Overview

### `main_app.py`
This is the **main Streamlit application**. It provides the user interface and manages the following workflows:
- Uploading and processing PDF files
- Displaying a radio menu to select between "Chat", "MindMap", and "Quiz"
- Interacting with external AI models via the Groq API
- Displaying results (chat answers, diagrams, quiz scores) directly in the web app

### `mindmap.py`
A **support module** that handles:
- Creating prompts for the AI model to generate a structured **markdown mind map**
- Parsing that markdown and rendering it into a visual diagram using **Graphviz**

### `requirements.txt`
A list of all required Python packages to run the application, including:
- `streamlit`
- `langchain`
- `huggingface-hub`
- `graphviz`
- `requests`
- and any other dependencies used in the code

---

##  How to Run

1. **Clone the Repository**
   ```bash
   git clone https://your-repo-url
   cd ai-studying-assistant
