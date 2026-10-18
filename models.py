from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Status:
    id: int
    sname: str

@dataclass
class Author:
    id: int
    fullname: str

@dataclass
class Genre:
    id: int
    gname: str

@dataclass
class Item:
    id: Optional[int]
    name: str
    year: int
    rating: Optional[int]
    status_id: int

@dataclass
class ItemFull:
    id: int
    name: str
    year: int
    rating: Optional[int]
    status_name: str
    authors: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)