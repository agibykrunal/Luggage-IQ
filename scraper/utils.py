import asyncio
import random
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


async def random_delay(min_sec=2.0, max_sec=6.0):
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)


def get_random_user_agent():
    return random.choice(USER_AGENTS)


def build_search_url(search_term, page_num=1):
    encoded = search_term.replace(" ", "+")
    return f"https://www.amazon.in/s?k={encoded}&page={page_num}&ref=sr_pg_{page_num}"


def parse_price(price_text):
    if not price_text:
        return 0
    cleaned = re.sub(r"[^\d.]", "", price_text.replace(",", ""))
    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return 0


def classify_price_band(price):
    if price < 3000:
        return "value"
    if price <= 6000:
        return "mid"
    return "premium"


def infer_category(title):
    title_lower = title.lower()
    if any(w in title_lower for w in ["backpack", "laptop bag", "rucksack"]):
        return "Backpack"
    if any(w in title_lower for w in ["duffle", "duffel", "gym bag", "travel bag"]):
        return "Duffle"
    return "Trolley"
