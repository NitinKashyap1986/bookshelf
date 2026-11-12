from datetime import datetime, timezone
from itertools import count
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="BookShelf API")

# ---------- Data models ----------

Status = Literal["want_to_read", "reading", "finished"]

class ShelfItemCreate(BaseModel):
    """What the client sends when adding a book."""
    title: str = Field(min_length=1, max_length=300)
    author: str | None = None
    status: Status = "want_to_read"
    rating: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=2000)


class ShelfItem(ShelfItemCreate):
    """What the server stores and returns: the input plus server-made fields."""
    id: int
    added_at: datetime

# ---------- In-memory storage (replaced by a database in week 2) ----------

shelf: list[ShelfItem] = []
id_counter = count(start=1)

# ---------- Endpoints ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/shelf", response_model=ShelfItem, status_code=201)
def add_to_shelf(item: ShelfItemCreate):
    new_item = ShelfItem(
        id=next(id_counter),
        added_at=datetime.now(timezone.utc),
        **item.model_dump(),
    )
    shelf.append(new_item)
    return new_item


@app.get("/api/shelf", response_model=list[ShelfItem])
def list_shelf(status: Status | None = None):
    items = shelf if status is None else [i for i in shelf if i.status == status]
    return sorted(items, key=lambda i: i.added_at, reverse=True)