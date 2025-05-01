import streamlit as st
from streamlit_oauth import OAuth2Component
from my_search import search_and_respond
from db import (
    init_db,
    get_user_by_email,
    create_user,
    get_prompt_count,
    increment_prompt_count,
    is_user_subscribed,
    update_subscription,
    get_chat_history,
    save_chat
)
import string
from collections import Counter
import os
import requests
import base64
import sqlite3
import hashlib
import datetime
from datetime import datetime 
from typing import Optional, Dict, List, Tuple  # Add this 


# Initialize DB
init_db()

# def truncate_text(text, word_limit=100):
#     words = text.split()
#     return " ".join(words[:word_limit]) + "..." if len(words) > word_limit else text

def summarize_text(answer,num_sentences=4):
                        answer = answer.translate(str.maketrans('', '', string.punctuation))
                        sentences = answer.split('.')
                        sentences = [s.strip() for s in sentences if s]  # Remove empty sentences
                        # 2. Calculate word frequencies
                        words = [word.lower() for sentence in sentences for word in sentence.split()]
                        word_frequency = Counter(words)
                        sentence_scores = {}
                        for i, sentence in enumerate(sentences):
                            for word in sentence.lower().split():
                                if word in word_frequency:
                                    if i not in sentence_scores:
                                        sentence_scores[i] = word_frequency[word]
                                    else:
                                        sentence_scores[i] += word_frequency[word]
                    
                        # 4. Get the top N sentences
                        top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
                        summary_sentences = [sentences[i] for i in top_sentences]
                        summary = '. '.join(summary_sentences)
                        return summary


global a_short

# PayU merchant details
MERCHANT_KEY = "V6alJT"
MERCHANT_SALT = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDULOIP8oYe4bnIFX8xdsCxzq6UopwZMNVOKLs8IaMXA1lacMJmaXjgDYPZPfVEHAW18Gk5zNObycolZlBd2JlaNmn5sYQmfFWND0MO24Qp8sgZWU1yERUAJgCII8l9sVDD8H31axa35L7v1VSMAzTsI2gNEteBlCcPz+PFWEu8wMrEFMndGHCS2P7/yPBJnoZbzmU4nfZcYrNEQSndiJTs4F4Utd9dH3F8dO9PzrcDUjB0xdf58uBeRF7Ml/L73lKgf1vsy1YBlcMnN7oR5NvmfAGCxgvBNPh7QAsBSNnJ12rtMSMY7bS8AIh+lr8RFnGngJQcCbD3EvcbB5GF9n1LAgMBAAECggEAONcxVJ5fKeTE1YJUydaLdtbs1Crf8KuxaTfmOQy12VNvW5g7rB3zYOqd+NPtYeqz6PLX7cEeq2yat/w56Xo+Uvmi2F6jDYBfluOQzmkmdepxisDuy3EiFCEaIV6c+wxGm8dQpy+iLW+dazjWZo/xXJV7qYzzqOYctNK3rUWjPJRYcFvNnljMudXw5PlNEtDgVslbwi3l8Lq7Jm5LAKMyD7jnrnWHFNfLcguKRuhTC3jtXOHHPQnLLue3pORYcvbsD6t/jPAtrsBKKxxJncwcRvS1+F2PeBiMav1ZXK0W2xlKrBU3ykWotDSb6eS9540L6aWBdWCpIN7RUzV3ydpZOQKBgQD15bINTf5GbEy4QcYNanVEyaEDZRpmfa39XipXR2dHPH5nKsY4yJty1c+Jt75d2t8p9bureIscTyWPKYL+0kiGqIIZIYiXEK5iGUZICOAXC4ic+ZXtmzKV7+bGD8czik9WEq69ncqAUnuMe6P8bFGhDpHknhMEV9XP5VrQk4swlQKBgQDc5IGXKAXABS09pRbgTcJmIXSS1whwB8GlTZu8xi+6gj+mOzy36WEZFrslqf1kwL/Em21SzE7QfI2EZ4Su//cgBR5iywgIjB6r91m0QuFdcf8PBEnMJkWCPFoQ7qvPZKrcVPLCkvTaEd44CNRY3kNBVAQeQGpEBjJYggY84aYeXwKBgQCMTrNJGi6z2knwfT9YGl2tkWs5d7AXuTDVOKzqPkj1AdSSY3rVncntPYj9aQXLof7if1/FWLPvxE2HIcWoRy6w/2e0lUjOAeuu+AL9SWssWx1pjJR7DqpPmaLRcuFUTGA2mdRxR57rl6T9pPMOLnRpdNnUXEo3mTLcPF+UUgwC/QKBgAGohYCJAGIMp+ZKkv1kGA2EOsfPbXTJ2h5Pkte79SfFSo0I7M/EpMH3dbg2qnxTJh1nvU5d0kmmZbmUvV5C9av73dqIA6tswd4woS/FQMPe0zddpOAveV4c7eAqqoeIDfBRgvELAWORtsVc65svL/oRk2ZWvXV9Rmt7rmhOmVypAoGAPuZowns5Ng3fFEvZlYzKXsurLNY7jmLP24674E/Kg240bziUu2qlsF3v+En/sBfV4Lf7S6GSMvVh+0BKt4l6a+1gIFbV7V4iUsv9JdukhHkD6DuomXXAs63Jym8ZNE4B34/mJXoluO5rPQ3Kc9UguXK4/tCoOTEcdB21mgw33Ew="


