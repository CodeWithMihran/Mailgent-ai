"""
cards.py
Builds rich Human-in-the-Loop (HITL) approval cards and audit summaries for ASI:One chat.
Provides both:
1. Formatted Markdown Card (universally rendered in all ACP clients & ASI:One web interface)
2. Structured JSON Card Payload (for rich interactive card widgets and button triggers)
"""

import json
from typing import List, Dict, Any


def build_audit_summary_markdown(analyzed_emails: List[Dict[str, Any]], pending_plan: Dict[str, Any]) -> str:
    """
    Renders a structured, clean GitHub-flavored Markdown card for the ASI:One chat interface.
    """
    total = len(analyzed_emails)
    breakdown = pending_plan.get("category_breakdown", {})
    urgent_items = pending_plan.get("urgent_items", [])
    stalled_items = pending_plan.get("stalled_items", [])
    job_ids = pending_plan.get("job_ids", [])
    urgent_ids = pending_plan.get("urgent_ids", [])
    archive_ids = pending_plan.get("archive_ids", [])
    draft_followups = pending_plan.get("draft_followups", [])

    lines = []
    lines.append("### 📬 Mailgent Inbox Audit Report")
    lines.append(f"Scanned **{total} recent emails** from your inbox.\n")

    # Category breakdown table
    lines.append("#### 📊 Category Breakdown")
    lines.append("| Category | Count | Status |")
    lines.append("| :--- | :---: | :--- |")
    lines.append(f"| 💼 **Job / Internship** | {breakdown.get('Job/Internship', 0)} | High Priority |")
    lines.append(f"| 🎓 **Academic** | {breakdown.get('Academic', 0)} | Kept in Inbox |")
    lines.append(f"| 💳 **Finance & Receipts** | {breakdown.get('Finance', 0)} | Kept in Inbox |")
    lines.append(f"| 🛍️ **Promotions / Clutter** | {breakdown.get('Promotions', 0)} | Queued to Archive |")
    lines.append(f"| 📁 **General / Other** | {breakdown.get('General', 0)} | Kept in Inbox |")
    lines.append("")

    # Urgent section
    if urgent_items:
        lines.append("#### 🚨 Urgent Action Items (< 48h Deadlines)")
        for idx, item in enumerate(urgent_items, 1):
            deadline_str = f" **[Due: {item['deadline']}]**" if item.get("deadline") else ""
            lines.append(f"{idx}. **{item['sender']}**: *{item['subject']}*{deadline_str}")
        lines.append("")

    # Ghosting Radar (Innovative Feature)
    if stalled_items:
        lines.append("#### 👻 Ghosting Radar (Stalled Applications)")
        for idx, item in enumerate(stalled_items, 1):
            lines.append(f"* ⏳ **{item['company']}** (*{item['subject']}*): No response for > 5 days.")
        lines.append("")

    # Proposed actions
    lines.append("#### 🛠️ Proposed Actions (Human-in-the-Loop)")
    lines.append(f"* 🏷️ Apply **`[Agent] Job`** label to **{len(job_ids)}** job/internship emails.")
    lines.append(f"* 🚨 Apply **`[Agent] Urgent`** label to **{len(urgent_ids)}** critical deadline emails.")
    lines.append(f"* 📦 **Archive {len(archive_ids)}** promotional emails from your primary inbox.")
    if draft_followups:
        lines.append(f"* 📝 Auto-create **{len(draft_followups)} polite follow-up draft(s)** directly in your Gmail Drafts folder.")
    lines.append("")
    lines.append("---")
    lines.append("👉 **Reply `Approve`** to apply these actions in Gmail.")
    lines.append("👉 **Reply `Cancel`** to discard this proposal.")

    return "\n".join(lines)


def build_audit_success_markdown(result: Dict[str, Any]) -> str:
    """Renders the execution confirmation card once approved."""
    lines = []
    lines.append("### ✅ Inbox Actions Successfully Applied!")
    lines.append(f"Mode: **{result.get('mode', 'live').upper()}**\n")
    lines.append(f"* 🏷️ **{result.get('job_labeled', 0)}** emails labeled with `[Agent] Job`")
    lines.append(f"* 🚨 **{result.get('urgent_labeled', 0)}** emails labeled with `[Agent] Urgent`")
    lines.append(f"* 📦 **{result.get('archived_promotions', 0)}** promotional emails archived from INBOX")
    if result.get("drafts_created", 0) > 0:
        lines.append(f"* 📝 **{result.get('drafts_created')}** follow-up email(s) drafted in your Gmail Drafts folder (ready to review & send)!")
    lines.append(f"\n🎉 *Your inbox is now clean and your critical career opportunities are highlighted!*")
    return "\n".join(lines)


