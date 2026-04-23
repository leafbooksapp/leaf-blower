from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class Book:
    title: str
    authors: List[str] = field(default_factory=list)
    isbn13: Optional[str] = None
    isbn10: Optional[str] = None
    cover_url: Optional[str] = None
    year: Optional[int] = None
    source: Optional[str] = None

    def to_dict(self):
        return asdict(self)