CLIENT_ID = "5918448459-qvpri389qnp5ekhbv0esoskq8b6b5bnk.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://avipalglobaltech.streamlit.app"
# REDIRECT_URI = "http://localhost:8501/"

AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

FREE_QUERY_LIMIT = 100

# --- Streamlit Config ---
st.set_page_config(
    page_title="ArInE Global",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Hide Streamlit default top menu and footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1dp5vir {padding-top: 1rem;}  /* optional: fix top padding */
    </style>
""", unsafe_allow_html=True)
# HIDE Streamlit's footer and "Manage App" button
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def get_base64_image(image_path: str) -> str:
    """Convert image to base64 for embedding in HTML."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# --- Theme Toggle ---
st.sidebar.title("🖌️ Appearance")
st.sidebar.info("""
**ArInE** (Artificial Intelligence Enabled) is your personal assistant powered by LLMs.
Use it to query documents, learn insights, and streamline your research.
""")

# --- Four Feature Blocks ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 Features")

st.sidebar.success("📄 Semantic Search\nFind insights from uploaded content using vector search.")
st.sidebar.warning("💬 Query Tracking\nTrack free and premium queries per user.")
st.sidebar.info("🧾 Subscription System\nIntegrated with PayU for secure payments.")
st.sidebar.error("🌗 This is another heading which you would like to keep.")


# --- Initialize Session State ---
def init_session_state():
    """Initialize all required session state variables."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "processing_query" not in st.session_state:
        st.session_state.processing_query = False
    if "short_ans" not in st.session_state:
        st.session_state.short_ans = []

init_session_state()



# --- Background Image ---
@st.cache_data
def get_base64_image(image_path: str) -> str:
    """Convert image to base64 for background."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

try:
    base64_image = get_base64_image("logo4.png")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    pass

# --- OAuth Component ---
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint=AUTHORIZE_ENDPOINT,
    token_endpoint=TOKEN_ENDPOINT,
)

# --- Helper Functions ---
def verify_payu_payment(txn_id: str) -> bool:
    """Verify PayU payment status."""
    hash_str = f"{MERCHANT_KEY}|verify_payment|{txn_id}|{MERCHANT_SALT}"
    hashh = hashlib.sha512(hash_str.encode()).hexdigest().lower()

    payload = {
        "key": MERCHANT_KEY,
        "command": "verify_payment",
        "var1": txn_id,
        "hash": hashh
    }

    try:
        response = requests.post(
            "https://info.payu.in/merchant/postservice?form=2",
            data=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("status") == "1"
    except Exception as e:
        st.error(f"Payment verification failed: {str(e)}")
        return False

# def fetch_user_info(access_token: str) -> Optional[dict]:
#     """Fetch user info from Google API."""
#     try:
#         response = requests.get(
#             USER_INFO_URL,
#             headers={"Authorization": f"Bearer {access_token}"},
#             timeout=10
#         )
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         st.error(f"Failed to fetch user info: {str(e)}")
#         return None

def fetch_user_info(access_token):
    import requests
    resp = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                        params={"access_token": access_token})
    return resp.json() if resp.ok else None

