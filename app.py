import streamlit as st
import json
import os
import tempfile
from rapidfuzz import fuzz
from openai import OpenAI
from streamlit_webrtc import webrtc_streamer

# -------------------
# Setup
# -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="STIAB Assistant", layout="centered")

# -------------------
# Load Custom CSS
# -------------------
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# -------------------
# JSON Loader
# -------------------
def load_json_safe(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            st.warning(f"⚠️ {file_path} is invalid JSON.")
    return default_data

languages = ["English", "French", "Dutch", "Spanish", "Italian", "German"]

translations_data = load_json_safe("translations.json", {})
troubleshooting_data = load_json_safe("troubleshooting.json", [])
if "problem_translations" not in st.session_state:
    st.session_state.problem_translations = load_json_safe("problem_translations.json", {})

# -------------------
# Helpers
# -------------------
def translate_problem(problem_text, lang):
    translations = st.session_state.problem_translations
    if problem_text in translations and lang in translations[problem_text]:
        return translations[problem_text][lang]
    translation = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate the following problem into {lang}. Return only the translated text."},
            {"role": "user", "content": problem_text}
        ],
        max_tokens=100
    )
    translated_problem = translation.choices[0].message.content.strip()
    if problem_text not in translations:
        translations[problem_text] = {}
    translations[problem_text][lang] = translated_problem
    st.session_state.problem_translations = translations
    return translated_problem

def get_match_label(score):
    if score >= 80:
        return "Best Match"
    elif score >= 65:
        return "Good Match"
    else:
        return "Possible Match"

# -------------------
# Session State
# -------------------
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"
if "system_choice" not in st.session_state:
    st.session_state.system_choice = None
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "selected_problem" not in st.session_state:
    st.session_state.selected_problem = None
if "awaiting_yes_no" not in st.session_state:
    st.session_state.awaiting_yes_no = False
if "show_lang_popup" not in st.session_state:
    st.session_state.show_lang_popup = False

selected_language = st.session_state.selected_language

# Safely load UI and buttons, fallback to English
ui_local = translations_data.get(selected_language, translations_data.get("English", {})).get(
    "ui", translations_data.get("English", {}).get("ui", {})
)
local_text = translations_data.get(selected_language, translations_data.get("English", {})).get(
    "buttons", translations_data.get("English", {}).get("buttons", {})
)

# -------------------
# Language toggle
# -------------------
if st.button("🌐", key="lang_btn"):
    st.session_state.show_lang_popup = not st.session_state.show_lang_popup

if st.session_state.show_lang_popup:
    flags = {
        "English": "🇬🇧",
        "French": "🇫🇷",
        "Dutch": "🇳🇱",
        "Spanish": "🇪🇸",
        "Italian": "🇮🇹",
        "German": "🇩🇪"
    }
    selected_popup_lang = st.radio(
        "Choose your language",
        options=list(flags.keys()),
        format_func=lambda lang: f"{flags[lang]} {lang}",
        index=list(flags.keys()).index(st.session_state.selected_language)
    )
    if st.button("Confirm"):
        st.session_state.selected_language = selected_popup_lang
        st.session_state.show_lang_popup = False

        # Reset UI state after language change
        st.session_state.system_choice = None
        st.session_state.candidates = []
        st.session_state.current_index = 0
        st.session_state.selected_problem = None
        st.session_state.awaiting_yes_no = False

        st.rerun()

# -------------------
# App Title
# -------------------
st.title(ui_local.get("title", "STIAB Assistant"))

# -------------------
# Step 1: System choice
# -------------------
system_choice = st.selectbox(
    ui_local.get("system_label", "Select a system"),
    [
        "-- Select a system --",
        "KDS",
        "Kiosk Software",
        "POS",
        ui_local.get("not_sure", "I'm not sure"),
    ]
)

if system_choice != "-- Select a system --":
    if system_choice == ui_local.get("not_sure", "I'm not sure"):
        st.session_state.system_choice = "I'm not sure"
    else:
        st.session_state.system_choice = system_choice

