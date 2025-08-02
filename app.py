import streamlit as st
import json
import os
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

user_input = st.text_input("Describe your issue:")

if user_input:
    # Fuzzy search
    best_matches = []
    for entry in troubleshooting_data:
        score_problem = fuzz.partial_ratio(user_input.lower(), entry["problem"].lower())
        score_try = fuzz.partial_ratio(user_input.lower(), entry["what_to_try_first"].lower())
        score = max(score_problem, score_try)
        if score > 60:  # threshold for match
            best_matches.append((score, entry))
    
    best_matches.sort(reverse=True, key=lambda x: x[0])

    if best_matches:
        top_entry = best_matches[0][1]

        # Build context for GPT
        context = (
            f"System: {top_entry['system']}\n"
            f"Problem: {top_entry['problem']}\n"
            f"What to Try First: {top_entry['what_to_try_first']}\n"
            f"When to Call Support: {top_entry['when_to_call_support']}\n"
        )

        # Send to GPT with strict instructions
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful IT troubleshooting assistant. Only use the information provided in the troubleshooting guide. If the answer is not in the guide, say: 'I don’t know. Please contact support.' Do not make up answers."},
                {"role": "user", "content": f"My issue: {user_input}"},
                {"role": "assistant", "content": f"Troubleshooting guide:\n{context}"}
            ],
            max_tokens=300
        )

        st.subheader("💡 Suggested Solution")
        st.write(response.choices[0].message.content)

    else:
        st.warning("No close matches found in the troubleshooting database.")
