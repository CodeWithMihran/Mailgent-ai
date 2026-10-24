"""
gmail_tools.py
Handles all interactions with Gmail (Live API and Offline Fallback):
- Login & Service initialization
- Fetching recent emails with metadata and body snippet
- Label creation and resolution ([Agent] Job, [Agent] Urgent)
- Applying labels and archiving clutter (removing INBOX label)
- Dual-mode: automatically uses live Gmail when token.json is present,
  or gracefully falls back to sample_emails.json for offline testing.
"""

import os
import sys
import json
import base64
from email.message import EmailMessage
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def create_raw_email(sender: str, subject: str, body: str, date_str: Optional[str] = None) -> str:
    msg = EmailMessage()
    msg["To"] = sender
    msg["From"] = "me"
    msg["Subject"] = subject
    if date_str:
        msg["Date"] = date_str
    msg.set_content(body)
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

TOKEN_FILE = os.getenv("GMAIL_TOKEN_PATH", "token.json")
SAMPLE_EMAILS_FILE = os.getenv("SAMPLE_EMAILS_PATH", "sample_emails.json")
FORCE_SAMPLE = os.getenv("USE_SAMPLE_EMAILS", "false").lower() in ("true", "1", "yes")

# In-memory mock storage for offline mode modifications
_mock_inbox_state: Optional[List[Dict[str, Any]]] = None
_mock_labels: Dict[str, str] = {
    "INBOX": "INBOX",
    "UNREAD": "UNREAD"
}


