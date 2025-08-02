import streamlit as st
import json

st.title("🛠 AI Troubleshooting Assistant")

# Load troubleshooting data
with open("troubleshooting.json", "r") as f:
    troubleshooting_data = json.load(f)

user_input = st.text_input("Describe your issue:")

if user_input:
    # Simple search (basic prototype, no AI yet)
    for entry in troubleshooting_data:
        if user_input.lower() in entry["problem"].lower():
            st.write("### Problem Found:")
            st.write(f"**Problem:** {entry['problem']}")
            st.write(f"**Causes:** {entry['causes']}")
            st.write(f"**Solution:** {entry['solution']}")
            break
    else:
        st.warning("No matching problem found in the database.")
