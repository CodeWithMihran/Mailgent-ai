"""
auth_once.py
Run once to authenticate with Google OAuth 2.0 and save token.json for headless execution.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail modify scope allows reading messages, modifying labels, and archiving
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
TOKEN_FILE = os.getenv("GMAIL_TOKEN_PATH", "token.json")


def authenticate_gmail():
    print("=" * 60)
    print("[*] Mailgent - Gmail OAuth 2.0 Setup")
    print("=" * 60)

    creds = None
    # Check if token.json already exists
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            print(f"[*] Found existing token in '{TOKEN_FILE}'")
        except Exception as e:
            print(f"[!] Existing token is invalid or corrupted: {e}")
            creds = None

    # If there are no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[*] Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("[+] Token refreshed successfully!")
            except Exception as e:
                print(f"[!] Token refresh failed: {e}. Re-authenticating...")
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"\n[ERROR] '{CREDENTIALS_FILE}' not found in current directory!")
                print("\nPlease follow these steps to obtain credentials.json:")
                print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
                print("2. Create a new project (e.g. 'Mailgent-Agent').")
                print("3. Enable the 'Gmail API' under APIs & Services > Library.")
                print("4. Configure the OAuth Consent Screen (User Type: External, add your email as Test User).")
                print("5. Go to Credentials > Create Credentials > OAuth client ID.")
                print("   - Application type: Desktop app")
                print("   - Name: Mailgent Desktop Client")
                print("6. Download the JSON file and rename it to 'credentials.json' in this folder.")
                print("=" * 60)
                sys.exit(1)

            print(f"[*] Starting OAuth 2.0 flow using '{CREDENTIALS_FILE}'...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future runs
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
        print(f"[+] Credentials saved to '{TOKEN_FILE}'")

    # Verify connection by fetching user profile
    try:
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        email_address = profile.get("emailAddress", "Unknown")
        total_messages = profile.get("messagesTotal", 0)
        print("\n" + "=" * 60)
        print(f"[SUCCESS] Successfully connected to Gmail!")
        print(f"   Account: {email_address}")
        print(f"   Total Messages in Account: {total_messages}")
        print(f"   Token ready at: {os.path.abspath(TOKEN_FILE)}")
        print("=" * 60)
    except Exception as e:
        print(f"[!] Connected, but failed to fetch profile: {e}")


if __name__ == "__main__":
    authenticate_gmail()
