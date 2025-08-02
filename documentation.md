# 🛠 Troubleshooting Assistant — Documentation  

## 📑 Table of Contents  
- [Purpose](#-purpose)  
- [Scope](#-scope)  
- [Epics](#-epics)  
- [User Stories](#-user-stories)  
- [Iteration History & Changes](#-iteration-history--changes)  
- [User Flow Diagram](#-user-flow-diagram)  
- [Next Planned Iterations](#-next-planned-iterations)  

---

## 📌 Purpose  
The purpose of this app is to provide an **AI‑assisted troubleshooting tool** for store staff to quickly diagnose and resolve issues with **KDS, Kiosk Software, and POS systems**, reducing downtime and dependency on support teams.  

It combines a **searchable troubleshooting knowledge base** with an **interactive chat assistant powered by GPT**, offering step‑by‑step guidance and follow‑up questions.  

---

## 📌 Scope  

**In Scope**  
- Store staff usage on desktop or tablet.  
- Troubleshooting KDS, Kiosk, and POS systems.  
- Keyword search with fuzzy matching (handles typos).  
- System selection for better filtering, with *“I’m not sure”* fallback.  
- Conversational responses powered by GPT.  
- Follow‑up questions with Yes/No buttons.  
- JSON‑based troubleshooting knowledge base.  

**Out of Scope**  
- Automatic remote fixes.  
- Real‑time integration with monitoring tools.  
- User authentication or role‑based access.  
- Support ticket escalation workflow (future iteration).  

---

## 📌 Epics  

### Epic 1: Knowledge Base Search  
- **Goal:** Users can search troubleshooting content stored in a JSON file.  
- **Features:**  
  - Keyword search with fuzzy matching.  
  - Filtering by system (KDS, Kiosk Software, POS).  
  - *“I’m not sure”* option to search all systems.  

### Epic 2: AI Conversational Guidance  
- **Goal:** Provide natural, easy‑to‑follow solutions.  
- **Features:**  
  - GPT‑powered explanation of troubleshooting steps.  
  - Follow‑up questions to narrow down the issue.  
  - Responses limited to the troubleshooting guide (no hallucinations).  

### Epic 3: Interactive Support Flow  
- **Goal:** Help users confirm or refine solutions.  
- **Features:**  
  - Yes/No buttons after each suggestion.  
  - Move to the next best match if “No”.  
  - Friendly resolution message if “Yes”.  
  - Escalation to support if all options fail.  

### Epic 4: Continuous Improvement  
- **Goal:** Enable future learning from real usage.  
- **Features:**  
  - Log Yes/No responses for reporting.  
  - Export logs to CSV or Google Sheets.  
  - Analytics dashboard for common issues.  

### Epic 5: Progressive Disclosure of Steps [Future Epic]  
- **Goal:** Simplify the user experience with a guided, step‑by‑step flow.  
- **Features:**  
  - Break the journey into clear steps (System → Issue → Suggestions → Confirmation).  
  - Use progress indicators to reassure users.  

### Epic 6: Dynamic Problem Categories [Future Epic]  
- **Goal:** Make searching easier for non‑technical users.  
- **Features:**  
  - Present clickable categories for common issues per system.  
  - Allow users to skip typing if their issue fits a category.  

### Epic 7: Instant Quick Fixes [Future Epic]  
- **Goal:** Reduce waiting time for answers.  
- **Features:**  
  - Show “What to Try First” steps instantly.  
  - Let GPT expand with a conversational explanation in parallel.  

### Epic 8: Escalation Flow [Future Epic]  
- **Goal:** Help users get support when automation fails.  
- **Features:**  
  - Offer a “Contact Support” button after 2–3 failed attempts.  
  - Pre‑fill ticket with issue details and steps already tried.  

### Epic 9: Knowledge Base Fallback Search [Future Epic]  
- **Goal:** Ensure no dead ends.  
- **Features:**  
  - If fuzzy matching finds nothing, run a broader keyword search across all systems.  
  - Show closest related problems with lower match scores.  

### Epic 10: Feedback Loop for Quality [Future Epic]  
- **Goal:** Continuously improve content and AI explanations.  
- **Features:**  
  - After resolution, ask “Was this explanation clear?” 👍 👎  
  - Store feedback for review and guide content updates.  

### Epic 11: Multilingual Support [Future Epic]  
- **Goal:** Support EMEA staff in their local languages.  
- **Features:**  
  - Allow users to select language at start.  
  - GPT provides troubleshooting responses in the chosen language.  
  - Localize buttons and static text.  

### Epic 12: Mobile‑Friendly Experience [Future Epic]  
- **Goal:** Optimize for tablets and small devices.  
- **Features:**  
  - Large, touch‑friendly buttons.  
  - Minimized typing.  
  - Adaptive layout for small screens.  

---

## 📌 User Stories  

**As a store staff member:**  
1. I want to **choose my system** (or say *I’m not sure*) so I don’t get irrelevant answers.  
2. I want to **type my issue** in my own words so I don’t have to know technical terms.  
3. I want the app to **suggest possible problems** so I can pick the closest one.  
4. I want the app to **show the system name in suggestions when I pick “I’m not sure.”**  
5. I want GPT to **explain the fix in plain language** so I can understand it.  
6. I want to **confirm if the fix worked** with a simple Yes/No button.  
7. If the fix didn’t work, I want the app to **suggest another solution** without me starting over.  
8. If no solutions work, I want the app to **tell me to contact support** instead of guessing.  
9. I want the app to **show categories of common problems** so I can pick quickly.  
10. I want to **see immediate quick fixes** before GPT finishes its answer.  
11. I want the app to **be easy to use on a tablet** with minimal typing.  
12. I want the option to **get help in my own language** when working across EMEA.  

---

## 📌 Iteration History & Changes  

### Iteration 1 — MVP  
- Built a Streamlit app with keyword search.  
- Loaded troubleshooting content from JSON.  
- Showed first matching problem/solution.  

### Iteration 2 — Added GPT  
- Integrated OpenAI GPT for conversational answers.  
- Prompt restricted to JSON content.  
- Issues: GPT too strict, ignored fuzzy matches.  

### Iteration 3 — Improved Fuzzy Matching  
- Lowered fuzzy threshold from 60 → 50.  
- Displayed top 3 matches instead of only one.  
- Added match quality labels: **Best Match / Good Match / Possible Match**.  

### Iteration 4 — Interactive Follow‑Ups  
- Added Yes/No buttons for confirming fixes.  
- “No” leads to the next best match.  
- Session state remembers chat history.  

### Iteration 5 — Problem Suggestions  
- After user input, suggested 3–5 likely problems.  
- User selects from dropdown.  
- GPT explains selected problem’s fix.  

### Iteration 6 — System Selection  
- Added **System choice** (KDS / Kiosk / POS).  
- **“I’m not sure”** option searches all systems.  
- Filtered matches by system when chosen.  

### Iteration 7 — Show System in Suggestions  
- When the user selects *“I’m not sure”*, each suggested problem now includes its **system name** (e.g., `POS - Receipt printer won’t print after payment`).  
- System name also displayed in GPT’s response header.  

---

## 📊 User Flow Diagram  

```mermaid
flowchart TD
    A[User Opens App] --> B[Select System: KDS / Kiosk / POS / I'm not sure]
    B --> C[Describe Issue]
    C --> D{Fuzzy Match Suggests Top 3-5 Problems}
    D --> E[User Selects Problem]
    E --> F[GPT Explains Fix]
    F --> G{Did it work?}
    G -->|Yes| H[Show Success Message]
    G -->|No| I[Try Next Best Match]
    I --> F
    I -->|If none left| J[Advise Contact Support]
