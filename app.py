import os
import json
import tempfile
import streamlit as st
import numpy as np
import soundfile as sf
import av
from rapidfuzz import fuzz
from openai import OpenAI
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

# -------------------
# Streamlit Config
# -------------------
st.set_page_config(page_title="STIAB Assistant", layout="wide")

# -------------------
# OpenAI Setup
# -------------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("❌ OpenAI API key is missing. Please check your secrets.toml.")
    st.stop()

# -------------------
# Load Data
# -------------------
def load_json(file_path, default):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"⚠️ Could not load {file_path}: {e}")
        return default

troubleshooting_data = load_json("troubleshooting.json", [])
translations_data = load_json("translations.json", {"English": {"app_title": "STIAB Assistant"}})

# -------------------
# Session State
# -------------------
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

selected_language = st.selectbox(
    "🌍",
    list(translations_data.keys()),
    index=list(translations_data.keys()).index(st.session_state.selected_language),
)
st.session_state.selected_language = selected_language
local_text = translations_data.get(selected_language, translations_data["English"])

# -------------------
# Voice Input
# -------------------
rtc_configuration = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class AudioProcessor:
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        self.frames.append(frame)
        return frame

def capture_and_transcribe():
    st.markdown(local_text.get("speak_issue", "🎤 Speak your issue below:"))
    ctx = webrtc_streamer(
        key="speech",
        mode="sendonly",
        rtc_configuration=rtc_configuration,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_processor and ctx.audio_processor.frames:
        audio_data = np.concatenate(
            [f.to_ndarray().flatten() for f in ctx.audio_processor.frames]
        )
        if audio_data.size > 0:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                sf.write(tmpfile.name, audio_data, ctx.audio_processor.frames[0].sample_rate)
                st.audio(tmpfile.name)

                try:
                    with open(tmpfile.name, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                        )
                        st.success(f"🎤 {local_text.get('transcribed', 'Transcribed')}: {transcript.text}")
                        return transcript.text
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")
    return None

# -------------------
# Main App Flow
# -------------------
st.title(local_text.get("app_title", "STIAB Assistant"))

system = st.selectbox(
    local_text.get("select_system", "Select your system"),
    ["KDS", "Kiosk Software", "POS", local_text.get("not_sure", "I’m not sure")]
)

if system:
    st.markdown(local_text.get("describe_issue", "Please describe your issue"))
    text_input = st.text_input(local_text.get("describe_issue_placeholder", "Type here..."))
    voice_input = capture_and_transcribe()

    query = voice_input if voice_input else text_input

    if query:
        st.write(f"🔍 {local_text.get('processing_query', 'Processing your query...')}")

        # Fuzzy matching
        best_match = None
        best_score = 0
        for entry in troubleshooting_data:
            problem_text = entry.get("Problem", "")
            if not problem_text:
                continue
            score = fuzz.partial_ratio(query.lower(), problem_text.lower())
            if score > best_score:
                best_score = score
                best_match = entry

        if best_match:
            if best_score >= 80:
                match_quality = local_text.get("best_match", "✅ Best Match")
            elif best_score >= 60:
                match_quality = local_text.get("good_match", "👍 Good Match")
            else:
                match_quality = local_text.get("possible_match", "🤔 Possible Match")

            st.subheader(f"{match_quality}: {best_match['Problem']}")
            st.write(f"**{local_text.get('what_to_try', 'What to Try First')}**: {best_match.get('What to Try First', 'N/A')}")
            st.write(f"**{local_text.get('when_to_call', 'When to Call Support')}**: {best_match.get('When to Call Support', 'N/A')}")
        else:
            st.warning(local_text.get("no_results", "No results found"))
