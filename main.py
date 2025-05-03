import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import requests
import graphviz

import mindmap


API_URL = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}


st.title("📚 AI Studying Assistant ☕")


uploaded_file = st.file_uploader("Upload your PDF file and let's unlock your FULL potential for success!", type="pdf")
pdf_loaded = False  

if uploaded_file is not None:
    st.write("File uploaded successfully!")
    pdf_path = "uploaded_file.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("Processing PDF..."):
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = splitter.split_documents(pages)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents, embeddings)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    
    st.write("PDF loaded and processed successfully!")
    pdf_loaded = True

choice = st.radio(
    "How would you like to study?",
    ["Chat with my materials", "Get a MindMap 🧠", "Test my knowledge with a Quiz"]
)

if choice:
    st.success(f"You selected: {choice}")

if choice == "Chat with my materials":
    if not pdf_loaded:
        st.error("Please upload a PDF file first to chat with your materials!")
    else:
        def query_huggingface(prompt, context):
            full_prompt = f"""
            Directly answer based on the context , it's a pdf uploaded to you to help me with.
            Give simple,explanatory ,concise, correct and relevant answer.
            If you can't answer, use your own Knowledge.
            Context: {context}
            Question: {prompt}
            """
            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 0.9
            }
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code != 200:
                st.error(f"Inference API error {response.status_code}: {response.text}")
                return "Error"
            data = response.json()
            if isinstance(data, list) and data:
                return data[0].get("generated_text", "No generated_text in response")
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            if isinstance(data, dict):
                try:
                    return data["choices"][0]["message"]["content"]
                except (KeyError, IndexError):
                    pass
            st.error(f"Unexpected response format: {data}")
            return "Error"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            st.chat_message("user").write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            relevant_docs = retriever.get_relevant_documents(user_input)
            context = "\n\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
            
            with st.spinner("Working on it..."):
                response = query_huggingface(user_input, context)
            
            st.chat_message("assistant").write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
if choice == "Get a MindMap 🧠":
    if not pdf_loaded:
        st.error("Please upload a PDF file first to get a mind map!")
    else:
        combined_text = "\n\n".join([doc.page_content for doc in documents])
        parse_description = ""
        mindmap_result = mindmap.get_mindmap(combined_text, parse_description)

        if mindmap_result:
            try:
                st.code(mindmap_result, language="markdown")
                st.markdown("### Visual Diagram")
                img_path = mindmap.render_img(mindmap_result) 
                if img_path:
                    st.image(img_path, caption="Mindmap Diagram", use_container_width=True)
                else:
                    st.error("Failed to load diagram.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Failed to generate mind map from the provided text.")
if choice == "Test my knowledge with a Quiz":
    if not pdf_loaded:
        st.error("Please upload a PDF file first to take a quiz!")
    else:
        st.markdown("###Quiz Setup")
        num_questions = st.selectbox("How many questions?", [3, 5, 10], index=1)
        difficulty = st.selectbox("Choose difficulty level:", ["Medium", "Hard"], index=0)

        if st.button("Generate Quiz"):
            full_text = "\n\n".join([doc.page_content for doc in documents])
            quiz_prompt = f"""
            Create {num_questions} multiple-choice questions based on the following content.
            Difficulty: {difficulty}.

            For each question, include:
            - The question
            - Four answer options labeled A–D
            - At the end of each question block, write "**Correct answer: [LETTER]**" on a new line.

            Content:
            {full_text}
            """

            with st.spinner("Generating quiz..."):
                payload = {
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [{"role": "user", "content": quiz_prompt}],
                    "temperature": 0.5,
                    "max_tokens": 2000,
                }
                response = requests.post(API_URL, headers=headers, json=payload)
                if response.status_code != 200:
                    st.error("Failed to generate quiz")
                    st.stop()

                quiz_text = response.json()["choices"][0]["message"]["content"]
                st.session_state.quiz_text = quiz_text 
                st.session_state.quiz_ready = True   

if st.session_state.get("quiz_ready"):
    import re

    quiz_text = st.session_state.get("quiz_text", "")
    question_blocks = re.findall(r'\*\*Question\s*\d+\*\*(.*?)\*\*Correct answer:\s*([A-D])\*\*', quiz_text, re.DOTALL)

    if not question_blocks:
        st.error("Couldn't parse the quiz. Please try generating it again.")
    else:
        st.markdown("### 📝 Quiz: Select one answer per question")

        with st.form("quiz_form"):
            user_answers = {}
            for i, (question_text, _) in enumerate(question_blocks):
                q_lines = question_text.strip().splitlines()
                question = q_lines[0].strip()
                options = [line.strip() for line in q_lines[1:] if line.strip().startswith(tuple("ABCD"))]

                st.write(f"**Q{i+1}: {question}**")
                user_answers[i] = st.radio(
                    label="",
                    options=[opt[0] for opt in options],
                    format_func=lambda x: f"{x}) {dict((opt[0], opt[2:].strip()) for opt in options).get(x)}",
                    key=f"q{i}"
                )

            submitted = st.form_submit_button("Submit Answers")

        if submitted:
            st.markdown("### Results")
            correct = 0
            for i, (_, correct_answer) in enumerate(question_blocks):
                user_ans = user_answers[i]
                correct_letter = correct_answer.strip().upper()
                result = "✅ Correct" if user_ans == correct_letter else f"❌ Wrong — Correct: {correct_letter}"
                st.write(f"Q{i+1}: You answered **{user_ans}**, {result}")
                if user_ans == correct_letter:
                    correct += 1
            st.success(f"You got {correct} out of {len(question_blocks)} correct.") 
