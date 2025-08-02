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

# Initialize session state for chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

user_input = st.text_input("Describe your issue or answer the assistant:")

def get_match_label(score):
    if score >= 80:
        return "Best Match"
    elif score >= 65:
        return "Good Match"
    else:
        return "Possible Match"

if user_input:
    # If no candidates yet, find matches
    if not st.session_state.candidates:
        matches = []
        for entry in troubleshooting_data:
            score_problem = fuzz.partial_ratio(user_input.lower(), entry["problem"].lower())
            score_try = fuzz.partial_ratio(user_input.lower(), entry["what_to_try_first"].lower())
            score = max(score_problem, score_try)
            if score > 50:
                matches.append((score, entry))
        
        matches.sort(reverse=True, key=lambda x: x[0])
        st.session_state.candidates = matches[:3]  # keep top 3
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
                {"role": "assistant", "content": f"I found a {match_label}: {entry['problem']}. {entry['what_to_try_first']} Did that help?"}
            )
            st.session_state.chat_history.append({"role": "context", "content": context})
        else:
            st.session_state.chat_history.append(
                {"role": "assistant", "content": "I couldn’t find anything close in the troubleshooting guide. Please contact support."}
            )
    else:
        # Use existing context and conversation
        context = st.session_state.chat_history[-1]["content"] if st.session_state.chat_history[-1]["role"] == "context" else st.session_state.chat_history[-2]["content"]

        # Continue with GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful IT troubleshooting assistant. Use the troubleshooting entry provided below. If the user says the fix didn’t work, try the next best match from the candidates list. If none work, say: 'Please contact support.'"},
                {"role": "assistant", "content": f"Troubleshooting entry:\n{context}"},
                {"role": "user", "content": user_input}
            ],
            max_tokens=300
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        # Detect if user said it didn’t work
        if user_input.strip().lower() in ["no", "didn't work", "does not work", "nope"]:
            st.session_state.current_index += 1
            if st.session_state.current_index < len(st.session_state.candidates):
                score, entry = st.session_state.candidates[st.session_state.current_index]
