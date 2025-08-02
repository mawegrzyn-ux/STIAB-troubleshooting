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
- **Features (future iterations):**  
  - Log Yes/No responses for reporting.  
  - Export logs to CSV or Google Sheets.  
  - Analytics dashboard for common issues.  

---

## 📌 User Stories  

**As a store staff member:**  
1. I want to **choose my system** (or say *I’m not sure*) so I don’t get irrelevant answers.  
2. I want to **type my issue** in my own words so I don’t have to know technical terms.  
3. I want the app to **suggest possible problems** so I can pick the closest one.  
4. I want GPT to **explain the fix in plain language** so I can understand it.  
5. I want to **confirm if the fix worked** with a simple Yes/No button.  
6. If the fix didn’t work, I want the app to **suggest another solution** without me starting over.  
7. If no solutions work, I want the app to **tell me to contact support** instead of guessing.  

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