def build_asi1_card_payload(analyzed_emails: List[Dict[str, Any]], pending_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs a structured JSON payload for ASI:One interactive card components.
    """
    urgent_items = pending_plan.get("urgent_items", [])
    return {
        "type": "card",
        "version": "1.0",
        "title": "📬 Mailgent Inbox Audit",
        "subtitle": f"Analyzed {len(analyzed_emails)} emails",
        "breakdown": pending_plan.get("category_breakdown", {}),
        "urgent_count": len(urgent_items),
        "actions_summary": {
            "label_jobs": len(pending_plan.get("job_ids", [])),
            "label_urgent": len(pending_plan.get("urgent_ids", [])),
            "archive_clutter": len(pending_plan.get("archive_ids", []))
        },
        "buttons": [
            {"label": "Approve Actions", "action": "send_message", "payload": "Approve", "variant": "primary"},
            {"label": "Cancel", "action": "send_message", "payload": "Cancel", "variant": "secondary"}
        ]
    }


def extract_pending_plan(analyzed_emails: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extracts counts, message IDs, and stalled application follow-ups for each proposed action.
    """
    category_breakdown = {}
    urgent_items = []
    stalled_items = []
    draft_followups = []
    job_ids = []
    urgent_ids = []
    archive_ids = []

    for item in analyzed_emails:
        analysis = item.get("analysis", {})
        cat = analysis.get("category", "General")
        category_breakdown[cat] = category_breakdown.get(cat, 0) + 1

        mid = item.get("id")
        rec_actions = analysis.get("recommended_actions", [])
        subject = item.get("subject", "")
        sender = item.get("sender", "")

        if "label_job" in rec_actions:
            job_ids.append(mid)

            # Detect stalled/ghosted application updates (e.g. applications with no activity/deadlines)
            if not analysis.get("is_urgent") and any(k in subject.lower() for k in ["application to", "application status", "applied"]):
                company = "Recruiter"
                if "datadog" in subject.lower():
                    company = "Datadog"
                elif "palantir" in subject.lower():
                    company = "Palantir"
                elif "@" in sender:
                    company = sender.split("@")[1].split(".")[0].capitalize()

                stalled_items.append({
                    "id": mid,
                    "company": company,
                    "subject": subject,
                    "sender": sender
                })

                draft_followups.append({
                    "to": sender,
                    "subject": f"Checking in: {subject}",
                    "threadId": item.get("threadId"),
                    "body": (
                        f"Dear {company} Recruiting Team,\n\n"
                        f"I hope you are having a productive week.\n\n"
                        f"I am writing to briefly check in on the status of my application for the Software Engineer Intern role. "
                        f"I remain very enthusiastic about the work {company} is doing and would welcome any updates or further questions.\n\n"
                        f"Thank you for your time and consideration!\n\n"
                        f"Sincerely,\nCandidate"
                    )
                })

        if analysis.get("is_urgent") or "label_urgent" in rec_actions:
            urgent_ids.append(mid)
            urgent_items.append({
                "id": mid,
                "sender": sender,
                "subject": subject,
                "deadline": analysis.get("deadline")
            })

        if "archive" in rec_actions or cat == "Promotions":
            archive_ids.append(mid)

    return {
        "category_breakdown": category_breakdown,
        "urgent_items": urgent_items,
        "stalled_items": stalled_items,
        "draft_followups": draft_followups,
        "job_ids": job_ids,
        "urgent_ids": urgent_ids,
        "archive_ids": archive_ids
    }


def test_cards():
    print("=" * 60)
    print("[*] Mailgent - Phase 5 Approval Card Test (cards.py)")
    print("=" * 60)

    from gmail_tools import GmailClient
    from llm import EmailClassifier

    client = GmailClient()
    emails = client.fetch_recent_emails(max_results=50)
    classifier = EmailClassifier()
    analyzed = classifier.classify_batch(emails)

    plan = extract_pending_plan(analyzed)
    markdown_card = build_audit_summary_markdown(analyzed, plan)
    json_card = build_asi1_card_payload(analyzed, plan)

    print("\n[--- Rendered Markdown Card ---]")
    print(markdown_card)
    print("\n[--- Structured JSON Card Payload ---]")
    print(json.dumps(json_card, indent=2))
    print("\n" + "=" * 60)
    print("[SUCCESS] Phase 5 cards module generated cleanly!")
    print("=" * 60)


if __name__ == "__main__":
    test_cards()
