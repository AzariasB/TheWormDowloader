import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

START = "https://pactwebserial.wordpress.com/2013/12/17/bonds-1-1/"
TITLE = "Pact"

TARGET_DOC = "out.html"
PAGE_BREAK = '<div style="break-after: page;"></div>'
ALIGN_STYLE = re.compile(r"text-align\s*:\s*(center|left|right)")
PADDING_STYLE = re.compile(r"padding-left\s*:\s*(\d+)px")
NAVIGATORS = re.compile(r"\s*(Next|Previous)\s*Chapter")
NEXT_REG = re.compile(r"\s*Next\s+Chapter\s*")

PAGE_CONTENT = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
</head>
<body>
<h1 style="text-align: center" >{TITLE}</h1>
"""


def fetch_page_content(page_data: BeautifulSoup) -> BeautifulSoup:
    main_content = page_data.find("article", attrs={"class": "type-post"})

    # Remove all the next/previous/last links
    for g in main_content.select('a'):
        if p := g.find_parent("p"):
            p.decompose()

    for g in main_content.find('span', string=NAVIGATORS) or []:
        if p := g.find_parent('p'):
            p.decompose()

    # Remove posted on date
    if posted_date_div := main_content.find('div', attrs={'class': 'entry-meta'}):
        posted_date_div.decompose()

    # Remove sharing div
    if sharing_div := main_content.find('div', attrs={'id': 'jp-post-flair'}):
        sharing_div.decompose()

    # Remove footer
    if decompose := main_content.find('footer'):
        decompose.decompose()

    return main_content


def get_next_page(page_data: BeautifulSoup) -> str | None:
    return (found := page_data.find('a', string=NEXT_REG)) and found.attrs.get("href", None) or None


def clean_link(link: str | None) -> str | None:
    """
    Some links are missing the "https:" part, so we add it here
    :param link:
    :return:
    """
    if not link:
        return None

    return link if link.startswith("https") else f"https:{link}"


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

                    current_page = clean_link(get_next_page(bs))
                    content = fetch_page_content(bs)
                    f.write(content.prettify())
                    f.write(PAGE_BREAK)
                # Sleep a bit to avoid flooding the website with requests
                await asyncio.sleep(1)
        f.write("</body></html>")


if __name__ == "__main__":
    asyncio.run(main())
