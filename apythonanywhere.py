import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────
#  FILL THESE IN BEFORE RUNNING
# ─────────────────────────────────────────
RECIPIENT_EMAIL = "ibteshamakhtar1@gmail.com"       # Email where you want alerts
SENDER_EMAIL    = "ibteshamakhtar1@gmail.com"  # Your Gmail address
SENDER_PASSWORD = "ceoz iosj jdji hmvq"  # Gmail App Password (16 chars)
# ─────────────────────────────────────────

URL = "https://meghalaya.gov.in/recruitment"

def scrape_posts():
    """Scrape all recruitment posts from the page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    }
    posts = []
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Each list item has a link and a date line
        for item in soup.select("ul li, .view-content li"):
            link = item.find("a", href=True)
            text = item.get_text(separator=" ", strip=True)

            # Look for date pattern like "Date: 20 Apr 2026"
            if link and "Date:" in text:
                date_str = ""
                for part in text.split("Date:"):
                    if len(part.strip()) >= 11:
                        date_str = part.strip()[:11].strip()
                        break

                if date_str:
                    href = link["href"]
                    if not href.startswith("http"):
                        href = "https://meghalaya.gov.in" + href
                    posts.append({
                        "title": link.get_text(strip=True),
                        "url":   href,
                        "date":  date_str
                    })
    except Exception as e:
        print(f"Error scraping page: {e}")

    return posts


def check_today(posts):
    """Filter posts that were posted today."""
    today = datetime.now().strftime("%d %b %Y")   # e.g. "21 Apr 2026"
    return [p for p in posts if p["date"] == today]


def send_email(new_posts):
    """Send an alert email with today's new posts."""
    today_str = datetime.now().strftime("%d %B %Y")
    subject = f"[Alert] {len(new_posts)} new Meghalaya recruitment post(s) — {today_str}"

    # Plain text body
    text_body = f"New recruitment posts found on {today_str}:\n\n"
    for p in new_posts:
        text_body += f"• {p['title']}\n"
        text_body += f"  Date : {p['date']}\n"
        text_body += f"  Link : {p['url']}\n\n"
    text_body += f"\nView all: {URL}"

    # HTML body
    rows = ""
    for p in new_posts:
        rows += f"""
        <tr>
          <td style="padding:10px 8px; border-bottom:1px solid #eee;">
            <a href="{p['url']}" style="color:#185FA5; text-decoration:none; font-weight:500;">{p['title']}</a>
          </td>
          <td style="padding:10px 8px; border-bottom:1px solid #eee; white-space:nowrap; color:#555;">{p['date']}</td>
        </tr>"""

    html_body = f"""
    <div style="font-family:Arial,sans-serif; max-width:600px; margin:auto;">
      <div style="background:#185FA5; padding:16px 20px; border-radius:8px 8px 0 0;">
        <h2 style="color:#E6F1FB; margin:0; font-size:16px;">Meghalaya Recruitment Alert</h2>
        <p style="color:#B5D4F4; margin:4px 0 0; font-size:13px;">{today_str}</p>
      </div>
      <div style="border:1px solid #ddd; border-top:none; border-radius:0 0 8px 8px; padding:20px;">
        <p style="color:#333; margin:0 0 16px;">
          {len(new_posts)} new recruitment post(s) were found today:
        </p>
        <table style="width:100%; border-collapse:collapse; font-size:14px;">
          <thead>
            <tr style="background:#f5f5f5;">
              <th style="text-align:left; padding:8px; font-weight:600; color:#333;">Post</th>
              <th style="text-align:left; padding:8px; font-weight:600; color:#333;">Date</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        <p style="margin:20px 0 0; font-size:13px; color:#888;">
          <a href="{URL}" style="color:#185FA5;">View all recruitment posts →</a>
        </p>
      </div>
    </div>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

    print(f"Email sent to {RECIPIENT_EMAIL} with {len(new_posts)} post(s).")


def main():
    print(f"Running check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scraping: {URL}")

    posts = scrape_posts()
    print(f"Total posts found on page: {len(posts)}")

    new_posts = check_today(posts)
    print(f"Posts from today: {len(new_posts)}")

    if new_posts:
        send_email(new_posts)
    else:
        print("No new posts today. No email sent.")


if __name__ == "__main__":
    main()