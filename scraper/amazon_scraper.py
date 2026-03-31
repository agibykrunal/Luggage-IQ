import asyncio
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from scraper.utils import random_delay, get_random_user_agent, build_search_url, parse_price

OUTPUT_DIR = Path("data/raw")

BRAND_SEARCH_TERMS = {
    "safari": "Safari luggage trolley",
    "skybags": "Skybags trolley luggage",
    "american-tourister": "American Tourister luggage",
    "vip": "VIP trolley bags",
    "aristocrat": "Aristocrat luggage trolley",
    "nasher-miles": "Nasher Miles hard luggage",
}

async def scrape_product_listing(page, url):
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await random_delay(2, 4)

    products = []
    items = await page.query_selector_all('[data-component-type="s-search-result"]')

    for item in items:
        try:
            asin = await item.get_attribute("data-asin")
            title_el = await item.query_selector("h2 a span")
            title = await title_el.inner_text() if title_el else ""

            price_el = await item.query_selector(".a-price .a-offscreen")
            price_text = await price_el.inner_text() if price_el else ""
            price = parse_price(price_text)

            list_price_el = await item.query_selector(".a-text-price .a-offscreen")
            list_price_text = await list_price_el.inner_text() if list_price_el else ""
            list_price = parse_price(list_price_text)

            rating_el = await item.query_selector(".a-icon-alt")
            rating_text = await rating_el.inner_text() if rating_el else "0"
            rating = float(rating_text.split(" ")[0]) if rating_text else 0.0

            review_el = await item.query_selector('[aria-label*="ratings"]')
            review_text = await review_el.get_attribute("aria-label") if review_el else "0"
            review_count = int("".join(filter(str.isdigit, review_text.split(" ")[0]))) if review_text else 0

            link_el = await item.query_selector("h2 a")
            link = await link_el.get_attribute("href") if link_el else ""
            full_link = f"https://www.amazon.in{link}" if link.startswith("/") else link

            discount = round((1 - price / list_price) * 100, 1) if list_price and price and list_price > price else 0.0

            products.append({
                "asin": asin,
                "product_title": title.strip(),
                "url": full_link,
                "sell_price": price,
                "list_price": list_price,
                "discount_pct": discount,
                "rating": rating,
                "review_count": review_count,
                "scraped_at": datetime.utcnow().isoformat(),
            })
        except Exception:
            continue

    return products


async def scrape_brand(browser, brand_id, search_term, max_pages=3):
    context = await browser.new_context(user_agent=get_random_user_agent())
    page = await context.new_page()

    all_products = []

    for page_num in range(1, max_pages + 1):
        url = build_search_url(search_term, page_num)
        try:
            products = await scrape_product_listing(page, url)
            all_products.extend(products)
            await random_delay(3, 7)
        except Exception as e:
            print(f"Error scraping {brand_id} page {page_num}: {e}")
            break

    await context.close()

    for product in all_products:
        product["brand"] = brand_id

    return all_products


async def main(brands_to_scrape):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        all_results = {}

        for brand_id in brands_to_scrape:
            search_term = BRAND_SEARCH_TERMS.get(brand_id)
            if not search_term:
                print(f"Unknown brand: {brand_id}")
                continue

            print(f"Scraping {brand_id}...")
            products = await scrape_brand(browser, brand_id, search_term)
            all_results[brand_id] = products
            print(f"  Found {len(products)} products for {brand_id}")

            out_file = OUTPUT_DIR / f"{brand_id}_products.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

        combined_file = OUTPUT_DIR / "products.json"
        with open(combined_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        await browser.close()

    print(f"Done. Output saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--brands", nargs="+", default=list(BRAND_SEARCH_TERMS.keys()))
    args = parser.parse_args()
    asyncio.run(main(args.brands))
