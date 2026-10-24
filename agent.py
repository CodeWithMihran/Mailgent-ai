"""
agent.py
Mailgent: Autonomous AI Inbox Assistant for Students
Built for Fetch-A-Thon 3.0: ASI:One Agent Challenge

Features:
- Agent Chat Protocol (ACP) integration for ASI:One
- Gmail scanning, AI-powered classification, and deadline detection
- Human-in-the-Loop (HITL) approval card presentation
- Automated labeling ([Agent] Job, [Agent] Urgent) and promotional archiving
- Dual-mode support (Live Gmail + Offline fallback)
- Interactive CLI mode for local testing (--cli)
"""

import os
import sys
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

# Ensure event loop exists on Python 3.12+ / 3.14 before uagents import
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    TextContent
)

from gmail_tools import GmailClient
from llm import EmailClassifier
from cards import (
    build_audit_summary_markdown,
    build_audit_success_markdown,
    extract_pending_plan
)

# Configuration
AGENT_NAME = os.getenv("AGENT_NAME", "mailgent")
AGENT_SEED = os.getenv("AGENT_SEED", "mailgent-student-inbox-assistant-v1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8000"))
MAILBOX_KEY = os.getenv("AGENT_MAILBOX_KEY") or os.getenv("AGENTVERSE_API_KEY")

# In-memory storage for pending Human-in-the-Loop audit proposals per user
# Key: user_address/sender, Value: pending_plan dict
pending_audits: Dict[str, Dict[str, Any]] = {}

# Initialize Gmail Client & AI Classifier
gmail_client = GmailClient()
classifier = EmailClassifier()

# Initialize uAgent
agent_kwargs = {
    "name": AGENT_NAME,
    "seed": AGENT_SEED,
    "port": AGENT_PORT,
    "endpoint": [f"http://127.0.0.1:{AGENT_PORT}/submit"]
}

if MAILBOX_KEY and MAILBOX_KEY != "your_agentverse_mailbox_key_here" and MAILBOX_KEY != "your_agentverse_api_key_here":
    print(f"[+] Mailgent: Connecting with Agentverse Mailbox key...")
    agent_kwargs["mailbox"] = f"{MAILBOX_KEY}@https://agentverse.ai"
else:
    print("[*] Mailgent: Running locally (Set AGENT_MAILBOX_KEY in .env to link to Agentverse / ASI:One)")

agent = Agent(**agent_kwargs)

# Initialize Chat Protocol
chat_proto = Protocol(name=chat_protocol_spec.name, version=chat_protocol_spec.version)


def process_user_intent(sender: str, text: str) -> str:
    """
    Processes the user's chat message and coordinates the inbox workflow.
    Returns response text (Markdown formatted).
    """
    cmd = text.strip().lower()

    # 1. Audit / Scan Intent
    if any(k in cmd for k in ["audit", "scan", "check", "inbox", "emails", "find deadline", "start"]):
        print(f"[*] Mailgent: Processing AUDIT request from {sender}...")
        emails = gmail_client.fetch_recent_emails(max_results=50)
        if not emails:
            return "📬 Your inbox is empty or no emails could be fetched."

        analyzed_emails = classifier.classify_batch(emails)
        plan = extract_pending_plan(analyzed_emails)
        pending_audits[sender] = plan

        response_md = build_audit_summary_markdown(analyzed_emails, plan)
        return response_md

    # 2. Approval Intent
    elif any(k == cmd or cmd.startswith(k) for k in ["approve", "confirm", "yes", "execute", "apply", "do it"]):
        print(f"[*] Mailgent: Processing APPROVAL request from {sender}...")
        if sender not in pending_audits:
            return (
                "⚠️ **No pending audit found.**\n\n"
                "Please type `Audit my emails` first so I can scan your inbox and propose actions."
            )

        plan = pending_audits[sender]
        result = gmail_client.execute_audit_actions(
            job_message_ids=plan.get("job_ids", []),
            urgent_message_ids=plan.get("urgent_ids", []),
            archive_message_ids=plan.get("archive_ids", [])
        )

        # Clear pending plan
        del pending_audits[sender]

        return build_audit_success_markdown(result)

    # 3. Cancellation Intent
    elif any(k == cmd or cmd.startswith(k) for k in ["cancel", "discard", "no", "abort", "reject"]):
        print(f"[*] Mailgent: Processing CANCELLATION request from {sender}...")
        if sender in pending_audits:
            del pending_audits[sender]
            return "🛑 **Action proposal cancelled.** No changes were made to your Gmail inbox."
        return "ℹ️ There are no active action proposals to cancel."

    # 4. Help / Welcome / Unrecognized
    else:
        return (
            "👋 **Hi! I am Mailgent, your Autonomous Inbox Assistant.**\n\n"
            "Here is how I can help you stay on top of job applications and deadlines:\n\n"
            "* 🔍 **`Audit my emails`** — Scans recent emails, categorizes them, flags upcoming deadlines (< 48h), and prepares an action plan.\n"
            "* ✅ **`Approve`** — Labels job emails (`[Agent] Job`), highlights urgent items (`[Agent] Urgent`), and archives promotional clutter.\n"
            "* 🛑 **`Cancel`** — Discards pending proposals.\n\n"
            "*Type **`Audit`** to begin!*"
        )


@chat_proto.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handles incoming Agent Chat Protocol messages from ASI:One.
    """
    incoming_text = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            incoming_text += item.text + " "

    incoming_text = incoming_text.strip()
    ctx.logger.info(f"Received message from {sender}: '{incoming_text}'")

    # Generate response
    reply_text = process_user_intent(sender=sender, text=incoming_text)

    # Send response back via Chat Protocol
    response_msg = ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid.uuid4(),
        content=[TextContent(type="text", text=reply_text)]
    )
    await ctx.send(sender, response_msg)
    ctx.logger.info(f"Sent reply to {sender}")


agent.include(chat_proto)


# -------------------------------------------------------------------------
# Interactive CLI Simulator Mode
# -------------------------------------------------------------------------
def run_cli_simulator():
    """Simulates an interactive chat session with Mailgent from the terminal."""
    print("=" * 60)
    print("🤖 Mailgent Interactive Chat Simulator")
    print(f"[*] Agent Address: {agent.address}")
    print("=" * 60)
    print("Type commands like 'Audit', 'Approve', 'Cancel', or 'quit'\n")

    simulated_user = "user_simulator_001"

    while True:
        try:
            user_input = input("User 👤 > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\n[Exiting chat simulator...]")
                break

            response = process_user_intent(sender=simulated_user, text=user_input)
            print("\nMailgent 🤖 >")
            print(response)
            print("-" * 60 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\n[Exiting...]")
            break


if __name__ == "__main__":
    if "--cli" in sys.argv or "--test" in sys.argv:
        run_cli_simulator()
    else:
        print("=" * 60)
        print("🚀 Starting Mailgent Autonomous Agent...")
        print(f"[*] Agent Address: {agent.address}")
        print("=" * 60)
        agent.run()
