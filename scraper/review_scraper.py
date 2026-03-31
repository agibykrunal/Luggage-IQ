import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from scraper.utils import random_delay, get_random_user_agent, parse_price

OUTPUT_DIR = Path("data/raw")


def build_review_url(asin, page_num=1):
    return (
        f"https://www.amazon.in/product-reviews/{asin}"
        f"?pageNumber={page_num}&sortBy=recent&reviewerType=all_reviews"
    )


async def scrape_reviews_for_product(browser, asin, brand, min_reviews=50):
    context = await browser.new_context(user_agent=get_random_user_agent())
    page = await context.new_page()

    reviews = []
    page_num = 1

    while len(reviews) < min_reviews:
        url = build_review_url(asin, page_num)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await random_delay(2, 5)

            review_els = await page.query_selector_all("[data-hook='review']")

            if not review_els:
                break

            for el in review_els:
                try:
                    rating_el = await el.query_selector("[data-hook='review-star-rating'] span")
                    rating_text = await rating_el.inner_text() if rating_el else "0"
                    rating = float(rating_text.split(" ")[0]) if rating_text else 0.0

                    title_el = await el.query_selector("[data-hook='review-title'] span:not(.a-icon-alt)")
                    title = await title_el.inner_text() if title_el else ""

                    body_el = await el.query_selector("[data-hook='review-body'] span")
                    body = await body_el.inner_text() if body_el else ""

                    date_el = await el.query_selector("[data-hook='review-date']")
                    date_text = await date_el.inner_text() if date_el else ""

                    helpful_el = await el.query_selector("[data-hook='helpful-vote-statement']")
                    helpful_text = await helpful_el.inner_text() if helpful_el else ""
                    helpful_count = int("".join(filter(str.isdigit, helpful_text))) if helpful_text else 0

                    review_id_el = await el.get_attribute("id")

                    reviews.append({
                        "review_id": review_id_el,
                        "asin": asin,
                        "brand": brand,
                        "rating": rating,
                        "title": title.strip(),
                        "body": body.strip(),
                        "date_raw": date_text.strip(),
                        "helpful_votes": helpful_count,
                        "scraped_at": datetime.utcnow().isoformat(),
                    })
                except Exception:
                    continue

            page_num += 1
            await random_delay(3, 6)

        except Exception as e:
            print(f"Error scraping reviews for {asin} page {page_num}: {e}")
            break

    await context.close()
    return reviews


async def main(input_file, min_reviews):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        products_by_brand = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        all_reviews = []

        for brand_id, products in products_by_brand.items():
            for product in products[:10]:
                asin = product.get("asin")
                if not asin:
                    continue

                print(f"Scraping reviews for {asin} ({brand_id})...")
                reviews = await scrape_reviews_for_product(browser, asin, brand_id, min_reviews)
                all_reviews.extend(reviews)
                print(f"  Got {len(reviews)} reviews")

                out_file = OUTPUT_DIR / f"{asin}_reviews.json"
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(reviews, f, indent=2, ensure_ascii=False)

        combined_file = OUTPUT_DIR / "reviews.json"
        with open(combined_file, "w", encoding="utf-8") as f:
            json.dump(all_reviews, f, indent=2, ensure_ascii=False)

        await browser.close()

    print(f"Total reviews scraped: {len(all_reviews)}")
    print(f"Saved to {OUTPUT_DIR / 'reviews.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/products.json")
    parser.add_argument("--min-reviews", type=int, default=50)
    args = parser.parse_args()
    asyncio.run(main(args.input, args.min_reviews))
