# Mailgent 📬🤖

> **Autonomous AI Inbox Assistant for Students**  
> *Built for Fetch-A-Thon 3.0: "ASI:One Agent Challenge — From Intent to Action"*

[![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-blue)](https://fetch.ai)
[![Protocol](https://img.shields.io/badge/Protocol-Agent%20Chat%20Protocol%20(ACP)-green)](https://asi1.ai)
[![Platform](https://img.shields.io/badge/Platform-Agentverse%20%7C%20ASI:One-purple)](https://agentverse.ai)

---

## 🎯 The Problem
Students and graduates applying for jobs receive hundreds of emails every week. Critical interview invitations, assessment links, and deadlines get buried under promotional offers, newsletters, and receipts. Missing an interview email means missing a career opportunity.

## 💡 The Solution
**Mailgent** is an autonomous AI agent accessible through **ASI:One**.
1. **Audit & Classify:** Scans recent Gmail messages and classifies them into *Job/Internship*, *Academic*, *Finance*, and *Promotions*.
2. **Flag Deadlines:** Detects urgent deadlines requiring action within 48 hours.
3. **Human-in-the-Loop (HITL) Safety:** Shows an audit summary and requests approval before modifying your inbox.
4. **Action:** On approval, automatically applies `[Agent] Job` and `[Agent] Urgent` labels in Gmail and archives clutter.

---

## 🛠️ Architecture & Tech Stack
* **Agent Framework:** `uagents` (Fetch.ai)
* **Chat Interface:** ASI:One (`asi1.ai`) via Agent Chat Protocol (ACP)
* **Agent Directory:** Agentverse Registry & Mailbox
* **API Integration:** Google Gmail API (OAuth 2.0)

---

## 🚀 Quick Start

### 1. Prerequisites
* Python 3.10+
* Google Cloud project with Gmail API enabled (`credentials.json`)
* Fetch.ai Agentverse account ([agentverse.ai](https://agentverse.ai))

### 2. Setup
```bash
git clone https://github.com/<your-username>/mailgent.git
cd mailgent

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Google API Credentials
Place your `credentials.json` from Google Cloud Console into the root of this repository.

### 4. Run Mailgent
```bash
python agent.py
```
Follow the terminal instructions to link your local agent to the Agentverse Mailbox. Once active, interact with Mailgent directly on [asi1.ai](https://asi1.ai).

---

## 📖 Complete Planning & Conversation Notes
For in-depth background discussions, problem analysis, architecture diagrams, and the full build roadmap, check [CONVERSATION_HISTORY.md](CONVERSATION_HISTORY.md).
