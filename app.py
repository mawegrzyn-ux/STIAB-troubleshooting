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

user_input = st.text_input("Describe your issue:")

def get_match_label(score):
    if score >= 80:
        return "Best Match"
    elif score >= 65:
        return "Good Match"
    else:
        return "Possible Match"

if user_input:
    # Fuzzy search
    best_matches = []
    for entry in troubleshooting_data:
        score_problem = fuzz.partial_ratio(user_input.lower(), entry["problem"].lower())
        score_try = fuzz.partial_ratio(user_input.lower(), entry["what_to_try_first"].lower())
        score = max(score_problem, score_try)
        if score > 50:  # lowered threshold for better matching
            best_matches.append((score, entry))
    
    # Sort by best score
    best_matches.sort(reverse=True, key=lambda x: x[0])

    if best_matches:
        st.subheader("🔍 Possible Matches")
        
        # Show up to 3 matches
        top_matches = best_matches[:3]

        for idx, (score, match) in enumerate(top_matches, start=1):
            context = (
                f"System: {match['system']}\n"
                f"Problem: {match['problem']}\n"
                f"What to Try First: {match['what_to_try_first']}\n"
                f"When to Call Support: {match['when_to_call_support']}\n"
            )

            # Ask GPT to explain
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are a helpful IT troubleshooting assistant. "
                            "Base your answer only on the troubleshooting entry provided below. "
                            "If it doesn’t exactly match the user’s problem, give the closest advice you can from the guide. "
                            "If the guide does not cover the issue, say: 'This issue is not covered. Please contact support.'"
                        )
                    },
                    {"role": "user", "content": f"My issue: {user_input}"},
                    {"role": "assistant", "content": f"Troubleshooting entry:\n{context}"}
                ],
                max_tokens=300
            )

            match_label = get_match_label(score)

            st.markdown(f"### {idx}. {match['problem']} ({match_label})")
            st.write(response.choices[0].message.content)
            st.markdown("---")
    else:
        st.warning("No close matches found in the troubleshooting database.")
