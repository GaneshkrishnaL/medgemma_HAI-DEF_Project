import tempfile
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
from datetime import datetime

from app.models.medgemma import MedGemmaClient
from app.models.medasr import MedASRClient
from app.core.orchestrator import Orchestrator
from app.db.store import (
    init_db, create_user, verify_user, create_session, 
    get_user_sessions, add_message, get_session_messages,
    add_vital, get_vitals_history
)
from app.core.vitals_analyzer import analyze_vitals

st.set_page_config(page_title="MedGemma-Copilot Pro", layout="wide", page_icon="🩺")

# -- CSS for Premium Feel --
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ff4b4b;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #a3a8b4;
        margin-bottom: 2rem;
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-bubble {
        background-color: #1e3a8a;
        color: white;
    }
    .bot-bubble {
        background-color: #1f2937;
        border-left: 4px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    medgemma = MedGemmaClient()
    medasr = MedASRClient()
    return Orchestrator(medgemma, medasr)

def login_screen():
    st.markdown("<div class='main-header'>🩺 MedGemma Copilot Pro</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login", type="primary"):
            if verify_user(u, p):
                st.session_state["user"] = u
                st.rerun()
            else:
                st.error("Invalid credentials")
                
    with tab2:
        u = st.text_input("Username", key="reg_u")
        p = st.text_input("Password", type="password", key="reg_p")
        if st.button("Register"):
            if create_user(u, p):
                st.success("User created! Please login.")
            else:
                st.error("Username already taken")

def main_app():
    orch = load_models()
    user = st.session_state["user"]
    
    with st.sidebar:
        st.title(f"Hi, {user} 👋")
        if st.button("Logout"):
            del st.session_state["user"]
            st.rerun()
        
        st.divider()
        menu = st.radio("Navigation", ["Chat & Analysis", "BP & Sugar Tracking", "Visit History"])

    if menu == "Chat & Analysis":
        render_chat_page(orch, user)
    elif menu == "BP & Sugar Tracking":
        render_vitals_page(user)
    elif menu == "Visit History":
        render_history_page(user)

def render_chat_page(orch, user):
    st.markdown("### 🤖 Medical Chat & Scan Analysis")
    
    # Session handling
    if "current_session" not in st.session_state:
        st.session_state["current_session"] = None

    col_sessions, col_chat = st.columns([1, 3])
    
    with col_sessions:
        if st.button("+ New Interview", use_container_width=True):
            st.session_state["current_session"] = None
        
        sessions = get_user_sessions(user)
        for sid, title in sessions:
            if st.button(f"📄 {title[:20]}...", key=sid):
                st.session_state["current_session"] = sid

    with col_chat:
        curr_sid = st.session_state["current_session"]
        
        # Display history
        if curr_sid:
            messages = get_session_messages(curr_sid)
            for role, content, img in messages:
                div_class = "user-bubble" if role == "user" else "bot-bubble"
                st.markdown(f"<div class='chat-bubble {div_class}'><b>{role.title()}:</b><br>{content}</div>", unsafe_allow_html=True)
        else:
            st.info("Start a new session or select one from the left to begin.")

        # Input Section
        with st.expander("Inputs (Report / Scans / Voice)", expanded=not curr_sid):
            up_img = st.file_uploader("Upload X-ray / Scan", type=["png", "jpg", "jpeg"])
            img = Image.open(up_img).convert("RGB") if up_img else None
            pasted = st.text_area("Paste report text", height=100)
            
            st.write("---")
            audio_data = st.audio_input("Record voice question")
            
        user_q = st.text_input("Type your question...", placeholder="e.g. Explain my X-ray results")
        
        if audio_data:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_data.read())
                tmp_path = tmp.name
            with st.spinner("Transcribing voice..."):
                v_q = orch.transcribe_if_audio(tmp_path)
                if v_q: user_q = v_q

        if st.button("Send", type="primary"):
            if not user_q:
                st.warning("Please provide a question or voice input.")
            else:
                if not curr_sid:
                    curr_sid = create_session(user, user_q[:30])
                    st.session_state["current_session"] = curr_sid
                
                add_message(curr_sid, "user", user_q)
                
                with st.spinner("Analyzing with MedGemma..."):
                    ans = orch.chat(user_id=user, user_question=user_q, pasted_text=pasted, image=img)
                    add_message(curr_sid, "assistant", ans)
                st.rerun()

def render_vitals_page(user):
    st.markdown("### 📊 Health Tracking (Blood Pressure & Sugar)")
    
    col_input, col_viz = st.columns([1, 2])
    
    with col_input:
        v_type = st.selectbox("Record Type", ["Blood Pressure", "Sugar Level"])
        if v_type == "Blood Pressure":
            sys = st.number_input("Systolic (top #)", value=120)
            dia = st.number_input("Diastolic (bottom #)", value=80)
            note = st.text_input("Notes (e.g. after lunch)")
            if st.button("Save BP"):
                add_vital(user, "blood_pressure", sys, dia, note)
                st.success("Blood pressure recorded!")
        else:
            glu = st.number_input("Glucose level (mg/dL)", value=100)
            note = st.text_input("Notes (e.g. fasting)")
            if st.button("Save Sugar"):
                add_vital(user, "sugar", glu, None, note)
                st.success("Sugar level recorded!")

    with col_viz:
        st.markdown("#### Trends & Analysis")
        data_bp = get_vitals_history(user, "blood_pressure")
        data_sugar = get_vitals_history(user, "sugar")
        
        tab_bp, tab_sugar = st.tabs(["BP History", "Sugar History"])
        
        with tab_bp:
            if data_bp:
                df_bp = pd.DataFrame(data_bp, columns=["Systolic", "Diastolic", "Notes", "Timestamp"])
                df_bp['Date'] = pd.to_datetime(df_bp['Timestamp'], unit='s')
                fig = px.line(df_bp, x="Date", y=["Systolic", "Diastolic"], title="Blood Pressure Trends")
                st.plotly_chart(fig, use_container_width=True)
                st.info(analyze_vitals(data_bp, "blood_pressure"))
            else:
                st.write("No BP data yet.")
                
        with tab_sugar:
            if data_sugar:
                df_s = pd.DataFrame(data_sugar, columns=["Glucose", "Extra", "Notes", "Timestamp"])
                df_s['Date'] = pd.to_datetime(df_s['Timestamp'], unit='s')
                fig = px.line(df_s, x="Date", y="Glucose", title="Blood Sugar Trends")
                st.plotly_chart(fig, use_container_width=True)
                st.info(analyze_vitals(data_sugar, "sugar"))
            else:
                st.write("No Sugar data yet.")

def render_history_page(user):
    st.markdown("### 📁 Full Interaction Archive")
    sessions = get_user_sessions(user)
    if not sessions:
        st.write("No history found.")
        return
        
    for sid, title in sessions:
        with st.expander(f"{title} ({sid.split('_')[-1]})"):
            msgs = get_session_messages(sid)
            for role, content, _ in msgs:
                st.markdown(f"**{role.upper()}**: {content}")

def main():
    init_db()
    if "user" not in st.session_state:
        login_screen()
    else:
        main_app()

if __name__ == "__main__":
    main()
