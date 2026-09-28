#!/usr/bin/env python3
"""Add a paper to Zotero with manually provided metadata and PDF URL or web snapshot."""

import sys
import os
import json
import argparse
import urllib.request
from pathlib import Path

API_KEY = os.environ.get("ZOTERO_API_KEY")
if not API_KEY:
    print("Error: ZOTERO_API_KEY not set")
    sys.exit(1)

USER_ID = None


def get_user_id():
    global USER_ID
    if USER_ID:
        return USER_ID
    req = urllib.request.Request(
        f"https://api.zotero.org/keys/{API_KEY}",
        headers={"Zotero-API-Key": API_KEY}
    )
    USER_ID = json.loads(urllib.request.urlopen(req).read())["userID"]
    return USER_ID


def api_request(endpoint, method="GET", data=None, headers=None):
    user_id = get_user_id()
    url = f"https://api.zotero.org/users/{user_id}/{endpoint}"
    hdrs = {"Zotero-API-Key": API_KEY, "Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)

    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=hdrs, method=method)
    else:
        req = urllib.request.Request(url, headers=hdrs, method=method)

    resp = urllib.request.urlopen(req)
    body = resp.read()
    return json.loads(body) if body else None


def get_collection_key(name_or_key):
    collections = api_request("collections")
    for c in collections:
        if c["data"]["key"] == name_or_key or c["data"]["name"].lower() == name_or_key.lower():
            return c["data"]["key"]
    return None


def parse_authors(authors_str):
    creators = []
    for author in authors_str.split(","):
        author = author.strip()
        if not author:
            continue
        parts = author.rsplit(" ", 1)
        if len(parts) == 2:
            creators.append({"creatorType": "author", "firstName": parts[0], "lastName": parts[1]})
        else:
            creators.append({"creatorType": "author", "name": author})
    return creators


def download_content(url):
    print(f"Downloading from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh)"})
    resp = urllib.request.urlopen(req, timeout=120)
    content_type = resp.headers.get("Content-Type", "")
    content = resp.read()
    return content, content_type


def download_html_singlefile(url):
    """Save a fully rendered web page using SingleFile CLI (same as Zotero's web connector)."""
    import subprocess, tempfile
    print(f"Saving web snapshot via SingleFile: {url}")

    # Find playwright's chromium
    try:
        result = subprocess.run(
            ["uv", "run", "python3", "-c",
             "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()"],
            capture_output=True, text=True, timeout=30)
        chromium_path = result.stdout.strip()
    except Exception:
        chromium_path = ""

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        tmp_path = f.name

    cmd = ["single-file", url, tmp_path,
           "--browser-wait-until", "networkidle",
           "--browser-wait-delay", "5000"]
    if chromium_path:
        cmd += ["--browser-executable-path", chromium_path]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0 or not os.path.exists(tmp_path):
        print(f"SingleFile failed: {result.stderr}")
        print("Falling back to raw download")
        content, _ = download_content(url)
        return content

    content = open(tmp_path, "rb").read()
    os.unlink(tmp_path)
    print(f"Saved complete snapshot: {len(content)} bytes")
    return content


def is_html_url(url):
    return url.endswith(".html") or url.endswith(".htm") or any(
        site in url for site in [
            "lesswrong.com", "alignmentforum.org", "transformer-circuits.pub",
            "distill.pub", "arxiv.org/html",
        ]
    )


def save_attachment_local(parent_key, content, filename, link_mode, content_type, url=None):
    attachment = {
        "itemType": "attachment",
        "parentItem": parent_key,
        "linkMode": link_mode,
        "title": filename,
        "contentType": content_type,
        "filename": filename,
    }
    if url and link_mode == "imported_url":
        attachment["url"] = url
        attachment["charset"] = "utf-8"

    result = api_request("items", method="POST", data=[attachment])
    if not result.get("successful"):
        print(f"Failed to create attachment: {result}")
        return False

    attach_key = list(result["successful"].values())[0]["key"]
    print(f"Created attachment item: {attach_key}")

    zotero_storage = Path.home() / "Zotero" / "storage" / attach_key
    zotero_storage.mkdir(parents=True, exist_ok=True)

    file_path = zotero_storage / filename
    file_path.write_bytes(content)
    print(f"Saved to: {file_path} ({len(content)} bytes)")
    return True


def create_item(metadata, collection_key=None):
    if collection_key:
        metadata["collections"] = [collection_key]
    return api_request("items", method="POST", data=[metadata])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a paper to Zotero with manual metadata")
    parser.add_argument("--pdf", required=True, help="URL to the PDF file or webpage to snapshot")
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--authors", required=True, help="Comma-separated author names (e.g., 'John Smith, Jane Doe')")
    parser.add_argument("--year", required=True, help="Publication year")
    parser.add_argument("--url", help="URL to the paper page (not the PDF)")
    parser.add_argument("--abstract", help="Paper abstract")
    parser.add_argument("--type", default="report", choices=["report", "preprint", "journalArticle", "conferencePaper", "webpage"], help="Item type")
    parser.add_argument("--publisher", help="Publisher or institution name")
    parser.add_argument("--collection", help="Zotero collection name or key")

    args = parser.parse_args()

    collection_key = None
    if args.collection:
        collection_key = get_collection_key(args.collection)
        if not collection_key:
            print(f"Error: Collection '{args.collection}' not found")
            sys.exit(1)

    metadata = {
        "itemType": args.type,
        "title": args.title,
        "creators": parse_authors(args.authors),
        "date": args.year,
    }

    if args.url:
        metadata["url"] = args.url
    elif args.type == "webpage":
        metadata["url"] = args.pdf
    if args.abstract:
        metadata["abstractNote"] = args.abstract
    if args.publisher:
        if args.type == "report":
            metadata["institution"] = args.publisher
        else:
            metadata["publisher"] = args.publisher
    if args.type == "webpage" and args.publisher:
        metadata["websiteTitle"] = args.publisher

    print(f"Title: {metadata['title']}")
    print(f"Authors: {', '.join(c.get('lastName', c.get('name')) for c in metadata['creators'])}")
    print(f"Year: {args.year}")

    result = create_item(metadata, collection_key)
    if not result.get("successful"):
        print(f"Error creating item: {result}")
        sys.exit(1)

    parent_key = list(result["successful"].values())[0]["key"]
    print(f"Created item: {parent_key}")

    try:
        content, resp_content_type = download_content(args.pdf)
        source_url = args.pdf

        if is_html_url(source_url) or "text/html" in resp_content_type:
            # Save as web snapshot using SingleFile for proper rendering
            content = download_html_singlefile(source_url)
            slug = args.title[:50].replace(" ", "-").replace("/", "-").lower()
            filename = f"{slug}.html"
            save_attachment_local(parent_key, content, filename,
                                 link_mode="imported_url",
                                 content_type="text/html",
                                 url=source_url)
        else:
            # Save as PDF
            filename = source_url.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename = f"{args.title[:50].replace(' ', '_')}.pdf"
            save_attachment_local(parent_key, content, filename,
                                 link_mode="imported_file",
                                 content_type="application/pdf")
    except Exception as e:
        print(f"Warning: Could not attach file: {e}")

    print("Done!")
