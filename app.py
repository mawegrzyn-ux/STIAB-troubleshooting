import streamlit as st
import json

st.title("🛠 AI Troubleshooting Assistant")

# Load troubleshooting data
with open("troubleshooting.json", "r") as f:
    troubleshooting_data = json.load(f)

# Ask user for their issue
user_input = st.text_input("Describe your issue:")

if user_input:
    results = []
    for entry in troubleshooting_data:
        if user_input.lower() in entry["problem"].lower() or user_input.lower() in entry["what_to_try_first"].lower():
            results.append(entry)

    if results:
        for r in results:
            st.subheader(f"{r['system']} Issue: {r['problem']}")
            st.write(f"**What to Try First:** {r['what_to_try_first']}")
            st.write(f"**When to Call Support:** {r['when_to_call_support']}")
            st.markdown("---")
    else:
        st.warning("No matching problem found in the database.")
