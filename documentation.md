# 🛠 STIAB Assistant — Documentation  

## 📑 Table of Contents  
- [Purpose](#purpose)  
- [Scope](#scope)  
- [Epics](#epics)  
- [User Stories](#user-stories)  
- [Iteration History & Changes](#iteration-history--changes)  
- [Change Log](#change-log)  
- [Code Documentation](#code-documentation)  
- [User Flow Diagram](#user-flow-diagram)  
- [Next Planned Iterations](#next-planned-iterations)  

---

## Purpose  
The purpose of the **STIAB Assistant** is to provide an **AI‑powered troubleshooting tool** for store staff to quickly diagnose and resolve issues with **KDS, Kiosk Software, and POS systems**, reducing downtime and dependency on support teams.  

It combines a **JSON knowledge base** with a **conversational AI assistant (GPT)** for interactive guidance in multiple languages.  

---

## Scope  

**In Scope**  
- Desktop and mobile use by store staff.  
- Troubleshooting KDS, Kiosk, and POS systems.  
- Fuzzy keyword search (handles typos).  
- System selection dropdown with *“I’m not sure”* fallback.  
- GPT‑powered troubleshooting guidance.  
- Follow‑up questions with Yes/No buttons.  
- JSON‑based troubleshooting database.  
- Multilingual support: English, French, Dutch, Spanish, Italian, German.  
- Full UI translation using `translations.json`.  
- Simple 🌐 dropdown selector above app title.  

**Out of Scope**  
- Remote device control or fixes.  
- Real‑time monitoring system integration.  
- User authentication or roles.  
- Support ticket escalation workflow (future).  

---

## Epics  

### Epic 11: Multilingual Support  
- **Goal:** Enable EMEA staff to troubleshoot in their native language.  
- **Features:**  
  - UI and GPT responses fully localized.  
  - Dropdown language selector with 🌐 icon for quick changes.  
  - Translate user queries into English for accurate matching.  
  - Centralized translations in `translations.json`.  

---

## User Stories  

**As a store staff member:**  
1. I want the **whole UI in my chosen language**, so I don’t have to guess what buttons mean.  
2. I want to **type my issue in my own language** and still get relevant troubleshooting steps.  
3. I want to **change my language quickly** via a 🌐 dropdown above the app title.  
4. I want to be offered **top suggestions** based on my query, even if I mistype.  
5. I want to confirm if a solution worked with simple **Yes/No buttons**.  
6. If none of the suggestions work, I want to be told to **contact support**.  

---

## Iteration History & Changes  

### Iteration 21 — STIAB Assistant + Scrollable Flag Bar  
- Renamed the app to **STIAB Assistant**.  
- Added horizontal scrollable flag bar for mobile.  
- Fixed previous issue of full‑width flag buttons.  

### Iteration 22 — Dropdown Language Selector with World Icon  
- Replaced flag bar with **🌐 dropdown selector** above app title.  
- Cleaner and more reliable on both desktop and mobile.  
- Entire UI still localized via `translations.json`.  

---

## Change Log  

| Iteration | Date       | Status | Change Summary |
|-----------|------------|--------|----------------|
| 1 | 2025-07-30 | ✅ Done | Initial MVP with keyword search and troubleshooting JSON. |
| 2 | 2025-07-31 | ✅ Done | Added GPT conversational guidance. |
| 3 | 2025-08-01 | ✅ Done | Improved fuzzy matching with quality labels. |
| 4 | 2025-08-01 | ✅ Done | Added Yes/No confirmation loop. |
| 5 | 2025-08-01 | ✅ Done | Top 3–5 suggestions dropdown. |
| 6 | 2025-08-01 | ✅ Done | Added system selection with “I’m not sure.” |
| 7 | 2025-08-02 | ✅ Done | Added system name to suggestions when unsure. |
| 8 | 2025-08-02 | ✅ Done | Multilingual support enabled (6 languages). |
| 9 | 2025-08-02 | ✅ Done | Localized Yes/No buttons and messages. |
| 17 | 2025-08-02 | ✅ Done | Full UI translation + native language input. |
| 18 | 2025-08-02 | ✅ Done | Flag‑based language selector above title; translations.json introduced. |
| 19 | 2025-08-02 | ✅ Done | CSS separated into styles.css. |
| 20 | 2025-08-02 | ✅ Done | Scrollable flag bar for mobile; switched to st.query_params. |
| 21 | 2025-08-02 | ✅ Done | Renamed to STIAB Assistant; improved flag bar. |
| 22 | 2025-08-02 | ✅ Done | Switched to 🌐 dropdown above title for language selection. |

---

## Code Documentation  

### Project Structure  

