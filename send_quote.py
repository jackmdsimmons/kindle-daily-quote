#!/usr/bin/env python3
"""
Daily Kindle quote emailer.
Picks a random highlight (min 40 chars) and sends it via Resend.

Env vars required:
  RESEND_API_KEY   — from resend.com
  TO_EMAIL         — your email address
"""
import csv
import os
import random
import urllib.request
import urllib.error
import json

HIGHLIGHTS_FILE = os.path.join(os.path.dirname(__file__), "kindle_highlights.csv")
MIN_LENGTH = 40  # skip single words / very short clips


def load_highlights():
    with open(HIGHLIGHTS_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            row for row in reader
            if row.get("Highlight") and len(row["Highlight"].strip()) >= MIN_LENGTH
        ]


def send_email(api_key: str, to: str, highlight: dict):
    text = highlight["Highlight"].strip()
    book = highlight.get("Book Title", "").strip()
    author = highlight.get("Author", "").strip()

    subject = f"📖 {book}" if book else "📖 Your daily Kindle quote"

    attribution = ""
    if book and author:
        attribution = f"<p style='margin-top:24px;color:#888;font-size:13px'>— {book} · {author}</p>"
    elif book:
        attribution = f"<p style='margin-top:24px;color:#888;font-size:13px'>— {book}</p>"

    html = f"""
    <div style="font-family:Georgia,serif;max-width:560px;margin:40px auto;padding:0 20px;color:#1a1a1a">
      <p style="font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:#aaa;margin-bottom:28px">
        Your Kindle highlight
      </p>
      <blockquote style="border-left:3px solid #d4a843;margin:0;padding:0 0 0 20px">
        <p style="font-size:18px;line-height:1.7;margin:0">{text}</p>
      </blockquote>
      {attribution}
    </div>
    """

    payload = json.dumps({
        "from": "Kindle Quotes <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "html": html,
    }).encode()

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"Sent: {result.get('id')}  |  {book} — {text[:60]}…")


def main():
    api_key = os.environ.get("RESEND_API_KEY")
    to_email = os.environ.get("TO_EMAIL")

    if not api_key or not to_email:
        raise RuntimeError("Set RESEND_API_KEY and TO_EMAIL environment variables.")

    highlights = load_highlights()
    if not highlights:
        raise RuntimeError("No highlights found in CSV.")

    pick = random.choice(highlights)
    send_email(api_key, to_email, pick)


if __name__ == "__main__":
    main()