# --- Main App Logic ---
def main():
    st.title("📚🔍 ArInE")

    # --- Google OAuth Flow ---
    if not st.session_state.token:
        st.markdown("<h1 style='text-align:center;'>🔐 Welcome to ArInE</h1>", unsafe_allow_html=True)
        token = oauth2.authorize_button(
            name="Continue with Google",
            redirect_uri=REDIRECT_URI,
            scope="profile email",
            extras_params={"prompt":"select_account consent"}
        )
        if token:
            st.session_state.token = token
            st.rerun()
        return

    # --- Post-Login Flow ---
    token = st.session_state.token.get("token") if st.session_state.token else None
    access_token = token.get("access_token") if token else None

    if not access_token:
        st.error("Invalid access token. Please log in again.")
        return

    user_info = fetch_user_info(access_token)
    if not user_info:
        return

    email = user_info.get("email")
    name = user_info.get("name")
    if not email or not name:
        st.error("Failed to retrieve user email/name.")
        return

    col1,col2=st.columns([8,2])
    with col1:
        # Replace all display outputs with:
        st.markdown(f"<div style='color:black;'>Welcome! {name}</div>", 
            unsafe_allow_html=True)
        # st.markdown(f"Welcome! , **{name}**")
    with col2:
        if st.button("🚪Sign Out"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    #----------Initialize User in DB-------------
    if not get_user_by_email(email):
        create_user(email,name)
    st.session_state.query_count = get_prompt_count(email)

    # --- Payment Verification ---
    if "transaction_id" in st.query_params:
        txn_id = st.query_params["transaction_id"]
        if verify_payu_payment(txn_id):
            update_subscription(email, True)
            st.success("🎉 Payment verified! You are now a premium subscriber.")
        else:
            st.warning("⚠️ Payment verification failed.")

    # --- Subscription Status ---
    subscribed = is_user_subscribed(email)
    if subscribed:
        st.success("✅ Premium User: Unlimited queries.")
    else:
        st.info(f"🎓 Free Tier: {st.session_state.query_count}/{FREE_QUERY_LIMIT} queries used.")

    # --- Query Input ---
    query = st.chat_input("Ask a question...")
    a_short = ""  # Initialize a_short here!
    if query and (subscribed or st.session_state.query_count < FREE_QUERY_LIMIT):
        with st.spinner("Searching for answers..."):
            try:
                # context = query_faiss(query)
                # answer = gemini_answer(f"Based on this context:\n{context}\n\nAnswer this question:\n{query
                answer = search_and_respond(query)
        
                # Black colored display with truncation
                st.markdown(f"<div style='color:black;'><strong>Q:</strong> {query}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:black;'><strong>A:</strong> {answer}</div>", unsafe_allow_html=True)
                # Save to history (also in black)
                st.session_state.chat_history.append((query, answer))
                # # Optional: Add "Show Full Answer" button
                # if 'show_full_answer' not in st.session_state:
                #     st.session_state.show_full_answer = False
                
                # if not st.session_state.show_full_answer and len(answer.split()) > 100:
                #     if st.button("🔍 Show Full Answer"):
                #         st.session_state.show_full_answer = True
                
                # if st.session_state.show_full_answer:
                #     st.markdown(f"<p style='color:black;'><strong>Full A:</strong> {answer}</p>", unsafe_allow_html=True)
                                

                if not subscribed:
                    increment_prompt_count(email)
                    st.session_state.query_count += 1

                st.success("✅ Answer generated!")

                # if st.button("📝 Elaborate Answer"):
                #     elaborated = gemini_answer(f"Elaborate this: {answer}")
                #     st.markdown(f"<div style='color:black;'>🧠 {elaborated}</div>", unsafe_allow_html=True)
                
        
            except Exception as e:
                st.error(f"Failed to process query: {str(e)}")

    elif query:
            st.error("🛑 Free limit reached. Please subscribe to continue.")
            st.link_button("🔗 Subscribe Now", "https://pmny.in/YrI6O1HHr1Na")
    # Show past interactions
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = get_user_chat_history(email)
    with  st.expander("✂️ Summarize Answer"):
            st.markdown(f"<p style='color:black;'>📌 {a_short}</p>", unsafe_allow_html=True)
    if st.session_state.chat_history:
        with st.expander("💬 Chat History"):
            for q, a in st.session_state.chat_history[-10:]:
                st.markdown(f"<div style='color:black;'><strong>Q:</strong> {q}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:black;'><strong>A:</strong> {a}</div>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)



if __name__ == "__main__":
    main()
