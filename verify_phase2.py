"""
verify_phase2.py
Automated validation script for Phase 1 & Phase 2.
Checks packages, sample emails, credentials status, and environment configuration.
"""

import os
import sys
import json

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def check_dependencies():
    print("[1/4] Checking Python libraries...")
    required_modules = [
        ("uagents", "uagents"),
        ("uagents_core", "uagents_core"),
        ("googleapiclient", "google-api-python-client"),
        ("google_auth_oauthlib", "google-auth-oauthlib"),
        ("dotenv", "python-dotenv"),
        ("pydantic", "pydantic"),
        ("requests", "requests")
    ]
    all_ok = True
    for mod_name, pkg_name in required_modules:
        try:
            __import__(mod_name)
            print(f"  [+] {pkg_name}: OK")
        except ImportError:
            print(f"  [!] {pkg_name}: MISSING")
            all_ok = False
    return all_ok


def check_sample_emails():
    print("\n[2/4] Validating sample_emails.json...")
    path = "sample_emails.json"
    if not os.path.exists(path):
        print("  [!] sample_emails.json does not exist.")
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            emails = json.load(f)

        if not isinstance(emails, list):
            print("  [!] sample_emails.json root is not a list.")
            return False

        print(f"  [+] Total emails loaded: {len(emails)}")
        if len(emails) < 50:
            print(f"  [!] Expected at least 50 emails, found {len(emails)}")
            return False

        # Validate required schema fields on first 5 entries
        for idx, email in enumerate(emails[:5]):
            for field in ["id", "sender", "subject", "snippet", "body", "labels"]:
                if field not in email:
                    print(f"  [!] Email #{idx} missing field: {field}")
                    return False

        # Count emails containing urgent deadline keywords
        urgent_keywords = ["deadline", "expires", "urgent", "action required", "48 hours", "24 hours"]
        urgent_count = sum(
            1 for e in emails 
            if any(k in (e["subject"] + " " + e["body"]).lower() for k in urgent_keywords)
        )
        print(f"  [+] Detected {urgent_count} emails containing urgent/action deadline markers.")
        return True
    except Exception as e:
        print(f"  [!] Failed to parse sample_emails.json: {e}")
        return False


def check_google_auth():
    print("\n[3/4] Checking Google OAuth credentials & token...")
    has_creds = os.path.exists("credentials.json")
    has_token = os.path.exists("token.json")

    print(f"  [{'+' if has_creds else '!'}] credentials.json: {'PRESENT' if has_creds else 'NOT YET PLACED'}")
    print(f"  [{'+' if has_token else '!'}] token.json: {'GENERATED' if has_token else 'NOT YET GENERATED'}")

    if has_token:
        print("  [+] Ready for live Gmail operations!")
    elif has_creds:
        print("  [*] credentials.json detected! Run 'python auth_once.py' to generate token.json.")
    else:
        print("  [*] Offline fallback mode ready via sample_emails.json (or add credentials.json for live Gmail).")
    return True


def check_environment():
    print("\n[4/4] Checking project scaffolding...")
    files = [".env.example", ".gitignore", "auth_once.py", "seed_inbox.py", "requirements.txt"]
    for f in files:
        status = "OK" if os.path.exists(f) else "MISSING"
        print(f"  [{'+' if status == 'OK' else '!'}] {f}: {status}")
    return True


def main():
    print("=" * 60)
    print("[*] Mailgent - Phase 1 & 2 Verification Suite")
    print("=" * 60)
    d_ok = check_dependencies()
    s_ok = check_sample_emails()
    g_ok = check_google_auth()
    e_ok = check_environment()

    print("\n" + "=" * 60)
    if d_ok and s_ok and e_ok:
        print("[SUCCESS] Phase 1 & Phase 2 verification PASSED!")
        print("=" * 60)
    else:
        print("[!] Verification found issues. Please review output above.")
        print("=" * 60)


if __name__ == "__main__":
    main()
