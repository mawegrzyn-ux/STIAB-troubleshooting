import streamlit as st
import json
from rapidfuzz import fuzz
from openai import OpenAI

# -------------------
# Setup
# -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="AI Troubleshooting Assistant", layout="centered")

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# Languages with flags
languages = {
    "🇬🇧": "English",
    "🇫🇷": "French",
    "🇳🇱": "Dutch",
    "🇪🇸": "Spanish",
    "🇮🇹": "Italian",
    "🇩🇪": "German"
}

# Load translations
with open("translations.json", "r") as f:
    translations_data = json.load(f)

# Default language
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

# Render flag bar with HTML
flags_html = '<div class="flag-bar">'
for flag, lang in languages.items():
    flags_html += f"""
    <a href="/?lang={lang}" style="text-decoration:none;">
        <button class="flag-btn">{flag}</button>
    </a>
    """
flags_html += "</div>"

st.markdown(flags_html, unsafe_allow_html=True)

# Capture language from query params
params = st.query_params
if "lang" in params:
    st.session_state.selected_language = params["lang"]

selected_language = st.session_state.selected_language
ui_local = translations_data[selected_language]["ui"]
local_text = translations_data[selected_language]["buttons"]

# App title
st.title("🤖 AI Troubleshooting Assistant")

# Load troubleshooting data
with open("troubleshooting.json", "r") as f:
    troubleshooting_data = json.load(f)

# Init session state
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

# Step 1: System choice
system_choice = st.selectbox(
    ui_local["system_label"],
    ["-- Select a system --", "KDS", "Kiosk Software", "POS", "I'm not sure"]
)
if system_choice != "-- Select a system --":
    st.session_state.system_choice = system_choice

def get_match_label(score):
    if score >= 80:
        return "Best Match"
    elif score >= 65:
        return "Good Match"
    else:
        return "Possible Match"

# Step 2: Issue input
if st.session_state.system_choice:
    user_input = st.text_input(ui_local["issue_placeholder"])

    if user_input and not st.session_state.selected_problem:
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
            if st.session_state.system_choice == "I'm not sure" or entry["system"] == st.session_state.system_choice:
                score_problem = fuzz.partial_ratio(translated_input.lower(), entry["problem"].lower())
                score_try = fuzz.partial_ratio(translated_input.lower(), entry["what_to_try_first"].lower())
                score = max(score_problem, score_try)
                if score > 50:
                    matches.append((score, entry))

        matches.sort(reverse=True, key=lambda x: x[0])
        st.session_state.candidates = matches[:5]

        if st.session_state.candidates:
            if st.session_state.system_choice == "I'm not sure":
                problem_choices = [f"{m[1]['system']} - {m[1]['problem']}" for m in st.session_state.candidates]
            else:
                problem_choices = [m[1]["problem"] for m in st.session_state.candidates]

            selected_problem = st.selectbox(ui_local["suggestions_label"], ["-- Select a problem --"] + problem_choices)

            if selected_problem != "-- Select a problem --":
                if st.session_state.system_choice == "I'm not sure":
                    problem_text = selected_problem.split(" - ", 1)[1]
                else:
                    problem_text = selected_problem

                st.session_state.selected_problem = problem_text
                st.rerun()
        else:
            st.warning(ui_local["no_results"])

# Step 3: Show GPT answer
if st.session_state.selected_problem:
    chosen_entry = next(entry for score, entry in st.session_state.candidates if entry["problem"] == st.session_state.selected_problem)
    score = next(score for score, entry in st.session_state.candidates if entry["problem"] == st.session_state.selected_problem)
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

    st.subheader(f"{match_label}: {chosen_entry['problem']} ({chosen_entry['system']})")
    st.write(answer)

    st.session_state.awaiting_yes_no = True

# Step 4: Yes/No buttons
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
