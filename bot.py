import os
import requests
import feedparser
import time
import re
from datetime import datetime

# =========================
# ตั้งค่า Telegram
# =========================
# ใช้ TOKEN และ CHAT_ID จาก Environment Variables
# เวลาใช้บน Render ให้ไปใส่ค่าใน Environment
# TOKEN = โทเคนบอท
# CHAT_ID = แชทไอดีของ Telegram

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# =========================
# คำค้นหาข่าว
# =========================

KEYWORDS = [
    "บัญชีม้า", "จับบัญชีม้า", "แก๊งบัญชีม้า",
    "พนันออนไลน์", "เว็บพนัน", "เว็บพนันออนไลน์",
    "สล็อต", "สล็อตออนไลน์", "บาคาร่า", "หวยออนไลน์",
    "ฉ้อโกง", "หลอกลงทุน", "หลอกโอนเงิน", "หลอกขาย",
    "ฟอกเงิน", "ยึดทรัพย์", "จับกุม",
    "แก๊งคอลเซ็นเตอร์", "คอลเซ็นเตอร์",
    "อาชญากรรมออนไลน์", "ภัยออนไลน์",
    "scam", "fraud", "online gambling", "money laundering"
]

# =========================
# เว็บไซต์ข่าว RSS
# =========================

FEEDS = [
    "https://www.thairath.co.th/rss/news.xml",
    "https://www.dailynews.co.th/rss/news/",
    "https://www.khaosod.co.th/rss",
    "https://www.matichon.co.th/feed",
    "https://www.prachachat.net/feed",
    "https://www.sanook.com/news/rss/",
    "https://mgronline.com/rss/Crime",
    "https://www.naewna.com/rss/news.xml",
    "https://www.komchadluek.net/rss",
    "https://www.posttoday.com/rss",
    "https://www.bangkokbiznews.com/rss",
    "https://www.bangkokpost.com/rss/data/topstories.xml",
    "https://feeds.bbci.co.uk/thai/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

sent = set()
last_morning_date = None

def clean_html(text):
    text = text or ""
    text = re.sub("<.*?>", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    return text.strip()

def summarize(text, max_len=230):
    text = clean_html(text)

    if not text:
        return "ไม่มีรายละเอียดเพิ่มเติมจากแหล่งข่าว"

    if len(text) > max_len:
        return text[:max_len] + "..."

    return text

def is_relevant(content):
    content = content.lower()
    return any(keyword.lower() in content for keyword in KEYWORDS)

def send_message(msg):
    if not TOKEN or not CHAT_ID:
        print("ยังไม่ได้ตั้งค่า TOKEN หรือ CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, data=data, timeout=15)

        if response.status_code != 200:
            print("ส่งข้อความไม่สำเร็จ:", response.text)

    except Exception as e:
        print("เกิดข้อผิดพลาดตอนส่ง Telegram:", e)

def thai_day_name():
    days = {
        0: "จันทร์",
        1: "อังคาร",
        2: "พุธ",
        3: "พฤหัสบดี",
        4: "ศุกร์",
        5: "เสาร์",
        6: "อาทิตย์"
    }

    return days[datetime.now().weekday()]

def thai_date():
    months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
        "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
        "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]

    now = datetime.now()
    thai_year = now.year + 543

    return f"{now.day} {months[now.month - 1]} {thai_year}"

def morning_message():
    day = thai_day_name()
    date_text = thai_date()

    msg = f"""📢 รายงานข่าวอาชญากรรมออนไลน์

ประจำวันที่ {date_text}
สวัสดีเช้าวัน{day}

ขอให้วันนี้เป็นวันที่ดี และขอให้ทุกท่านใช้ความระมัดระวังในการรับข่าวสาร การทำธุรกรรมทางการเงิน และการใช้งานช่องทางออนไลน์ต่าง ๆ

⚠️ ระบบจะติดตามและคัดกรองข่าวที่เกี่ยวข้องกับประเด็นสำคัญ ได้แก่

- บัญชีม้า / การฟอกเงิน
- เว็บพนัน / พนันออนไลน์ / สล็อตออนไลน์
- การฉ้อโกง / หลอกลงทุน / หลอกโอนเงิน
- แก๊งคอลเซ็นเตอร์
- อาชญากรรมออนไลน์และภัยไซเบอร์

📡 หากพบข่าวที่เกี่ยวข้อง ระบบจะแจ้งเตือนโดยอัตโนมัติจากแหล่งข่าวที่เปิดเผยต่อสาธารณะ

โปรดใช้วิจารณญาณในการอ่านข่าว และติดตามข้อมูลจากหน่วยงานหรือสื่อที่น่าเชื่อถือ"""

    send_message(msg)

def check_morning_message():
    global last_morning_date

    now = datetime.now()
    today = now.date()

    if now.hour == 8 and last_morning_date != today:
        morning_message()
        last_morning_date = today

def get_news():
    print("🔎 กำลังตรวจสอบข่าว...")
    count = 0

    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                title = getattr(entry, "title", "")
                link = getattr(entry, "link", "")
                summary = getattr(entry, "summary", "")

                if not link:
                    continue

                if link in sent:
                    continue

                content = f"{title} {summary}"

                if is_relevant(content):
                    short_summary = summarize(summary)

                    msg = f"""🚨 แจ้งเตือนข่าวที่เกี่ยวข้อง

📌 หัวข้อข่าว:
{title}

📝 รายละเอียดโดยย่อ:
{short_summary}

🔗 แหล่งข่าว:
{link}"""

                    send_message(msg)

                    print("ส่งข่าวแล้ว:", title)

                    sent.add(link)
                    count += 1

                    if count >= 5:
                        print("ครบจำนวนข่าวต่อรอบแล้ว")
                        return

        except Exception as e:
            print("อ่านข่าวจาก RSS ไม่สำเร็จ:", feed_url, e)

print("🤖 ระบบบอทเริ่มทำงานแล้ว")
print("📡 กำลังติดตามข่าวอาชญากรรมออนไลน์")

send_message("✅ บอทเริ่มทำงานแล้ว")
get_news()

while True:
    check_morning_message()
    get_news()

    print("⏳ รอ 10 นาที ก่อนตรวจสอบข่าวรอบถัดไป")
    time.sleep(600)
