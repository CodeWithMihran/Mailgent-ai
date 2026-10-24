# Mailgent-ai: Project Context & Conversation History

This document contains the project brief, conversation context, architectural decisions, and step-by-step implementation guide for **Mailgent** built during **Fetch-A-Thon 3.0** (24 October 2026).

---

## 1. Hackathon Overview & Problem Statement

### The Event
* **Hackathon:** Fetch-A-Thon 3.0 (Fetch.ai Innovation Lab, 24 October 2026).
* **Theme:** *"ASI:One Agent Challenge — From Intent to Action"*.
* **Timeframe:** ~6 hours build time.
* **Core Requirement:** Build an autonomous AI agent registered on Agentverse, implementing the Agent Chat Protocol (ACP), and executing a multi-step real-world action from ASI:One chat. No custom frontend needed—the demo runs inside ASI:One.

### The Problem
Students and fresh graduates applying for internships and jobs receive hundreds of emails weekly:
* Interview invitations and screening assessments
* Application status updates and rejections
* College notices and academic announcements
* Promotional newsletters, receipts, and marketing spam

Crucial interview invites get buried, and deadlines get missed. Sorting through 200+ emails by hand is slow, stressful, and error-prone.

### The Solution: Mailgent
An autonomous inbox assistant accessible via **ASI:One**.
* **Intent:** The user types `"Audit my last 200 emails"` in ASI:One chat.
* **Inspection:** Mailgent connects to Gmail, parses recent emails, and classifies them into structured categories.
* **Intelligence:** Flags high-priority items and detects upcoming deadlines (e.g. *"Interview invite: reply by Friday 5 PM"*).
* **Safety / HITL:** Generates a structured audit report and presents a **Human-in-the-Loop (HITL)** approval card.
* **Action:** Upon user approval (`"Approve"`), Mailgent creates `[Agent]` labels in Gmail, tags important emails, and archives promotional clutter from the inbox.

---

## 2. Technical Stack & Architecture

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Agent Framework** | Fetch.ai `uagents` | Autonomous agent runtime and lifecycle management |
| **Communication** | Agent Chat Protocol (ACP) | Standardized messaging protocol for ASI:One |
| **Registry & Mailbox** | Fetch.ai Agentverse | Agent discovery, Almanac registration, and message routing |
| **User Interface** | ASI:One (`asi1.ai`) | Web3 native chat interface where users interact with the agent |
| **Email Service** | Google Gmail API (Python) | Fetching emails, metadata parsing, label creation, and batch modifications |
| **Classification** | Hybrid Rule & Heuristic Engine | Zero-latency, reliable categorization and regex-based deadline extraction |

### Workflow Architecture
```
[User on ASI:One]
       │
       ▼ (Agent Chat Protocol - ChatMessage)
[Mailgent (uAgent)] ──(OAuth 2.0)──► [Gmail API]
       │                                  │
       ├─► Fetches unread/recent emails ──┘
       ├─► Classifies into Categories:
       │     • Job / Internship (Interviews, assessments)
       │     • Academic / College notices
       │     • Finance / Receipts
       │     • Promotions / Newsletters
       │     • Other / General
       ├─► Extracts deadlines & urgent action items (48h window)
       ├─► Returns Summary & HITL Approval Card to ASI:One
       │
[User sends "Approve"]
       │
       ▼
[Mailgent applies actions via Gmail API]
       ├─► Creates labels: [Agent] Job, [Agent] Urgent
       ├─► Applies labels to matching emails
       └─► Archives promotional emails (removes from INBOX)
       │
       ▼
[Success Report sent back to ASI:One]
```

---

## 3. Project File Structure

```text
Mailgent-ai/
├── README.md                  # Project overview, installation, and demo guide
├── CONVERSATION_HISTORY.md    # Complete conversation context and design notes
├── requirements.txt           # Python dependencies
├── credentials.json           # Google Cloud OAuth 2.0 client secret (keep secret)
├── token.json                 # Generated OAuth token for headless execution
├── gmail_service.py           # Gmail API wrapper (read, label, archive)
├── classifier.py              # Email categorization and deadline detection
└── agent.py                   # Fetch.ai uAgent with ACP and Agentverse Mailbox
```

---

## 4. Implementation Details

### `requirements.txt`
```txt
uagents>=0.12.0
uagents-core>=0.1.0
google-api-python-client>=2.100.0
google-auth-httplib2>=0.2.0
google-auth-oauthlib>=1.2.0
python-dotenv>=1.0.0
```

### `gmail_service.py`
Provides helper methods:
* `fetch_recent_emails(max_results)`: Reads latest emails from `INBOX` with Subject, From, Date, and Snippet.
* `get_or_create_label(label_name)`: Checks if `[Agent] Job` or `[Agent] Urgent` exists; if not, creates them.
* `apply_actions(label_map, archive_ids)`: Applies target labels and removes `INBOX` label from promotional emails.

### `classifier.py`
* Detects categories using targeted keyword patterns.
* Extracts deadlines via regex patterns (e.g., *"reply by Friday"*, *"due date: [date]"*).
* Prepares action plans without executing until explicit approval is granted.

### `agent.py`
* Initializes `Agent(name="inbox_agent", mailbox=True)`.
* Attaches `chat_proto` using `chat_protocol_spec` from `uagents_core.contrib.protocols.chat`.
* Implements message handlers for `@chat_proto.on_message(model=ChatMessage)`:
  * Responds to `"Audit"` requests with analysis and approval card.
  * Responds to `"Approve"` requests by calling `gmail_service.apply_actions()`.
  * Responds to `"Cancel"` by clearing pending state.

---

## 5. Hackathon 6-Hour Time Budget

* **Hour 1:** Google Cloud project setup, enable Gmail API, configure OAuth Consent screen, download `credentials.json`, seed demo inbox with sample job & promotional emails.
* **Hour 2:** Build and test `gmail_service.py` standalone. Verify reading, labeling, and archiving.
* **Hour 3:** Build and test `classifier.py`. Verify category grouping and deadline extraction.
* **Hour 4:** Implement `agent.py` with `uagents` ACP protocol and in-memory pending action state.
* **Hour 5:** Connect Agentverse Mailbox (`mailbox=True`), publish manifest to Almanac, test chat on `asi1.ai`.
* **Hour 6:** Record 2-minute demo video, complete `README.md`, submit to Devpost.

---

## 6. Demo Video Script (2 Minutes)

* **0:00 – 0:25:** **The Problem** — Introduce how job-hunting students lose critical interview invitations in an inbox clogged with 100s of marketing emails.
* **0:25 – 0:45:** **The Solution & Fetch.ai Stack** — Open ASI:One (`asi1.ai`). Show Mailgent connected via Agent Chat Protocol and registered on Agentverse. Prompt: *"Audit my last emails"*.
* **0:45 – 1:15:** **Intent to Action & Audit Card** — Mailgent returns a categorized breakdown, highlights an urgent interview deadline, and presents a Human-in-the-Loop action proposal.
* **1:15 – 1:40:** **Approval & Execution** — Type *"Approve"*. Switch to the Gmail tab to show the new `[Agent]` labels created and applied, and the promotional clutter archived.
* **1:40 – 2:00:** **Conclusion** — Summarize impact: privacy-focused, zero missed opportunities, powered by Fetch.ai.
