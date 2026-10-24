"""
seed_inbox.py
Injects the 50 realistic emails from sample_emails.json directly into your
test Gmail inbox via Gmail API users().messages().insert().

Usage:
  .\\venv\\Scripts\\python.exe seed_inbox.py [--dry-run] [--limit 10]
"""

import os
import sys
import json
import time
import base64
from email.message import EmailMessage

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = os.getenv("GMAIL_TOKEN_PATH", "token.json")
SAMPLE_EMAILS_FILE = "sample_emails.json"


def get_gmail_service():
    if not os.path.exists(TOKEN_FILE):
        print(f"[!] Error: '{TOKEN_FILE}' not found.")
        print("    Please run 'auth_once.py' first to authenticate.")
        return None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE)
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        print(f"[!] Failed to load credentials from '{TOKEN_FILE}': {e}")
        return None


def create_raw_email(sender, subject, body, date_str=None):
    msg = EmailMessage()
    msg["To"] = "me"
    msg["From"] = sender
    msg["Subject"] = subject
    if date_str:
        msg["Date"] = date_str
    msg.set_content(body)
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")


def seed_inbox(dry_run=False, limit=None):
    if not os.path.exists(SAMPLE_EMAILS_FILE):
        print(f"[!] '{SAMPLE_EMAILS_FILE}' not found!")
        return

    with open(SAMPLE_EMAILS_FILE, "r", encoding="utf-8") as f:
        emails = json.load(f)

    if limit and limit > 0:
        emails = emails[:limit]

    print("=" * 60)
    print(f"[*] Mailgent - Seeding Demo Inbox ({len(emails)} emails)")
    print(f"[*] Dry run mode: {dry_run}")
    print("=" * 60)

    if dry_run:
        print("[INFO] Dry run enabled. Inspecting sample messages:")
        for idx, item in enumerate(emails, 1):
            print(f"  {idx:02d}. [{item['sender']}] {item['subject'][:55]}...")
        print("=" * 60)
        print("[SUCCESS] Dry run completed without modifying Gmail.")
        return

    service = get_gmail_service()
    if not service:
        sys.exit(1)

    profile = service.users().getProfile(userId="me").execute()
    print(f"[+] Connected to Gmail account: {profile.get('emailAddress')}")
    print("[*] Inserting emails into INBOX...")

    success_count = 0
    for idx, item in enumerate(emails, 1):
        try:
            raw_msg = create_raw_email(
                sender=item["sender"],
                subject=item["subject"],
                body=item["body"]
            )
            labels = item.get("labels", ["INBOX", "UNREAD"])
            
            # Insert message directly without triggering spam filters
            service.users().messages().insert(
                userId="me",
                body={"raw": raw_msg, "labelIds": labels}
            ).execute()

            print(f"  [{idx:02d}/{len(emails):02d}] Inserted: {item['subject'][:50]}...")
            success_count += 1
            # Slight sleep to avoid exceeding Gmail API rate limits
            time.sleep(0.3)
        except Exception as e:
            print(f"  [!] Failed to insert message {idx}: {e}")

    print("=" * 60)
    print(f"[SUCCESS] Finished! Inserted {success_count}/{len(emails)} emails into INBOX.")
    print("=" * 60)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    limit = None
    for arg in sys.argv:
        if arg.startswith("--limit="):
            limit = int(arg.split("=")[1])
    seed_inbox(dry_run=dry_run, limit=limit)
