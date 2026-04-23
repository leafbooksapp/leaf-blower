from typing import List, Optional

from integrations import books_api
from models.book import Book


def search(query: str) -> Optional[List[Book]]:
    """Search for books, preferring Google Books with Open Library as fallback."""
    return books_api.search_google(query) or books_api.search_open_library(query)
