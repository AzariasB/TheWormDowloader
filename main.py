import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

START = "https://parahumans.wordpress.com/2011/06/11/1-1/"
TARGET_DOC = "worm.html"
PAGE_BREAK = '<div class="page-break"></div>'
NEXT_PATTERN = re.compile(r"\s*Next\s*Chapter\s*")

PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>The worm</title>
</head>
<body>
"""


def fetch_page_content(page_data: BeautifulSoup) -> BeautifulSoup:
    main_content = page_data.find("article", attrs={"class": "type-post"})
    # Remove "next chapter button"
    for g in main_content.find_all('a', string=NEXT_PATTERN):
        g.parent.decompose()
    # Remove posted on date
    main_content.find('div', attrs={'class': 'entry-meta'}).decompose()

    # Remove sharing div
    main_content.find('div', attrs={'id': 'jp-post-flair'}).decompose()

    # Remove footer
    main_content.find('footer').decompose()

    return main_content


def get_next_page(page_data: BeautifulSoup) -> str | None:
    return (found := page_data.find('a', string=NEXT_PATTERN)) and found.attrs.get("href", None) or None


async def main():
    current_page = START
    with open(TARGET_DOC, "w") as f:
        f.write(PAGE_CONTENT)
        async with aiohttp.ClientSession() as session:
            while current_page is not None:
                async with session.get(current_page) as response:
                    print(f"Parsing page {current_page}")
                    raw_html = await response.text()
                    bs = BeautifulSoup(raw_html, 'html.parser')

                    current_page = get_next_page(bs)
                    content = fetch_page_content(bs)
                    f.write(content.prettify())
                    f.write(PAGE_BREAK)
                # Sleep a bit to avoid flooding the website with requests
                await asyncio.sleep(1)
        f.write("</body></html>")


if __name__ == "__main__":
    asyncio.run(main())
