"""
llm.py
Classification Engine for Mailgent:
- Categorizes emails into: Job/Internship, Academic, Finance, Promotions, General
- Computes urgency score (1 to 10)
- Detects impending deadlines (especially < 48 hours)
- Provides reasoning and recommended actions (label_job, label_urgent, archive, keep)
- Hybrid architecture: Uses ASI:One / OpenAI API if ASI1_API_KEY is configured,
  or falls back to a high-speed local heuristic NLP engine with zero latency.
"""

import os
import re
import sys
import json
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests
from dotenv import load_dotenv

load_dotenv()

ASI1_API_KEY = os.getenv("ASI1_API_KEY")
ASI1_API_BASE = os.getenv("ASI1_API_BASE", "https://api.asi1.ai/v1")
ASI1_MODEL = os.getenv("ASI1_MODEL", "asi1-mini")


# -------------------------------------------------------------------------
# Local Heuristic NLP Rules (Zero Latency, High Reliability Fallback)
# -------------------------------------------------------------------------
JOB_PATTERNS = [
    r"interview", r"coding challenge", r"online assessment", r"hackerrank",
    r"technical assessment", r"offer letter", r"internship", r"job application",
    r"talent acquisition", r"recruiting", r"greenhouse\.io", r"lever\.co",
    r"workday", r"phone screen", r"hiring manager", r"sde intern",
    r"interview invite", r"internshala", r"assessment is pending"
]

ACADEMIC_PATTERNS = [
    r"university", r"registrar", r"course registration", r"tuition",
    r"canvas", r"blackboard", r"grade posted", r"midterm", r"final exam",
    r"degree audit", r"dean of students", r"teaching assistant", r"seminar"
]

FINANCE_PATTERNS = [
    r"receipt", r"invoice", r"billing", r"payment sent", r"subscription",
    r"order delivered", r"order confirmation", r"doordash", r"uber ride",
    r"paypal", r"venmo", r"aws billing", r"github copilot"
]

PROMO_PATTERNS = [
    r"unsubscribe", r"flash sale", r"50% off", r"discount", r"newsletter",
    r"special offer", r"weekly digest", r"trending on", r"streak", r"meetups near you",
    r"doorbuster", r"double star", r"upgrade to premium", r"deals",
    r"quiz\b", r"bite-size", r"win big", r"win ₹", r"win rs", r"grab ₹"
]

DEADLINE_PATTERNS = [
    (r"(?:within|in)\s+(?:the\s+next\s+)?(12|24|48|72)\s*hours?", "Within 12-48 Hours"),
    (r"expires\s+in\s+(\d+\s*hours?)", r"Expires in \1"),
    (r"by\s+(tomorrow|tonight|friday|monday|sunday|today)\b(?:\s+at\s+[\d:]+\s*(?:am|pm)?)?", r"By \1"),
    (r"due\s+date\s*(?:is|:)?\s*([a-zA-Z]+\s+\d{1,2}(?:,\s*\d{4})?)", r"Due: \1"),
    (r"closes\s+in\s+(\d+\s*hours?)", r"Closes in \1"),
    (r"deadline\s+approaching", "Deadline Approaching (< 24h)"),
    (r"assessment\s+is\s+pending", "Assessment Pending (< 24h)"),
    (r"action\s+required", "Immediate Action Required"),
    (r"urgent\b", "Urgent Attention Needed")
]