class GmailClient:
    def __init__(self, token_file: str = TOKEN_FILE, force_sample: bool = FORCE_SAMPLE):
        self.token_file = token_file
        self.force_sample = force_sample
        self.is_offline = force_sample or not os.path.exists(token_file)
        self.service = None
        self._init_client()

    def _init_client(self):
        if not self.is_offline:
            try:
                creds = Credentials.from_authorized_user_file(self.token_file)
                self.service = build("gmail", "v1", credentials=creds)
                profile = self.service.users().getProfile(userId="me").execute()
                self.email_address = profile.get("emailAddress", "me")
                print(f"[+] GmailClient: Connected to live Gmail ({self.email_address})")
                return
            except Exception as e:
                print(f"[!] GmailClient: Failed to connect to live Gmail ({e}). Falling back to offline mode.")
                self.is_offline = True

        # Offline / Fallback mode
        self.email_address = "student.demo@university.edu (Offline/Mock Mode)"
        print(f"[*] GmailClient: Running in OFFLINE mode using '{SAMPLE_EMAILS_FILE}'")
        self._load_mock_data()

    def _load_mock_data(self):
        global _mock_inbox_state
        if _mock_inbox_state is None:
            if os.path.exists(SAMPLE_EMAILS_FILE):
                with open(SAMPLE_EMAILS_FILE, "r", encoding="utf-8") as f:
                    _mock_inbox_state = json.load(f)
            else:
                _mock_inbox_state = []
        return _mock_inbox_state

    # -------------------------------------------------------------------------
    # Fetching Emails
    # -------------------------------------------------------------------------
    def fetch_recent_emails(self, max_results: int = 50, query: str = "in:inbox") -> List[Dict[str, Any]]:
        """
        Fetches recent emails from INBOX or matching a search query with normalized metadata.
        Returns a list of dictionaries with keys:
          id, threadId, sender, subject, date, snippet, body, labels
        """
        if self.is_offline:
            mock_data = self._load_mock_data()
            if query and query != "in:inbox":
                q = query.lower().replace("in:inbox", "").strip()
                results = [
                    msg for msg in mock_data
                    if q in msg.get("subject", "").lower() 
                    or q in msg.get("sender", "").lower() 
                    or q in msg.get("snippet", "").lower()
                ][:max_results]
            else:
                results = [
                    msg for msg in mock_data 
                    if "INBOX" in msg.get("labels", [])
                ][:max_results]
            print(f"[+] GmailClient: Fetched {len(results)} emails from offline mock store.")
            return results

        # Live Gmail API fetch
        try:
            res = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            ).execute()
            messages = res.get("messages", [])
            if not messages:
                print("[*] GmailClient: No messages found matching query.")
                return []

            detailed_emails = []
            for m in messages:
                msg_data = self.service.users().messages().get(
                    userId="me",
                    id=m["id"],
                    format="full"
                ).execute()

                parsed = self._parse_gmail_message(msg_data)
                detailed_emails.append(parsed)

            print(f"[+] GmailClient: Fetched {len(detailed_emails)} emails from live Gmail.")
            return detailed_emails
        except Exception as e:
            print(f"[!] GmailClient: Error fetching emails: {e}")
            return []

    def _parse_gmail_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts sender, subject, date, and clean body text from Gmail API response."""
        payload = msg.get("payload", {})
        headers = payload.get("headers", [])

        header_dict = {h["name"].lower(): h["value"] for h in headers if "name" in h and "value" in h}
        sender = header_dict.get("from", "Unknown Sender")
        subject = header_dict.get("subject", "(No Subject)")
        date = header_dict.get("date", "")

        # Extract body text
        body_text = self._extract_body(payload)
        snippet = msg.get("snippet", "")

        return {
            "id": msg.get("id"),
            "threadId": msg.get("threadId"),
            "sender": sender,
            "subject": subject,
            "date": date,
            "snippet": snippet,
            "body": body_text if body_text else snippet,
            "labels": msg.get("labelIds", [])
        }

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Recursively parses payload parts to find plain text content."""
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                    return self._decode_base64url(part["body"]["data"])
                elif "parts" in part:
                    nested = self._extract_body(part)
                    if nested:
                        return nested

        # Single part message
        if "body" in payload and "data" in payload["body"]:
            return self._decode_base64url(payload["body"]["data"])

        return ""

    @staticmethod
    def _decode_base64url(data: str) -> str:
        try:
            return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="replace")
        except Exception:
            return ""

    # -------------------------------------------------------------------------
    # Label Management
    # -------------------------------------------------------------------------
    def get_or_create_label(self, label_name: str) -> str:
        """
        Retrieves the labelId for a given label name (e.g. '[Agent] Job').
        Creates the label if it does not already exist.
        """
        if self.is_offline:
            if label_name not in _mock_labels:
                _mock_labels[label_name] = f"LABEL_{len(_mock_labels) + 1}_{label_name.upper().replace(' ', '_')}"
                print(f"[+] GmailClient (Offline): Created mock label '{label_name}' (ID: {_mock_labels[label_name]})")
            return _mock_labels[label_name]

        try:
            # Check existing labels
            res = self.service.users().labels().list(userId="me").execute()
            labels = res.get("labels", [])
            for lbl in labels:
                if lbl["name"].lower() == label_name.lower():
                    return lbl["id"]

            # Label doesn't exist, create it
            label_body = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show"
            }
            new_label = self.service.users().labels().create(userId="me", body=label_body).execute()
            print(f"[+] GmailClient: Created new Gmail label '{label_name}' (ID: {new_label['id']})")
            return new_label["id"]
        except Exception as e:
            print(f"[!] GmailClient: Failed to get/create label '{label_name}': {e}")
            return label_name

    # -------------------------------------------------------------------------
    # Labeling & Archiving Actions
    # -------------------------------------------------------------------------
    def apply_labels(
        self,
        message_ids: List[str],
        add_label_names: Optional[List[str]] = None,
        remove_label_names: Optional[List[str]] = None
    ) -> int:
        """
        Applies label changes to a batch of messages.
        Returns the number of messages successfully modified.
        """
        if not message_ids:
            return 0

        add_label_names = add_label_names or []
        remove_label_names = remove_label_names or []

        if self.is_offline:
            mock_data = self._load_mock_data()
            modified = 0
            for msg in mock_data:
                if msg["id"] in message_ids:
                    current_labels = set(msg.get("labels", []))
                    current_labels.update(add_label_names)
                    for r in remove_label_names:
                        current_labels.discard(r)
                    msg["labels"] = list(current_labels)
                    modified += 1
            print(f"[+] GmailClient (Offline): Modified {modified} messages (+{add_label_names}, -{remove_label_names})")
            return modified

        # Resolve label IDs for live Gmail
        add_ids = [self.get_or_create_label(name) if name != "INBOX" else "INBOX" for name in add_label_names]
        remove_ids = [self.get_or_create_label(name) if name != "INBOX" else "INBOX" for name in remove_label_names]

        try:
            body = {
                "ids": message_ids,
                "addLabelIds": add_ids,
                "removeLabelIds": remove_ids
            }
            self.service.users().messages().batchModify(userId="me", body=body).execute()
            print(f"[+] GmailClient: Successfully modified {len(message_ids)} messages in Gmail.")
            return len(message_ids)
        except Exception as e:
            print(f"[!] GmailClient: batchModify failed: {e}. Falling back to sequential modify...")
            success = 0
            for mid in message_ids:
                try:
                    self.service.users().messages().modify(
                        userId="me",
                        id=mid,
                        body={"addLabelIds": add_ids, "removeLabelIds": remove_ids}
                    ).execute()
                    success += 1
                except Exception as inner_e:
                    print(f"  [!] Failed to modify {mid}: {inner_e}")
            return success

    def archive_emails(self, message_ids: List[str]) -> int:
        """Archives emails by removing the 'INBOX' label."""
        return self.apply_labels(message_ids=message_ids, remove_label_names=["INBOX"])

    # -------------------------------------------------------------------------
    # Account Profile & Status Metrics
    # -------------------------------------------------------------------------
    def get_account_profile(self) -> Dict[str, Any]:
        """Fetches live account statistics and label counts."""
        if self.is_offline:
            return {
                "email": "student.demo@university.edu (Offline Mock Mode)",
                "total_messages": len(_mock_inbox_state or []),
                "unread_messages": sum(1 for m in (_mock_inbox_state or []) if "UNREAD" in m.get("labels", [])),
                "mode": "offline"
            }

        try:
            profile = self.service.users().getProfile(userId="me").execute()
            return {
                "email": profile.get("emailAddress", "me"),
                "total_messages": profile.get("messagesTotal", 0),
                "threads_total": profile.get("threadsTotal", 0),
                "history_id": profile.get("historyId", "N/A"),
                "mode": "live"
            }
        except Exception as e:
            print(f"[!] Failed to get profile: {e}")
            return {
                "email": self.email_address,
                "error": str(e),
                "mode": "live"
            }

    # -------------------------------------------------------------------------
    # Creative Innovation: Ghosting Radar & Smart Follow-Up Drafter
    # -------------------------------------------------------------------------
    def create_followup_draft(self, to_email: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a professional follow-up email in the user's Gmail Drafts folder.
        The user can review and click 'Send' whenever ready.
        """
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        if self.is_offline:
            print(f"[+] GmailClient (Offline): Created Gmail Draft to <{to_email}>: '{subject}'")
            return {
                "id": f"draft_{len(_mock_inbox_state) + 1:03d}",
                "to": to_email,
                "subject": subject,
                "status": "created_offline"
            }

        try:
            raw_msg = create_raw_email(sender=to_email, subject=subject, body=body)
            draft_body = {
                "message": {
                    "raw": raw_msg
                }
            }
            if thread_id:
                draft_body["message"]["threadId"] = thread_id

            draft = self.service.users().drafts().create(userId="me", body=draft_body).execute()
            print(f"[+] GmailClient: Created live Gmail Draft (ID: {draft.get('id')}) to {to_email}")
            return {
                "id": draft.get("id"),
                "to": to_email,
                "subject": subject,
                "status": "created_live"
            }
        except Exception as e:
            print(f"[!] GmailClient: Failed to create draft: {e}")
            return {"error": str(e)}

    def execute_audit_actions(
        self,
        job_message_ids: List[str],
        urgent_message_ids: List[str],
        archive_message_ids: List[str],
        draft_followups: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes the full Human-in-the-Loop action package:
        1. Tags job/internship messages with '[Agent] Job'
        2. Tags urgent messages with '[Agent] Urgent'
        3. Archives clutter/promotions by removing 'INBOX'
        4. Auto-creates professional follow-up drafts for stalled/ghosted applications
        """
        print("=" * 60)
        print("[*] GmailClient: Executing approved inbox actions...")
        print("=" * 60)

        job_count = 0
        urgent_count = 0
        archive_count = 0
        drafts_count = 0

        if job_message_ids:
            job_count = self.apply_labels(
                message_ids=job_message_ids,
                add_label_names=["[Agent] Job"]
            )

        if urgent_message_ids:
            urgent_count = self.apply_labels(
                message_ids=urgent_message_ids,
                add_label_names=["[Agent] Urgent"]
            )

        if archive_message_ids:
            archive_count = self.archive_emails(message_ids=archive_message_ids)

        if draft_followups:
            for d in draft_followups:
                res = self.create_followup_draft(
                    to_email=d.get("to", ""),
                    subject=d.get("subject", ""),
                    body=d.get("body", ""),
                    thread_id=d.get("threadId")
                )
                if "error" not in res:
                    drafts_count += 1

        summary = {
            "job_labeled": job_count,
            "urgent_labeled": urgent_count,
            "archived_promotions": archive_count,
            "drafts_created": drafts_count,
            "total_actions": job_count + urgent_count + archive_count + drafts_count,
            "mode": "offline" if self.is_offline else "live"
        }

        print(f"[SUCCESS] Audit actions executed successfully:")
        print(f"  - Job emails labeled: {summary['job_labeled']}")
        print(f"  - Urgent emails labeled: {summary['urgent_labeled']}")
        print(f"  - Clutter archived: {summary['archived_promotions']}")
        print(f"  - Follow-up drafts prepared: {summary['drafts_created']}")
        print("=" * 60)
        return summary


# -------------------------------------------------------------------------
# Self-Test Script (Phase 3 Deliverable)
# -------------------------------------------------------------------------
def test_gmail_tools():
    print("=" * 60)
    print("[*] Testing gmail_tools.py (Phase 3 Self-Test)")
    print("=" * 60)

    client = GmailClient()
    print(f"[*] Account: {client.email_address}")
    print(f"[*] Mode: {'OFFLINE (Mock)' if client.is_offline else 'LIVE (Gmail API)'}")

    # 1. Fetch recent emails
    print("\n--- Test 1: Fetching recent emails ---")
    emails = client.fetch_recent_emails(max_results=10)
    assert len(emails) > 0, "Failed to fetch any emails!"
    print(f"[PASS] Successfully fetched {len(emails)} emails.")
    print(f"       First email: [{emails[0]['sender']}] {emails[0]['subject']}")

    # 2. Label Resolution / Creation
    print("\n--- Test 2: Label resolution and creation ---")
    job_label_id = client.get_or_create_label("[Agent] Job")
    urgent_label_id = client.get_or_create_label("[Agent] Urgent")
    assert job_label_id, "Failed to obtain [Agent] Job label ID"
    assert urgent_label_id, "Failed to obtain [Agent] Urgent label ID"
    print(f"[PASS] [Agent] Job Label ID: {job_label_id}")
    print(f"[PASS] [Agent] Urgent Label ID: {urgent_label_id}")

    # 3. Labeling and Archiving Action Execution
    print("\n--- Test 3: Action Execution (Label & Archive) ---")
    test_job_ids = [emails[0]["id"]]
    test_urgent_ids = [emails[1]["id"]]
    test_archive_ids = [emails[2]["id"]]

    result = client.execute_audit_actions(
        job_message_ids=test_job_ids,
        urgent_message_ids=test_urgent_ids,
        archive_message_ids=test_archive_ids
    )

    assert result["job_labeled"] == 1, "Expected 1 job email labeled"
    assert result["urgent_labeled"] == 1, "Expected 1 urgent email labeled"
    assert result["archived_promotions"] == 1, "Expected 1 email archived"

    print(f"\n[PASS] All Phase 3 checks passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_gmail_tools()
