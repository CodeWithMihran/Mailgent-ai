# Mailgent 📬🤖

> **Autonomous AI Inbox Assistant for Students**  
> *Built for Fetch-A-Thon 3.0: "ASI:One Agent Challenge — From Intent to Action"*

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
[![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-blue)](https://fetch.ai)
[![Protocol](https://img.shields.io/badge/Protocol-Agent%20Chat%20Protocol%20(ACP)-green)](https://asi1.ai)
[![Platform](https://img.shields.io/badge/Platform-Agentverse%20%7C%20ASI:One-purple)](https://agentverse.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Agentverse & ASI:One Metadata
* **Agent Name:** `mailgent`
* **Agent Handle:** `@mailgent`
* **Agent Address:** `agent1qtdpknm8y3vqxj2sgvme5ql6wsqau7m9c3drd7k74avry64nnaxxs5y35ya`
* **Agentverse Profile:** [agentverse.ai/agents/details/agent1qtdpknm8y3vqxj2sgvme5ql6wsqau7m9c3drd7k74avry64nnaxxs5y35ya/profile](https://agentverse.ai/agents/details/agent1qtdpknm8y3vqxj2sgvme5ql6wsqau7m9c3drd7k74avry64nnaxxs5y35ya/profile)
* **Protocol:** Agent Chat Protocol (ACP) v0.4.12
* **Registration Status:** **Active** on Agentverse Almanac API

---

## 🎯 The Problem
For college students and job applicants, their email inbox is the single point of failure between a dream career and missed opportunities:
* **Overwhelming Clutter:** Hundreds of newsletter blasts, campus advisories, receipts, and promotional offers drown out important updates every week.
* **Strict 24–48 Hour Expiration Windows:** Critical interview scheduling portals, screening questionnaires, and HackerRank assessments frequently expire within 24 to 48 hours.
* **The Ghosting Void:** Recruiters often go silent after applications. Students struggle to identify stalled applications and lack the time to draft polite, professional follow-ups.

---

## 💡 The Solution: Mailgent (From Intent to Action)
**Mailgent** is not a passive chatbot or a raw API wrapper. It is an autonomous AI agent accessible through **ASI:One** that transforms a single natural language intent into real-world inbox organization:

1. **Autonomous Email Triage (`Audit`):** Scans recent messages and groups them into `Job/Internship`, `Academic`, `Finance`, and `Promotions`.
2. **48-Hour Deadline Radar:** Analyzes email bodies for urgent temporal commitments (e.g. *"Assessment link expires in 48 hours"*, *"Select interview slot by Friday 5 PM"*).
3. **👻 Ghosting Radar (Innovative Feature):** Identifies job applications with zero recruiter updates for over 5 days and auto-composes context-aware follow-up emails into your **Gmail Drafts folder**.
4. **Human-in-the-Loop (HITL) Safety (`Approve` / `Cancel`):** Presents an interactive Markdown Approval Card in ASI:One chat summarizing proposed actions before altering your inbox.
5. **Real-World Gmail Execution:** On approval, Mailgent creates and applies `[Agent] Job` and `[Agent] Urgent` Gmail labels, archives promotional clutter out of the primary inbox, and writes follow-up drafts.
6. **Student Career Radar (`Pipeline`):** Aggregates all recruitment communications into an active board of active interview loops, expiring challenges, and application updates.
7. **Live Inbox Search (`Search <term>`):** Instant keyword query across live Gmail messages with formatted markdown snippet cards.
8. **Live Account Profile (`Profile`):** Displays real-time connection status, authenticated email, total messages, and active thread counts.

---

## ⚖️ How Mailgent Compares to Generic Email Tools

| Capability | Generic API Wrappers | **Mailgent (Autonomous Agent)** |
| :--- | :--- | :--- |
| **User Interaction** | Requires manual, low-level commands with message IDs (e.g. `move to trash 1875f4...`) | **Single high-level intent:** `"Audit my emails"` |
| **Intelligence** | No reasoning; dumps raw JSON strings | **Dual-Engine AI Reasoning:** Category triage, 48h deadline detection, and Ghosting Radar |
| **Safety & Control** | Immediate destructive actions with zero preview | **Human-in-the-Loop (HITL) Approval Cards** before applying changes |
| **Career Impact** | None; treats job alerts the same as newsletters | Proactively rescues interviews from expiring and auto-drafts recruiter follow-ups |
| **Offline Reliability** | Fails immediately if credentials or network drop | **Dual-Mode Architecture:** Live Gmail API + 50-email realistic offline fallback |

---

## 🛠️ Architecture & Workflow

```
[User on ASI:One]
       │
       ▼ (Agent Chat Protocol - ChatMessage)
[Mailgent (uAgent)] ──(OAuth 2.0)──► [Google Gmail API]
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

## 💬 Command Reference & Examples

| Intent / Command | Description | Example Output |
| :--- | :--- | :--- |
| **`Audit`** | Autonomous scan, classification, and HITL proposal card | `### 📬 Mailgent Inbox Audit Report` with categories and 48h deadlines |
| **`Approve`** | Executes proposed actions in Gmail | `### ✅ Inbox Actions Successfully Applied!` with label & draft counts |
| **`Cancel`** | Discards pending proposal safely | `🛑 Action proposal cancelled. No changes were made.` |
| **`Pipeline`** | Student career radar & interview loops | `### 💼 Student Career Radar & Job Pipeline` (Interviews, Tests, Reviews) |
| **`Search <term>`** | Live keyword search across inbox | `### 🔎 Search Results for '<term>'` (e.g. `search interview`) |
| **`Draft`** | Composes custom email draft in Gmail | `### 📝 Follow-Up Draft Created!` ready in your Gmail Drafts folder |
| **`Profile`** | Real-time Gmail connection stats | `### 📇 Mailgent Live Connection Status` (Account, mode, message counts) |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
* Python 3.10+ (Tested and verified on Python 3.13 and Python 3.14)
* Fetch.ai Agentverse Account ([agentverse.ai](https://agentverse.ai))
* Google Cloud OAuth 2.0 Credentials (optional: offline fallback included)

### 2. Setup
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

### 3. Immediate Interactive Test (Zero-Config CLI)
You can run the full agent conversation and execution loop right in your terminal:
```bash
python agent.py --cli
```
* Type `Profile` to check connection status.
* Type `Pipeline` to view your active career radar.
* Type `Audit` to scan and generate the HITL approval card.
* Type `Approve` to apply labels and drafts.

### 4. Connect to Live Gmail (OAuth 2.0)
1. Download your OAuth 2.0 client secret JSON from [Google Cloud Console](https://console.cloud.google.com/) and place it as `credentials.json` in the root folder.
2. Run the one-time authentication script:
   ```bash
   python auth_once.py
   ```
3. Enable the **Gmail API** in Google Cloud Console.
4. Run `python agent.py` — Mailgent will automatically detect `token.json` and switch from `OFFLINE (Mock)` to `LIVE (Gmail API)`.

### 5. Connect to Agentverse & ASI:One
1. Get your Mailbox key from [Agentverse.ai](https://agentverse.ai).
2. Add your key to `.env`:
   ```env
   AGENT_MAILBOX_KEY="your_agentverse_mailbox_key_here"
   ```
3. Run the live agent:
   ```bash
   python agent.py
   ```
4. Open [asi1.ai](https://asi1.ai), search for your agent address, and send:
   `"Audit my emails"`!

---

## 📂 Repository File Structure
```text
Mailgent-ai/
├── README.md              # Project overview, architecture, and submission guide
├── agent.py               # Main uAgent: ACP protocol handler & intent orchestrator
├── gmail_tools.py         # Google Gmail API wrapper: fetch, labels, archive, drafts
├── llm.py                 # Hybrid classifier: ASI:One LLM API + zero-latency NLP
├── cards.py               # HITL approval cards, Ghosting Radar, and pipeline views
├── auth_once.py           # Google OAuth 2.0 login helper & token generator
├── seed_inbox.py          # Demo inbox injector (50 realistic student emails)
├── verify_phase2.py       # Automated environment & schema verification suite
├── sample_emails.json     # 50 realistic student/applicant test emails
├── dump_code.py           # Clean codebase exporter for review & inspection
├── requirements.txt       # Python dependencies (uagents, google-api, etc.)
├── .env.example           # Environment template with secret keys masked
└── .gitignore             # Safeguards credentials and local state
```

---

## 🔒 Security & Privacy
* **Local Credentials:** `credentials.json` and `token.json` are stored strictly on your local machine and are excluded by `.gitignore`.
* **Owner Allowlist (`OWNER_ADDRESS`):** Built-in address security whitelist ensures that only the authenticated owner can trigger inbox actions.
* **Human-in-the-Loop:** Mailgent never deletes or archives emails without explicit user confirmation (`Approve`).

---

## 🏆 Hackathon Alignment & Criteria

* **From Intent to Action (25%):** Executes real-world Gmail operations (labeling, archiving, and drafts) directly from natural language chat.
* **Use of Fetch.ai Tech (20%):** Built natively with `uagents`, implements the official Agent Chat Protocol (ACP), and connects via Agentverse Mailbox & Almanac.
* **Innovation & Creativity (20%):** Features the **Ghosting Radar** to draft recruiter follow-ups and the **48-Hour Deadline Radar** to prevent missed career opportunities.
* **Real-World Impact (20%):** Solves a universal, high-stakes pain point for job-seeking college students and new graduates.
* **Zero UI Overhead (15%):** The entire user workflow is demonstrated natively inside an ASI:One conversation.

---

## 👤 Author
* **Developer:** Md Mihran Sohail
* **Hackathon:** Fetch-A-Thon 3.0 (Fetch.ai Innovation Lab)
* **GitHub:** [@CodeWithMihran](https://github.com/CodeWithMihran)
