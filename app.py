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
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("styles.css")

# Supported languages
languages = ["English", "French", "Dutch", "Spanish", "Italian", "German"]

# Load translations
with open("translations.json", "r") as f:
    translations_data = json.load(f)

# Default language
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

# Language selector row with 🌐
lang_container = st.container()
with lang_container:
    cols = st.columns([0.1, 0.9])
    cols[0].markdown("🌐")
    selected_lang = cols[1].selectbox("", languages, index=languages.index(st.session_state.selected_language))
    st.session_state.selected_language = selected_lang

selected_language = st.session_state.selected_language
ui_local = translations_data[selected_language]["ui"]
local_text = translations_data[selected_language]["buttons"]

# App title
st.title(ui_local["title"])

# Load troubleshooting data
with open("troubleshooting.json", "r") as f:
    troubleshooting_data = json.load(f)

# Load problem translations cache
cache_file = "problem_translations.json"
if os.path.exists(cache_file):
    with open(cache_file, "r") as f:
        problem_translations = json.load(f)
else:
    problem_translations = {}

def translate_problem(problem_text, lang):
    # Return cached if available
    if problem_text in problem_translations and lang in problem_translations[problem_text]:
        return problem_translations[problem_text][lang]

    # Otherwise translate using GPT
    translation = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate the following problem into {lang}. Return only the translated text."},
            {"role": "user", "content": problem_text}
        ],
        max_tokens=100
    )
    translated_problem = translation.choices[0].message.content.strip()

    # Save to cache
    if problem_text not in problem_translations:
        problem_translations[problem_text] = {}
    problem_translations[problem_text][lang] = translated_problem

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(problem_translations, f, indent=2, ensure_ascii=False)

    return translated_problem

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
            if st.session_state.system_choice == "I'm not sure" or entry["system"] == st.session_state.system_choice:
                score_problem = fuzz.partial_ratio(translated_input.lower(), entry["problem"].lower())
                score_try = fuzz.partial_ratio(translated_input.lower(), entry["what_to_try_first"].lower())
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
                if st.session_state.system_choice == "I'm not sure":
                    # Extract back the original English problem
                    chosen_idx = translated_choices.index(selected_problem)
                    chosen_entry = st.session_state.candidates[chosen_idx][1]
                else:
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

# Step 3: Yes/No buttons
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
