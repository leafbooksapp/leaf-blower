import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

from models.book import Book


def search_google(q: str) -> Optional[List[Book]]:
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY", "")
    if not api_key:
        return None
    url = "https://www.googleapis.com/books/v1/volumes?" + urllib.parse.urlencode({
        "q": q,
        "maxResults": 20,
        "key": api_key,
    })
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Leaf/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    books = []
    for item in data.get("items") or []:
        info = item.get("volumeInfo") or {}
        ids = {i["type"]: i["identifier"] for i in info.get("industryIdentifiers") or []}
        images = info.get("imageLinks") or {}
        books.append(Book(
            title=info.get("title", ""),
            authors=info.get("authors") or [],
            isbn13=ids.get("ISBN_13"),
            isbn10=ids.get("ISBN_10"),
            cover_url=images.get("thumbnail") or images.get("smallThumbnail"),
            year=(info.get("publishedDate") or "")[:4] or None,
            source="google",
        ))
    return books or None


def search_open_library(q: str) -> Optional[List[Book]]:
    url = "https://openlibrary.org/search.json?" + urllib.parse.urlencode({
        "q": q,
        "fields": "key,title,author_name,first_publish_year,isbn,cover_i",
        "limit": 20,
    })
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Leaf/1.0 (leaf@example.com)"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    books = []
    for doc in data.get("docs") or []:
        isbns = doc.get("isbn") or []
        cover_id = doc.get("cover_i")
        books.append(Book(
            title=doc.get("title", ""),
            authors=doc.get("author_name") or [],
            isbn13=next((i for i in isbns if len(i) == 13), None),
            isbn10=next((i for i in isbns if len(i) == 10), None),
            cover_url=f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None,
            year=doc.get("first_publish_year"),
            source="openlibrary",
        ))
    return books or None
