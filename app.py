import streamlit as st
import google.generativeai as genai
import json

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="GCP ACE Study Partner", layout="centered", page_icon="🚀")

# ADD THIS SNIPPET TO HIDE THE ADDRESS BAR ON IPHONE:
st.markdown(
    """
    <head>
      <meta name="apple-mobile-web-app-capable" content="yes">
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
      <link rel="apple-touch-icon" href="https://your-icon-url.com/icon.png">
    </head>
    """,
    unsafe_allow_html=True
)
# Retrieve API Key from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ API Key not found! Add 'GEMINI_API_KEY' to Streamlit Secrets.")
    st.stop()

# --- 2. SESSION STATE MANAGEMENT ---
if "cards" not in st.session_state:
    st.session_state.cards = []
    st.session_state.current_index = 0
    st.session_state.session_complete = False

# --- 3. CORE FUNCTIONS ---
def generate_cards(topic):
    """Generates flashcards using a fallback model list to avoid 404 errors."""
    # 2026 Priority List: Gemini 3 Flash is fastest, 2.5 is the stable fallback
    model_list = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.0-flash']
    
    success = False
    with st.spinner(f"AI is generating {topic} flashcards..."):
        for model_name in model_list:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = (
                    f"Generate 5 scenario-based flashcards for the GCP Associate Cloud Engineer exam "
                    f"focused on {topic}. Format your response ONLY as a JSON list like this: "
                    "[{\"q\": \"scenario question\", \"a\": \"detailed explanation\"}]"
                )
                response = model.generate_content(prompt)
                
                # Clean the response text for JSON parsing
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                st.session_state.cards = json.loads(raw_json)
                st.session_state.current_index = 0
                st.session_state.session_complete = False
                success = True
                break # Exit loop if model works
            except Exception:
                continue # Try the next model if 404 or error occurs
        
    if not success:
        st.error("Could not connect to any Gemini models. Please check your API key and quota.")

# --- 4. UI LAYOUT ---
st.title("🛡️ GCP ACE: Flashcard Partner")
st.write("Master GCP Associate Cloud Engineer scenarios on the go.")

topic = st.selectbox("Select Study Domain:", 
                    ["IAM & Security", "GKE & Containers", "Networking", "Storage & Databases", "SAP on GCP Admin"])

if st.button("Generate Study Session"):
    generate_cards(topic)

# --- 5. FLASHCARD DISPLAY LOGIC ---
if st.session_state.cards and not st.session_state.session_complete:
    card = st.session_state.cards[st.session_state.current_index]
    
    st.divider()
    st.subheader(f"Card {st.session_state.current_index + 1} of 5")
    
    # Question Area
    st.info(f"**SCENARIO:** \n\n {card['q']}")
    
    # User Input
    user_ans = st.text_area("Your reasoning/answer:", key=f"input_{st.session_state.current_index}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Check Answer"):
            st.success(f"**EXPLANATION:** \n\n {card['a']}")
            
            # AI Feedback on your specific answer
            try:
                model = genai.GenerativeModel('gemini-1.5-flash') # Simplified model for quick feedback
                feedback_prompt = f"Question: {card['q']}\nIdeal Answer: {card['a']}\nUser's Answer: {user_ans}\nRate user answer 1-10 and explain briefly."
                feedback = model.generate_content(feedback_prompt)
                st.write(f"**AI Score:** {feedback.text}")
            except:
                st.write("*(Feedback rating currently unavailable)*")
                
    with col2:
        if st.button("Next Card ➡️"):
            if st.session_state.current_index < 4:
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.session_state.session_complete = True
                st.rerun()

# --- 6. SESSION SUMMARY ---
if st.session_state.session_complete:
    st.balloons()
    st.success("🎉 Session Complete!")
    st.write("Great job! You've reviewed 5 key scenarios. Keep practicing daily to build durable knowledge.")
    if st.button("Start New Topic"):
        st.session_state.cards = []
        st.session_state.session_complete = False
        st.rerun()
