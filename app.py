import streamlit as st
import json
from rapidfuzz import fuzz
from openai import OpenAI

# -------------------
# Setup OpenAI
# -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🤖 AI Troubleshooting Assistant")

# Language choices with flags
languages = {
    "🇬🇧 English": "English",
    "🇫🇷 French": "French",
    "🇳🇱 Dutch": "Dutch",
    "🇪🇸 Spanish": "Spanish",
    "🇮🇹 Italian": "Italian",
    "🇩🇪 German": "German"
}

# UI translations
ui_text = {
    "English": {
        "system_label": "Which system is the issue related to?",
        "issue_placeholder": "Describe your issue",
        "suggestions_label": "Do any of these match your issue?",
        "no_results": "No similar problems found in the database."
    },
    "French": {
        "system_label": "À quel système le problème est-il lié ?",
        "issue_placeholder": "Décrivez votre problème",
        "suggestions_label": "L’un de ces problèmes correspond-il au vôtre ?",
        "no_results": "Aucun problème similaire trouvé dans la base de données."
    },
    "Dutch": {
        "system_label": "Met welk systeem heeft het probleem te maken?",
        "issue_placeholder": "Beschrijf uw probleem",
        "suggestions_label": "Komt een van deze overeen met uw probleem?",
        "no_results": "Geen soortgelijke problemen gevonden in de database."
    },
    "Spanish": {
        "system_label": "¿Con qué sistema está relacionado el problema?",
        "issue_placeholder": "Describe tu problema",
        "suggestions_label": "¿Coincide alguno de estos con tu problema?",
        "no_results": "No se encontraron problemas similares en la base de datos."
    },
    "Italian": {
        "system_label": "A quale sistema è relativo il problema?",
        "issue_placeholder": "Descrivi il tuo problema",
        "suggestions_label": "Uno di questi corrisponde al tuo problema?",
        "no_results": "Nessun problema simile trovato nel database."
    },
    "German": {
        "system_label": "Mit welchem System hängt das Problem zusammen?",
        "issue_placeholder": "Beschreiben Sie Ihr Problem",
        "suggestions_label": "Passt eines dieser Probleme zu Ihrem?",
        "no_results": "Keine ähnlichen Probleme in der Datenbank gefunden."
    }
}

# Translations for buttons and messages
translations = {
    "English": {
        "yes": "✅ Yes, it worked",
        "no": "❌ No, still an issue",
        "success": "Great to hear that solved your problem! 🎉",
        "error": "I’ve run out of suggestions from the guide. Please contact support."
    },
    "French": {
        "yes": "✅ Oui, ça a marché",
        "no": "❌ Non, j’ai encore un problème",
        "success": "Ravi d’apprendre que cela a résolu votre problème ! 🎉",
        "error": "Je n’ai plus de suggestions. Veuillez contacter le support."
    },
    "Dutch": {
        "yes": "✅ Ja, het werkte",
        "no": "❌ Nee, nog steeds een probleem",
        "success": "Fijn om te horen dat het probleem is opgelost! 🎉",
        "error": "Ik heb geen suggesties meer. Neem contact op met de ondersteuning."
    },
    "Spanish": {
        "yes": "✅ Sí, funcionó",
        "no": "❌ No, todavía hay un problema",
        "success": "¡Me alegra saber que eso resolvió tu problema! 🎉",
        "error": "Me he quedado sin sugerencias. Por favor, contacta con soporte."
    },
    "Italian": {
        "yes": "✅ Sì, ha funzionato",
        "no": "❌ No, c’è ancora un problema",
        "success": "Felice di sapere che ha risolto il problema! 🎉",
        "error": "Non ho più suggerimenti. Si prega di contattare l’assistenza."
    },
    "German": {
        "yes": "✅ Ja, es hat funktioniert",
        "no": "❌ Nein, immer noch ein Problem",
        "success": "Schön zu hören, dass dein Problem gelöst wurde! 🎉",
        "error": "Mir sind die Vorschläge ausgegangen. Bitte kontaktiere den Support."
    }
}

# Ask user for preferred language
lang_choice = st.selectbox("🌍 Select your language:", list(languages.keys()))
selected_language = languages[lang_choice]
local_text = translations[selected_language]
ui_local = ui_text[selected_language]

# Load troubleshooting data
with open("troubleshooting.json", "r") as f:
    troubleshooting_data = json.load(f)

# Initialize session state
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

# Step 1: Ask which system
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

# Step 2: If system chosen, ask for issue
if st.session_state.system_choice:
    user_input = st.text_input(ui_local["issue_placeholder"])

    if user_input and not st.session_state.selected_problem:
        # Translate user input to English for matching
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

# Step 3: If a problem was selected
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

# Step 4: Show Yes/No buttons in chosen language
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
