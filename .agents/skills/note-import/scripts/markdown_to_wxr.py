#!/usr/bin/env python3
"""Convert Markdown articles into a minimal WXR file for note import."""

from __future__ import annotations

import argparse
import html
import re
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "note-article"


def extract_title_and_body(markdown: str) -> tuple[str, list[str]]:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            return line[2:].strip(), lines[:index] + lines[index + 1 :]
    return "Untitled", lines


def inline_markdown(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        lambda match: f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    if re.fullmatch(r"https?://\S+", text.strip()):
        url = html.escape(text.strip(), quote=True)
        return f'<a href="{url}">{url}</a>'
    return escaped


def markdown_to_html(lines: list[str]) -> str:
    output: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            output.append("<ul>")
            output.extend(f"<li>{item}</li>" for item in list_items)
            output.append("</ul>")
            list_items = []

    def append_paragraph(text: str) -> None:
        # note import renders <p> margins generously; use line breaks for tighter prose.
        output.append(f"{inline_markdown(text)}<br />")

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            flush_list()
            continue

        heading = re.match(r"^(#{2,4})\s+(.+)$", line)
        if heading:
            flush_list()
            level = len(heading.group(1))
            output.append(f"<h{level}>{inline_markdown(heading.group(2).strip())}</h{level}>")
            continue

        bullet = re.match(r"^-\s+(.+)$", line)
        if bullet:
            list_items.append(inline_markdown(bullet.group(1).strip()))
            continue

        flush_list()
        append_paragraph(line)

    flush_list()
    return "\n".join(output).strip()


def build_item(
    title: str,
    content_html: str,
    slug: str,
    post_date: datetime,
    post_id: int,
) -> str:
    pub_date = format_datetime(post_date)
    post_date_text = post_date.strftime("%Y-%m-%d %H:%M:%S")
    title_xml = escape(title)
    slug_xml = escape(slug)
    content_cdata = content_html.replace("]]>", "]]]]><![CDATA[>")

    return f"""    <item>
      <title>{title_xml}</title>
      <link>https://note.com/</link>
      <pubDate>{pub_date}</pubDate>
      <dc:creator><![CDATA[harness17]]></dc:creator>
      <guid isPermaLink="false">{slug_xml}</guid>
      <description></description>
      <content:encoded><![CDATA[{content_cdata}]]></content:encoded>
      <excerpt:encoded><![CDATA[]]></excerpt:encoded>
      <wp:post_id>{post_id}</wp:post_id>
      <wp:post_date><![CDATA[{post_date_text}]]></wp:post_date>
      <wp:post_date_gmt><![CDATA[{post_date_text}]]></wp:post_date_gmt>
      <wp:comment_status><![CDATA[closed]]></wp:comment_status>
      <wp:ping_status><![CDATA[closed]]></wp:ping_status>
      <wp:post_name><![CDATA[{slug_xml}]]></wp:post_name>
      <wp:status><![CDATA[draft]]></wp:status>
      <wp:post_parent>0</wp:post_parent>
      <wp:menu_order>0</wp:menu_order>
      <wp:post_type><![CDATA[post]]></wp:post_type>
      <wp:post_password><![CDATA[]]></wp:post_password>
      <wp:is_sticky>0</wp:is_sticky>
    </item>"""


def build_wxr(items: list[str], post_date: datetime) -> str:
    pub_date = format_datetime(post_date)
    joined_items = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:wfw="http://wellformedweb.org/CommentAPI/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
  <channel>
    <title>note import</title>
    <link>https://note.com/</link>
    <description>Generated WXR for note import</description>
    <pubDate>{pub_date}</pubDate>
    <language>ja</language>
    <wp:wxr_version>1.2</wp:wxr_version>
{joined_items}
  </channel>
</rss>
"""


def parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.now().replace(microsecond=0)
    return datetime.fromisoformat(value).replace(microsecond=0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Markdown to note-compatible WXR.")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("-o", "--output", required=True, type=Path)
    parser.add_argument("--slug", action="append", default=[])
    parser.add_argument("--date", default="", help="ISO datetime, e.g. 2026-05-21T21:30:00")
    args = parser.parse_args()

    post_date = parse_date(args.date or None)
    items = []
    for index, input_path in enumerate(args.inputs, start=1):
        markdown = input_path.read_text(encoding="utf-8")
        title, body_lines = extract_title_and_body(markdown)
        content_html = markdown_to_html(body_lines)
        slug = args.slug[index - 1] if index <= len(args.slug) else slugify(input_path.stem)
        items.append(build_item(title, content_html, slug, post_date, index))

    wxr = build_wxr(items, post_date)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(wxr, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
