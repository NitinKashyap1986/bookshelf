from datetime import datetime, timezone
from itertools import count
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from datetime import datetime, timezone
from itertools import count
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="BookShelf API")

# ---------- Data models ----------

Status = Literal["want_to_read", "reading", "finished"]
Rating = Annotated[int, Field(ge=1, le=5)]
Notes = Annotated[str, Field(max_length=2000)]

class ShelfItemCreate(BaseModel):
    """What the client sends when adding a book."""
    title: str = Field(min_length=1, max_length=300)
    author: str | None = None
    status: Status = "want_to_read"
    rating: Rating | None = None
    notes: Notes | None = None

class ShelfItemUpdate(BaseModel):
    """What the client may send to change an item. Every field is optional."""
    model_config = ConfigDict(extra="forbid")

    status: Status | None = None
    rating: Rating | None = None
    notes: Notes | None = None

class ShelfItem(ShelfItemCreate):
    """What the server stores and returns."""
    id: int
    added_at: datetime
    finished_at: datetime | None = None

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
    now = datetime.now(timezone.utc)
    new_item = ShelfItem(
        id=next(id_counter),
        added_at=now,
        finished_at=now if item.status == "finished" else None,
        **item.model_dump(),
    )
    shelf.append(new_item)
    return new_item

def find_index(item_id: int) -> int:
    """Return the list position of the item with this id, or raise a 404."""
    for index, item in enumerate(shelf):
        if item.id == item_id:
            return index
    raise HTTPException(status_code=404, detail=f"Shelf item {item_id} not found")


@app.get("/api/shelf", response_model=list[ShelfItem])
def list_shelf(status: Status | None = None):
    items = shelf if status is None else [i for i in shelf if i.status == status]
    return sorted(items, key=lambda i: i.added_at, reverse=True)

@app.patch("/api/shelf/{item_id}", response_model=ShelfItem)
def update_shelf_item(item_id: int, changes: ShelfItemUpdate):
    index = find_index(item_id)
    current = shelf[index]

    data = changes.model_dump(exclude_unset=True)
    if data.get("status") is None:
        data.pop("status", None)  # status can't be cleared, so ignore null

    if "status" in data:
        if data["status"] == "finished" and current.status != "finished":
            data["finished_at"] = datetime.now(timezone.utc)
        elif data["status"] != "finished":
            data["finished_at"] = None

    updated = current.model_copy(update=data)
    shelf[index] = updated
    return updated

@app.delete("/api/shelf/{item_id}", status_code=204)
def delete_shelf_item(item_id: int):
    index = find_index(item_id)
    shelf.pop(index)
    return Response(status_code=204)