# -------------------
# Step 2: Issue Input (Typing or Voice)
# -------------------
if st.session_state.system_choice:
    st.write(ui_local.get("issue_placeholder", "Describe your issue"))

    # Option 1: Manual text input
    user_input = st.text_input("💬 Type your issue here")

    # Option 2: Voice input
    st.markdown("🎤 Or speak your issue below:")

    webrtc_ctx = webrtc_streamer(
        key="speech",
        mode="sendonly",
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
    )

    if webrtc_ctx.audio_receiver:
        audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        if audio_frames:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                audio_frames[0].to_soundfile(tmpfile.name)
                st.audio(tmpfile.name)
                audio_path = tmpfile.name
                with open(audio_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )

                    st.success(f"🎤 Transcribed: {transcript.text}")
                    user_input = transcript.text  # override input with voice text

    # -------------------
    # Run fuzzy search if input is available
    # -------------------
    if user_input:
        translation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate this text from {selected_language} to English."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100
        )
        translated_input = translation.choices[0].message.content

        matches = []
        for entry in troubleshooting_data:
            if st.session_state.system_choice == "I'm not sure" or entry.get("system") == st.session_state.system_choice:
                score_problem = fuzz.partial_ratio(translated_input.lower(), entry.get("problem", "").lower())
                score_try = fuzz.partial_ratio(translated_input.lower(), entry.get("what_to_try_first", "").lower())
                score = max(score_problem, score_try)
                if score > 50:
                    matches.append((score, entry))

        matches.sort(reverse=True, key=lambda x: x[0])
        st.session_state.candidates = matches[:5]

        if st.session_state.candidates:
            translated_choices = []
            for score, entry in st.session_state.candidates:
                translated_problem = translate_problem(entry["problem"], selected_language)
                if st.session_state.system_choice == "I'm not sure":
                    translated_choices.append(f"{entry['system']} - {translated_problem}")
                else:
                    translated_choices.append(translated_problem)

            selected_problem = st.selectbox(
                ui_local.get("suggestions_label", "Possible issues"),
                ["-- Select a problem --"] + translated_choices,
                key="problem_selector"
            )

            if selected_problem != "-- Select a problem --":
                chosen_idx = translated_choices.index(selected_problem)
                chosen_entry = st.session_state.candidates[chosen_idx][1]
                st.session_state.selected_problem = chosen_entry["problem"]

                score = st.session_state.candidates[chosen_idx][0]
                match_label = get_match_label(score)

                context = (
                    f"System: {chosen_entry['system']}\n"
                    f"Problem: {chosen_entry['problem']}\n"
                    f"What to Try First: {chosen_entry['what_to_try_first']}\n"
                    f"When to Call Support: {chosen_entry['when_to_call_support']}\n"
                )

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"You are a helpful IT troubleshooting assistant. Respond only in {selected_language}."},
                        {"role": "user", "content": f"My issue: {user_input}"},
                        {"role": "assistant", "content": f"Troubleshooting entry:\n{context}"}
                    ],
                    max_tokens=300
                )
                answer = response.choices[0].message.content

                st.subheader(f"{match_label}: {translate_problem(chosen_entry['problem'], selected_language)} ({chosen_entry['system']})")
                st.write(answer)

                st.session_state.awaiting_yes_no = True
        else:
            st.warning(ui_local.get("no_results", "No matching problems found."))

# -------------------
# Step 3: Yes/No Buttons
# -------------------
if st.session_state.awaiting_yes_no:
    col1, col2 = st.columns(2)
    with col1:
        if st.button(local_text.get("yes", "Yes")):
            st.success(local_text.get("success", "Glad it worked!"))
            st.session_state.awaiting_yes_no = False
            st.session_state.selected_problem = None
            st.session_state.candidates = []
            st.session_state.current_index = 0
            st.rerun()
    with col2:
        if st.button(local_text.get("no", "No")):
            st.session_state.current_index += 1
            if st.session_state.current_index < len(st.session_state.candidates):
                next_score, next_entry = st.session_state.candidates[st.session_state.current_index]
                st.session_state.selected_problem = next_entry["problem"]
                st.rerun()
            else:
                st.error(local_text.get("error", "Please contact support."))
                st.session_state.awaiting_yes_no = False
                st.session_state.selected_problem = None
                st.session_state.candidates = []
                st.session_state.current_index = 0
