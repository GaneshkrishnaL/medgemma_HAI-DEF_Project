import tempfile
import streamlit as st
from PIL import Image

from app.models.medgemma import MedGemmaClient
from app.models.medasr import MedASRClient
from app.core.orchestrator import Orchestrator
from app.db.store import init_db, get_recent_records

st.set_page_config(page_title="MedGemma-Copilot", layout="wide")

@st.cache_resource
def load_models():
    medgemma = MedGemmaClient()
    medasr = MedASRClient()
    return Orchestrator(medgemma, medasr)

def main():
    init_db()
    orch = load_models()

    st.title("🩺 Custom MedGemma Copilot")

    with st.sidebar:
        st.header("User")
        user_id = st.text_input("User ID", value="ganesh_demo_user")
        st.divider()
        st.subheader("Recent history")
        recents = get_recent_records(user_id, limit=8)
        for r in recents:
            st.caption(r["question"][:80])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Inputs")
        uploaded_image = st.file_uploader("Upload X-ray / scan image (optional)", type=["png", "jpg", "jpeg"])
        image = Image.open(uploaded_image).convert("RGB") if uploaded_image else None
        if image:
            st.image(image, caption="Uploaded image", use_container_width=True)

        pasted_text = st.text_area("Paste report text / doctor notes (optional)", height=220)

        st.markdown("**Live Voice / MicroPhone:**")
        audio_recorded = st.audio_input("Record your question")

        if audio_recorded and ("last_audio" not in st.session_state or st.session_state.get("last_audio") != audio_recorded.name):
            with st.spinner("Transcribing..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_recorded.read())
                    tmp_path = tmp.name
                transcribed = orch.transcribe_if_audio(tmp_path)
                st.session_state["transcribed"] = transcribed
                st.session_state["last_audio"] = audio_recorded.name
                st.rerun()

        if st.session_state.get("transcribed"):
            st.info("Transcription ready — you can edit it below.")
            st.session_state["question"] = st.text_area(
                "Transcribed question (editable)",
                value=st.session_state["transcribed"],
                height=100
            )

    with col2:
        st.subheader("Chat")
        q_default = st.session_state.get("question", "")
        user_question = st.text_area("Your question", value=q_default, height=120, placeholder="e.g., Explain this report in simple terms. What should I ask my doctor?")

        if st.button("Ask MedGemma", type="primary"):
            if not user_question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Thinking..."):
                    answer = orch.chat(
                        user_id=user_id,
                        user_question=user_question,
                        pasted_text=pasted_text,
                        image=image
                    )
                st.markdown(answer)

        st.caption("This tool is for education and visit preparation, not diagnosis.")

if __name__ == "__main__":
    main()
