import streamlit as st
import google.generativeai as genai
import json

# App Configuration
st.set_page_config(page_title="GCP ACE Study Partner", layout="centered")
st.title("🚀 GCP ACE Flashcard Partner")

# Sidebar for API Key
with st.sidebar:
    api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    topic = st.selectbox("Choose Topic", ["IAM", "GKE", "Networking", "Storage", "SAP on GCP"])

# Session State for Flashcards
if "cards" not in st.session_state:
    st.session_state.cards = []
    st.session_state.current_index = 0
    st.session_state.score_history = []

# Function to generate cards
def generate_cards():
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Generate 5 difficult GCP Associate Cloud Engineer exam flashcards about {topic}. Output ONLY a JSON list: [{{'q': 'scenario-based question', 'a': 'detailed answer'}}] "
    response = model.generate_content(prompt)
    try:
        # Clean JSON string and load
        content = response.text.replace('```json', '').replace('```', '').strip()
        st.session_state.cards = json.loads(content)
        st.session_state.current_index = 0
    except:
        st.error("Failed to parse AI response. Try again.")

if st.button("Generate New Cards"):
    generate_cards()

# Display Flashcard
if st.session_state.cards:
    card = st.session_state.cards[st.session_state.current_index]
    
    st.subheader(f"Card {st.session_state.current_index + 1} of 5")
    st.info(card['q'])
    
    user_answer = st.text_area("Your Answer:", key=f"ans_{st.session_state.current_index}")
    
    if st.button("Submit & Rate"):
        # AI Rating Logic
        model = genai.GenerativeModel('gemini-1.5-flash')
        rating_prompt = f"Question: {card['q']}\nCorrect Answer: {card['a']}\nUser Answer: {user_answer}\nRate this answer 1-10 and explain briefly."
        rating_res = model.generate_content(rating_prompt)
        
        st.write("---")
        st.success(f"**Correct Answer:** {card['a']}")
        st.write(f"**AI Feedback:** {rating_res.text}")
        
        if st.session_state.current_index < 4:
            if st.button("Next Card"):
                st.session_state.current_index += 1
                st.rerun()
        else:
            st.balloons()
            st.write("🏁 Session Complete! Copy the feedback above for your notes.")
