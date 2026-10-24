# Mailgent 📬🤖

> **Autonomous AI Inbox Assistant for Students**  
> *Built for Fetch-A-Thon 3.0: "ASI:One Agent Challenge — From Intent to Action"*

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
[![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-blue)](https://fetch.ai)
[![Protocol](https://img.shields.io/badge/Protocol-Agent%20Chat%20Protocol%20(ACP)-green)](https://asi1.ai)
[![Platform](https://img.shields.io/badge/Platform-Agentverse%20%7C%20ASI:One-purple)](https://agentverse.ai)

---

## 📌 Agent Metadata (Innovation Lab / Agentverse)
* **Agent Name:** `mailgent`
* **Agent Address:** `agent1qtdpknm8y3vqxj2sgvme5ql6wsqau7m9c3drd7k74avry64nnaxxs5y35ya`
* **Protocol:** Agent Chat Protocol (ACP) v0.4.12
* **Target UI:** [ASI:One](https://asi1.ai)
* **Framework:** Fetch.ai `uagents` (Python 3.10+)

---

## 🎯 The Problem
For college students and graduates applying for jobs, their email inbox is the single point of failure between a dream career and missed opportunities:
* **Overwhelming Volume:** Hundreds of recruitment confirmations, newsletters, receipts, and campus alerts every week.
* **Buried Deadlines:** Critical interview scheduling links and HackerRank assessments with strict **24-to-48-hour expiration deadlines** get buried under clutter.
* **The Ghosting Void:** Recruiters frequently go silent after applications, leaving candidates unsure of when and how to follow up professionally.

---

## 💡 The Solution: Mailgent (From Intent to Action)
Mailgent turns simple natural language prompts in **ASI:One chat** into real-world autonomous actions inside Gmail:

1. **Autonomous Audit & Classification (`Audit`):** Scans recent emails and groups them into `Job/Internship`, `Academic`, `Finance`, and `Promotions`.
2. **48-Hour Deadline Radar:** Analyzes email bodies for urgent action items (e.g. *"Complete assessment within 48 hours"*, *"Interview invite: reply by Friday 5 PM"*).
3. **👻 Ghosting Radar (Creative Innovation):** Detects stalled job applications (> 5 days without response) and automatically prepares context-aware follow-up emails in your **Gmail Drafts folder**.
4. **Human-in-the-Loop (HITL) Safety (`Approve` / `Cancel`):** Delivers an interactive Approval Card in ASI:One chat summarizing proposed actions before modifying your inbox.
5. **Real-World Inbox Execution:** Upon typing `Approve`, Mailgent creates and applies `[Agent] Job` and `[Agent] Urgent` labels, saves follow-up drafts, and archives promotional clutter.
6. **Student Career Radar (`Pipeline`):** Aggregates all recruitment communications into an active board of interview loops, coding challenges, and status reviews.
7. **Instant Gmail Search (`Search <term>`):** Live keyword search across your inbox (e.g. `Search interview`, `Search stipend`).
8. **Live Account Profile (`Profile`):** Displays real-time Gmail connection stats, message counts, and threads.

---

## 🛠️ Architecture & Workflow

```
[User on ASI:One]
       │
       ▼ (Agent Chat Protocol - ChatMessage)
[Mailgent (uAgent)] ──(OAuth 2.0)──► [Gmail API]
       │                                   │
       ├─► 1. Fetches recent inbox emails ─┘
       ├─► 2. Classifies: Job, Academic, Finance, Promo
       ├─► 3. Flags <48h deadlines & stalled applications
       ├─► 4. Returns Audit & HITL Approval Card to ASI:One
       │
[User replies "Approve"]
       │
       ▼
[Mailgent Executes Real-World Actions]
       ├─► Creates labels: [Agent] Job, [Agent] Urgent
       ├─► Labels job invitations & critical deadlines
       ├─► Creates follow-up email drafts in Gmail Drafts
       └─► Archives promotional emails from INBOX
       │
       ▼
[Success Confirmation Card sent back to ASI:One]
```

---

## 🚀 Quick Start & Local Testing

### 1. Prerequisites
* Python 3.10+ (Checked and fully compatible with Python 3.13 / 3.14)
* Fetch.ai Agentverse Account ([agentverse.ai](https://agentverse.ai))
* Google Cloud OAuth 2.0 Credentials (optional: offline fallback provided)

### 2. Installation
```bash
git clone https://github.com/CodeWithMihran/Mailgent-ai.git
cd Mailgent-ai

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Immediate Zero-Configuration Test (Interactive CLI)
You can test the entire conversation and execution flow right in your terminal with the included 50-email realistic dataset:
```bash
python agent.py --cli
```
* Type `Audit` to scan the inbox.
* Type `Approve` to execute labels, follow-up drafts, and archiving!

### 4. Connect to Live Gmail (Optional)
1. Download your OAuth 2.0 client secret JSON from Google Cloud Console and place it as `credentials.json`.
2. Run the one-time authentication script:
   ```bash
   python auth_once.py
   ```
3. (Optional) Inject the 50 realistic demo emails into your test Gmail inbox:
   ```bash
   python seed_inbox.py
   ```

### 5. Connect to Agentverse & ASI:One
1. Get your Mailbox key from [Agentverse.ai](https://agentverse.ai).
2. Add your key to `.env`:
   ```env
   AGENT_MAILBOX_KEY="your_agentverse_mailbox_key_here"
   ```
3. Run Mailgent:
   ```bash
   python agent.py
   ```
4. Open [asi1.ai](https://asi1.ai), search for your agent's address, and send:
   `"Audit my emails"`!

---

## 📂 Repository File Structure
```text
Mailgent-ai/
├── README.md              # Project overview, badges, and submission guide
├── agent.py               # Main uAgent: Agent Chat Protocol (ACP) handler
├── gmail_tools.py         # Gmail API wrapper: fetch, labels, archive, drafts
├── llm.py                 # Hybrid classifier: ASI:One LLM API + zero-latency NLP
├── cards.py               # HITL approval cards & Ghosting Radar payloads
├── auth_once.py           # Google OAuth 2.0 login helper
├── seed_inbox.py          # Demo inbox injector (50 realistic emails)
├── verify_phase2.py       # Automated environment & schema verification suite
├── sample_emails.json     # 50 realistic student/applicant test emails
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── .gitignore             # Safeguards credentials and local state
```

---

## 🏆 Hackathon Alignment & Judging Criteria
* **From Intent to Action:** Doesn't stop at text; manages live Gmail labels, drafts, and archives.
* **Innovation & Creativity:** Introduces the **Ghosting Radar** to draft follow-ups for stalled applications and **48-Hour Deadline Radar**.
* **Zero UI Overhead:** Complete user workflow demonstrated natively inside an ASI:One conversation.
* **Rock-Solid Reliability:** Built-in dual-mode ensures seamless demo presentations even in offline/rate-limited environments.
