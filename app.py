import streamlit as st
import json
from rapidfuzz import fuzz
from openai import OpenAI

# -------------------
# Setup OpenAI
# -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🤖 AI Troubleshooting Assistant")

# Load troubleshooting data
with open("troubleshooting.json", "r") as f:
    troubleshooting_data = json.load(f)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "awaiting_yes_no" not in st.session_state:
    st.session_state.awaiting_yes_no = False

user_input = st.text_input("Describe your issue:")

def get_match_label(score):
    if score >= 80:
        return "Best Match"
    elif score >= 65:
        return "Good Match"
    else:
        return "Possible Match"

if user_input and not st.session_state.awaiting_yes_no:
    # Store user input
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # If no candidates yet, search for matches
    if not st.session_state.candidates:
        matches = []
        for entry in troubleshooting_data:
            score_problem = fuzz.partial_ratio(user_input.lower(), entry["problem"].lower())
            score_try = fuzz.partial_ratio(user_input.lower(), entry["what_to_try_first"].lower())
            score = max(score_problem, score_try)
            if score > 50:
                matches.append((score, entry))
        
        matches.sort(reverse=True, key=lambda x: x[0])
        st.session_state.candidates = matches[:3]
        st.session_state.current_index = 0

        if st.session_state.candidates:
            score, entry = st.session_state.candidates[0]
            match_label = get_match_label(score)
            context = (
                f"System: {entry['system']}\n"
                f"Problem: {entry['problem']}\n"
                f"What to Try First: {entry['what_to_try_first']}\n"
                f"When to Call Support: {entry['when_to_call_support']}\n"
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": f"I found a {match_label}: {entry['problem']}.\n{entry['what_to_try_first']}\n\nDid that help?"}
            )
            st.session_state.chat_history.append({"role": "context", "content": context})
            st.session_state.awaiting_yes_no = True
        else:
            st.session_state.chat_history.append(
                {"role": "assistant", "content": "I couldn’t find anything close in the troubleshooting guide. Please contact support."}
            )

# Render chat history
for chat in st.session_state.chat_history:
    if chat["role"] == "assistant":
        st.markdown(f"**Assistant:** {chat['content']}")
    elif chat["role"] == "user":
        st.markdown(f"**You:** {chat['content']}")

# Show Yes/No buttons if assistant is waiting
if st.session_state.awaiting_yes_no:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, it worked"):
            st.session_state.chat_history.append({"role": "user", "content": "Yes"})
            st.session_state.chat_history.append({"role": "assistant", "content": "Great to hear that solved your problem! 🎉"})
            st.session_state.awaiting_yes_no = False
            st.session_state.candidates = []
            st.session_state.current_index = 0
            st.experimental_rerun()
    with col2:
        if st.button("❌ No, still an issue"):
            st.session_state.chat_history.append({"role": "user", "content": "No"})
            st.session_state.current_index += 1
            if st.session_state.current_index < len(st.session_state.candidates):
                score, entry = st.session_state.candidates[st.session_state.current_index]
                match_label = get_match_label(score)
                context = (
                    f"System: {entry['system']}\n"
                    f"Problem: {entry['problem']}\n"
                    f"What to Try First: {entry['what_to_try_first']}\n"
                    f"When to Call Support: {entry['when_to_call_support']}\n"
                )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": f"Okay, let’s try another suggestion.\nI found a {match_label}: {entry['problem']}.\n{entry['what_to_try_first']}\n\nDid that help?"}
                )
                st.session_state.chat_history.append({"role": "context", "content": context})
            else:
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": "I’ve run out of suggestions from the guide. Please contact support."}
                )
                st.session_state.awaiting_yes_no = False
            st.experimental_rerun()
