import streamlit as st
import json
import os
from rapidfuzz import fuzz
from openai import OpenAI

# -------------------
# Setup
# -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="STIAB Assistant", layout="centered")

# Load CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# -------------------
# Safe JSON Loader
# -------------------
def load_json_safe(file_path, default_data):
    """Safely load a JSON file; return default if missing or invalid."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    st.warning(f"⚠️ {file_path} is empty. Using defaults.")
        except json.JSONDecodeError:
            st.warning(f"⚠️ {file_path} is invalid JSON. Using defaults.")
    else:
        st.warning(f"⚠️ {file_path} not found. Using defaults.")
    return default_data

# -------------------
# Load Data
# -------------------
languages = ["English", "French", "Dutch", "Spanish", "Italian", "German"]

translations_data = load_json_safe("translations.json", {
    "English": {
        "ui": {
            "title": "STIAB Assistant",
            "system_label": "Select a system",
            "issue_placeholder": "Describe your issue",
            "suggestions_label": "Possible issues",
            "no_results": "No matching problems found."
        },
        "buttons": {
            "yes": "Yes",
            "no": "No",
            "success": "Glad it worked!",
            "error": "Please contact support."
        }
    }
})

troubleshooting_data = load_json_safe("troubleshooting.json", [])

if "problem_translations" not in st.session_state:
    st.session_state.problem_translations = load_json_safe("problem_translations.json", {})

# -------------------
# Translation with Cache
# -------------------
def translate_problem(problem_text, lang):
    """Translate a problem string into the target language, with caching."""
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

    st.info(f"💾 Cached translation for '{problem_text}' in {lang}.")
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
ui_local = translations_data.get(selected_language, translations_data["English"])["ui"]
local_text = translations_data.get(selected_language, translations_data["English"])["buttons"]

# -------------------
# Sticky World Icon & Popup Modal
# -------------------
st.markdown("""
    <style>
    .lang-button {
        position: fixed;
        top: 10px;
        right: 20px;
        z-index: 9999;
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 50%;
        padding: 8px;
        cursor: pointer;
    }
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .modal-content {
        background: white;
        padding: 20px;
        border-radius: 10px;
        width: 300px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("🌐", key="lang_btn"):
    st.session_state.show_lang_popup = True

if st.session_state.show_lang_popup:
    st.markdown('<div class="modal"><div class="modal-content">', unsafe_allow_html=True)
    st.write("Select your language")

    selected_popup_lang = st.radio(
        "Choose language",
        options=languages,
        index=languages.index(st.session_state.selected_language),
        label_visibility="collapsed"
    )

    if st.button("Confirm"):
        st.session_state.selected_language = selected_popup_lang
        st.session_state.show_lang_popup = False
        st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

# -------------------
# App Title
# -------------------
st.title(ui_local["title"])

# -------------------
# Step 1: System choice
# -------------------
system_choice = st.selectbox(
    ui_local["system_label"],
    ["-- Select a system --", "KDS", "Kiosk Software", "POS", "I'm not sure"]
)
if system_choice != "-- Select a system --":
    st.session_state.system_choice = system_choice

# -------------------
# Step 2: Issue Input
# -------------------
if st.session_state.system_choice:
    user_input = st.text_input(ui_local["issue_placeholder"])

    if user_input:
        # Translate input for matching
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
                ui_local["suggestions_label"],
                ["-- Select a problem --"] + translated_choices,
                key="problem_selector"
            )

            if selected_problem != "-- Select a problem --":
                chosen_idx = translated_choices.index(selected_problem)
                chosen_entry = st.session_state.candidates[chosen_idx][1]
                st.session_state.selected_problem = chosen_entry["problem"]

                # 🚀 Trigger GPT immediately
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
            st.warning(ui_local["no_results"])

# -------------------
# Step 3: Yes/No Buttons
# -------------------
if st.session_state.awaiting_yes_no:
    col1, col2 = st.columns(2)
    with col1:
        if st.button(local_text["yes"]):
            st.success(local_text["success"])
            st.session_state.awaiting_yes_no = False
            st.session_state.selected_problem = None
            st.session_state.candidates = []
            st.session_state.current_index = 0
            st.rerun()
    with col2:
        if st.button(local_text["no"]):
            st.session_state.current_index += 1
            if st.session_state.current_index < len(st.session_state.candidates):
                next_score, next_entry = st.session_state.candidates[st.session_state.current_index]
                st.session_state.selected_problem = next_entry["problem"]
                st.rerun()
            else:
                st.error(local_text["error"])
                st.session_state.awaiting_yes_no = False
                st.session_state.selected_problem = None
                st.session_state.candidates = []
                st.session_state.current_index = 0

# -------------------
# Save Translation Cache to File
# -------------------
if st.session_state.get("problem_translations"):
    try:
        with open("problem_translations.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.problem_translations, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"⚠️ Could not save translation cache: {e}")


