markdown
# BookShelf — Requirements (MVP v1.0.0)

## Purpose
BookShelf is a personal reading tracker. I can find any book, keep it on my shelf,
and track it from "want to read" to "finished", with a rating and notes.

## Users
- **Reader** — a person tracking their own books. (Until v1.1.0 there is one reader: me.)

## Key terms
- **Book** — a title from Open Library (title, authors, first publish year, cover).
- **Shelf item** — a book on my shelf, plus my status, rating and notes.
- **Status** — one of: `want_to_read`, `reading`, `finished`.

## MVP features

### F1. Search for books
As a reader, I want to search by title or author so that I can find a book to add.
- Typing a query and searching shows up to 20 results with title, author(s), year and cover image.
- Books with no cover show a placeholder image.
- An empty search is not sent; the app asks me to type something.
- If Open Library is slow or down, I see a friendly error, not a crash.
- Search waits until I stop typing (~400 ms) so it doesn't call the API on every keystroke.
Backend: `GET /api/search?q=...&page=1` → calls Open Library.

### F2. Add a book to my shelf
As a reader, I want to add a search result to my shelf with a status so that I can track it.
- Each search result has an "Add to shelf" button; default status is `want_to_read`.
- The same book can't be added to my shelf twice; I'm told it's already there.
- The book's details are saved once in the database, even if added again later by another user.
Backend: `POST /api/shelf`.

### F3. View my shelf
As a reader, I want to see all my books and filter by status so that I know what I'm reading.
- The shelf lists every book with cover, title, author, status, rating and notes.
- I can filter to All / Want to read / Reading / Finished.
- Newest additions appear first.
- An empty shelf shows a message pointing me to search.
Backend: `GET /api/shelf?status=...`.

### F4. Update a book on my shelf
As a reader, I want to change a book's status, rating and notes so that my shelf stays current.
- I can change status at any time.
- When status becomes `finished`, the finish date is recorded automatically.
- Rating is optional and must be a whole number from 1 to 5; anything else is rejected.
- Notes are free text, up to 2,000 characters.
- Changes are saved and still there after a page reload.
Backend: `PATCH /api/shelf/{id}`.

### F5. Remove a book from my shelf
As a reader, I want to remove a book so that my shelf only has books I care about.
- I'm asked to confirm before it's removed.
- After removal it's gone from the list and from the database.
- Removing a book that doesn't exist returns "not found", not a crash.
Backend: `DELETE /api/shelf/{id}`.

### F6. See my reading stats
As a reader, I want a summary of my reading so that I can see my progress.
- Shows how many books are in each status.
- Shows how many books I finished this calendar year.
- Numbers update right after I change a book's status.
Backend: `GET /api/stats`.

## After the MVP
### F7. Accounts (v1.1.0)
As a reader, I want my own account so that my shelf is private to me.
- I can sign up with email and password, and log in and out.
- Passwords are never stored in plain text.
- I only ever see and change my own shelf items.

## Non-functional requirements
- **Cost:** everything runs on free tiers (Render, Neon, GitHub Pages, Open Library).
- **Hosting:** the app is reachable at a public URL and works on a phone browser.
- **Reliability:** the first request after idle may take ~1 minute (Render free tier);
  the app shows a "waking up" message instead of looking broken.
- **Security:** no secrets (database URL, JWT secret) in the code or repo.
- **Quality:** every feature has automated tests; all tests pass before merging to `main`.
- **Etiquette:** calls to Open Library use a timeout and a descriptive User-Agent.

## Out of scope (for now)
- Social features (following friends, sharing shelves)
- Reading progress by page number
- Importing from Goodreads
- Native mobile apps