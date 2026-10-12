"""One-off export of blog.detassigny.net (simple-blog PHP CMS) into Zensical Markdown.

Usage: python scripts/migrate.py [docs_dir]

Fetches every post page and the RSS feed from the live site, converts the
TinyMCE HTML bodies to Markdown, downloads uploaded images, and writes
posts into <docs_dir>/posts/. Prints an id -> slug map for the redirects.
"""

import re
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree

import ftfy
import requests
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

BASE_URL = "https://blog.detassigny.net"
POST_IDS = range(1, 13)


def slugify(title: str) -> str:
    """Replicates simple-blog's slug generation so new URLs match the old slugs."""
    slug = re.sub(r"[^A-Za-z0-9-]", "-", title)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-").lower()


def rss_dates(session: requests.Session) -> dict[int, datetime]:
    xml = session.get(f"{BASE_URL}/rss", timeout=30).content
    dates = {}
    for item in ElementTree.fromstring(xml).iter("item"):
        match = re.search(r"/posts/(\d+)/", item.findtext("link", ""))
        if match:
            dates[int(match.group(1))] = parsedate_to_datetime(item.findtext("pubDate")).astimezone(timezone.utc).replace(tzinfo=None)
    return dates


def parse_meta_date(text: str) -> datetime:
    # e.g. "November 29th, 2018 | Written by Gabriel de Tassigny"
    raw = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text.split("|")[0].strip())
    return datetime.strptime(raw, "%B %d, %Y")


class Converter(MarkdownConverter):
    def convert_img(self, el, text, parent_tags):
        return f"![{el.get('alt', '')}]({el['src']})"


def code_language(el):
    for cls in el.get("class") or []:
        if cls.startswith("language-"):
            return cls.removeprefix("language-")
    return None


def to_markdown(html: str) -> str:
    md = Converter(
        heading_style="ATX",
        bullets="-",
        code_language_callback=code_language,
        escape_underscores=False,
        escape_asterisks=False,
    ).convert(html)
    md = md.replace(" ", " ")
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def main() -> None:
    docs = Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
    posts_dir = docs / "posts"
    images_dir = posts_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    dates = rss_dates(session)
    redirects = {}
    files = {}

    for post_id in POST_IDS:
        page_url = f"{BASE_URL}/posts/{post_id}/x"
        soup = BeautifulSoup(ftfy.fix_text(session.get(page_url, timeout=30).text), "html.parser")

        title = soup.select_one(".post-header h1").get_text(strip=True)
        subtitle = soup.select_one(".post-description").get_text(strip=True)
        date = dates.get(post_id) or parse_meta_date(soup.select_one(".blog-post-meta").get_text())
        slug = slugify(title)
        content = soup.select_one(".post-content")

        for img in content.find_all("img"):
            src = urljoin(page_url, img["src"])
            name = Path(src).name
            (images_dir / name).write_bytes(session.get(src, timeout=30).content)
            img.attrs = {"src": f"images/{name}", "alt": img.get("alt") or name.split("-")[0].title()}

        for el in content.find_all(["h1", "h2", "h3", "h4", "p", "strong", "em"]):
            if not el.get_text(strip=True) and not el.find("img"):
                el.decompose()

        body = to_markdown(content.decode_contents().replace("\u00a0", " "))
        date_str = date.strftime("%Y-%m-%d %H:%M:%S") if date.time() != datetime.min.time() else date.strftime("%Y-%m-%d")
        front_matter = "\n".join([
            "---",
            f"date: {date_str}",
            "authors:",
            "  - gabriel",
            f"slug: {slug}",
            f"description: {subtitle!r}" if ":" in subtitle else f"description: {subtitle}",
            "---",
        ])
        post = f"{front_matter}\n\n# {title}\n\n{subtitle}\n\n<!-- more -->\n\n{body}"
        filename = f"{date:%Y-%m-%d}-{slug}.md"
        (posts_dir / filename).write_text(post)
        redirects[post_id] = slug
        files[post_id] = filename

    # Point links between posts at the Markdown sources so Zensical resolves them
    for path in posts_dir.glob("*.md"):
        text = re.sub(
            r"\]\((?:https?://blog\.detassigny\.net)?/posts/(\d+)(?:/[^ )]*)?",
            lambda m: f"]({files[int(m.group(1))]}",
            path.read_text(),
        )
        path.write_text(text)

    for post_id, slug in redirects.items():
        print(f"{post_id}\t{slug}")


if __name__ == "__main__":
    main()