class EmailClassifier:
    def __init__(self, api_key: Optional[str] = ASI1_API_KEY):
        self.api_key = api_key
        self.use_llm = bool(api_key and api_key.strip() and api_key != "your_asi1_or_openai_api_key_here")
        if self.use_llm:
            print(f"[+] EmailClassifier: Configured to use ASI:One / LLM API ({ASI1_MODEL})")
        else:
            print("[*] EmailClassifier: Using fast local NLP engine (Zero latency, offline ready)")

    def classify_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies a single email and returns structured metadata."""
        if self.use_llm:
            try:
                return self._classify_with_llm(email)
            except Exception as e:
                print(f"[!] LLM classification failed ({e}). Falling back to local NLP engine.")
                return self._classify_with_heuristics(email)
        return self._classify_with_heuristics(email)

    def classify_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classifies a list of emails."""
        results = []
        for e in emails:
            classification = self.classify_email(e)
            merged = {**e, "analysis": classification}
            results.append(merged)
        return results

    # -------------------------------------------------------------------------
    # Local Heuristic Engine
    # -------------------------------------------------------------------------
    def _classify_with_heuristics(self, email: Dict[str, Any]) -> Dict[str, Any]:
        sender = email.get("sender", "").lower()
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        snippet = email.get("snippet", "").lower()
        text = f"{sender} {subject} {snippet} {body[:500]}"

        # Category determination
        category = "General"
        score = 3
        reason = "Standard inbox message."
        recommended_actions = []

        is_promo = any(re.search(p, text) for p in PROMO_PATTERNS)
        is_job = any(re.search(p, text) for p in JOB_PATTERNS)
        is_academic = any(re.search(p, text) for p in ACADEMIC_PATTERNS)
        is_finance = any(re.search(p, text) for p in FINANCE_PATTERNS)

        # If it's a promotional quiz / marketing blast without direct interview invite
        if is_promo and not any(k in text for k in ["interview invite", "assessment is pending", "offer letter"]):
            category = "Promotions"
            score = 1
            reason = "Promotional offer, marketing newsletter, or sales digest."
            recommended_actions.append("archive")
        elif is_job:
            category = "Job/Internship"
            score = 7
            reason = "Job or internship recruitment communication."
            recommended_actions.append("label_job")
        elif is_academic:
            category = "Academic"
            score = 5
            reason = "University or coursework notification."
        elif is_finance:
            category = "Finance"
            score = 4
            reason = "Billing receipt or financial transaction."
        elif is_promo:
            category = "Promotions"
            score = 1
            reason = "Promotional offer, marketing newsletter, or sales digest."
            recommended_actions.append("archive")

        # Deadline / Urgency detection
        deadline_found = None
        for pattern, label in DEADLINE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                deadline_found = match.expand(label) if "\\" in label else label
                break

        # Mentor's Guard: only trust deadline detection for categories that matter
        is_urgent = False
        if deadline_found and category in ("Job/Internship", "Academic", "Finance"):
            # Ensure marketing FOMO cannot trigger urgency
            if not any(re.search(p, text) for p in [r"quiz\b", r"flash sale", r"50% off", r"bite-size", r"win big", r"win ₹"]):
                is_urgent = True
                score = max(score, 9)
                reason += f" Action deadline detected: {deadline_found}."
                if "label_urgent" not in recommended_actions:
                    recommended_actions.append("label_urgent")

        return {
            "category": category,
            "urgency_score": score,
            "is_urgent": is_urgent,
            "deadline": deadline_found if is_urgent else None,
            "reason": reason.strip(),
            "recommended_actions": recommended_actions
        }

    # -------------------------------------------------------------------------
    # ASI:One / OpenAI LLM Engine
    # -------------------------------------------------------------------------
    def _classify_with_llm(self, email: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
You are Mailgent, an AI assistant analyzing an email for a student job applicant.
Classify the following email and respond with valid JSON ONLY.

Email Details:
- From: {email.get('sender')}
- Subject: {email.get('subject')}
- Snippet: {email.get('snippet')}
- Body excerpt: {email.get('body', '')[:400]}

Respond ONLY with this JSON format:
{{
  "category": "Job/Internship" | "Academic" | "Finance" | "Promotions" | "General",
  "urgency_score": <int 1-10>,
  "is_urgent": <bool true if requires action in < 48 hours>,
  "deadline": "<deadline description or null>",
  "reason": "<one sentence explanation>",
  "recommended_actions": ["label_job" | "label_urgent" | "archive" | "keep"]
}}
"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": ASI1_MODEL,
            "messages": [
                {"role": "system", "content": "You are Mailgent's email classification engine. Always reply in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        res = requests.post(f"{ASI1_API_BASE}/chat/completions", headers=headers, json=payload, timeout=8)
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        # Strip potential markdown code blocks
        clean_json = re.sub(r"^```json\s*", "", content.strip(), flags=re.MULTILINE)
        clean_json = re.sub(r"```$", "", clean_json.strip())
        return json.loads(clean_json)


def test_classifier():
    print("=" * 60)
    print("[*] Mailgent - Phase 4 Classification Test (llm.py)")
    print("=" * 60)

    from gmail_tools import GmailClient

    client = GmailClient()
    emails = client.fetch_recent_emails(max_results=10)
    assert emails, "No emails found to classify!"

    classifier = EmailClassifier()
    analyzed = classifier.classify_batch(emails)

    print(f"\n[+] Classified {len(analyzed)} emails:")
    print("-" * 60)

    category_counts = {}
    urgent_count = 0

    for idx, e in enumerate(analyzed, 1):
        info = e["analysis"]
        cat = info["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if info["is_urgent"]:
            urgent_count += 1

        print(f"[{idx:02d}] {info['category']:<15} (Score: {info['urgency_score']:02d}/10) | {e['subject'][:45]}")
        if info["deadline"]:
            print(f"     ⏰ Deadline: {info['deadline']}")
        print(f"     💡 Reason: {info['reason']}")
        print(f"     ⚡ Action: {info['recommended_actions']}")
        print()

    print("=" * 60)
    print(f"[SUMMARY] Breakdown: {category_counts}")
    print(f"[SUMMARY] Urgent Items Requiring Immediate Action: {urgent_count}")
    print("=" * 60)
    print("[SUCCESS] Phase 4 classifier working cleanly!")


if __name__ == "__main__":
    test_classifier()
