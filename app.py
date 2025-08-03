import streamlit as st
import json
import os
from rapidfuzz import fuzz
from openai import OpenAI

# -------------------
# Setup
# -------------------
st.set_page_config(page_title="STIAB Assistant", layout="centered")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

translations_data = load_json_safe("translations.json", {})
troubleshooting_data = load_json_safe("troubleshooting.json", [])

# -------------------
# Session State Defaults
# -------------------
defaults = {
    "selected_language": "English",
    "system_choice": None,
    "candidates": [],
    "current_index": 0,
    "selected_problem": None,
    "awaiting_yes_no": False,
    "show_lang_popup": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

selected_language = st.session_state.selected_language
ui_local = translations_data.get(selected_language, {}).get("ui", translations_data["English"]["ui"])
local_text = translations_data.get(selected_language, {}).get("buttons", translations_data["English"]["buttons"])

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
    st.session_state.system_choice = (
        "I'm not sure" if system_choice == ui_local.get("not_sure", "I'm not sure") else system_choice
    )

# -------------------
# Step 2: Issue Input + Spinner Placement
# -------------------
user_input = None
if st.session_state.system_choice:
    st.write(ui_local.get("issue_placeholder", "Describe your issue"))
    user_input = st.text_input("💬 " + ui_local.get("text_input", "Type your issue here"))

    # Spinner placeholder BELOW input
    spinner_placeholder = st.empty()

    if user_input:
        with spinner_placeholder, st.spinner(ui_local.get("loading", "Thinking...")):
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
                    translated_choices.append(entry["problem"])  # simplified for clarity

                selected_problem = st.selectbox(
                    ui_local.get("suggestions_label", "Possible issues"),
                    ["-- Select a problem --"] + translated_choices,
                    key="problem_selector",
                )

                if selected_problem != "-- Select a problem --":
                    chosen_idx = translated_choices.index(selected_problem)
                    chosen_entry = st.session_state.candidates[chosen_idx][1]

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"You are a helpful IT troubleshooting assistant. Respond only in {selected_language}."},
                            {"role": "user", "content": f"My issue: {user_input}"},
                            {"role": "assistant", "content": f"Troubleshooting entry:\n{chosen_entry}"}
                        ],
                        max_tokens=300
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)

                    st.session_state.awaiting_yes_no = True
            else:
                st.warning(ui_local.get("no_results", "No matching problems found."))
