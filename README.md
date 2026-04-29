# CineRef

## What is CineRef?

CineRef is a community-driven cinematic reference platform built with Python, Flask, and SQLite. It was designed for filmmakers — students, first-jobbers, independent filmmakers, and enthusiasts — who need a free, open alternative to expensive paywalled tools like Shotdeck. The idea is simple: any filmmaker can upload tagged frames from their work, turning their portfolio into a searchable reference library for the entire community. Think of it as the Wikipedia model applied to cinematography — open, community-first, and free.

The project was born out of a real gap in the filmmaking world. Reference tools are essential for pre-production, but the good ones cost money that emerging filmmakers in developing markets simply do not have. CineRef targets that underserved audience: the film student in Bangkok, the first-jobber in Lagos, the independent filmmaker in Buenos Aires. The platform is built with the assumption that great cinema exists everywhere, not just in Hollywood, and that the people making it deserve the same tools.

---

## Design Philosophy

From the beginning, the goal was to build something that felt like a real product — not a homework project. Every design decision was made with that in mind. The visual aesthetic draws inspiration from A24's editorial style: dark, cinematic, minimal, with strong typography and deliberate use of whitespace. The browse page uses a masonry layout so that images retain their natural proportions, giving the grid a dynamic, living quality rather than the rigid block feel of a standard grid. Shot cards reveal metadata on hover, keeping the interface clean while making information accessible.

The shot detail page was directly inspired by Shotdeck's layout — a full-bleed image at the top, two-column metadata below with bold labels and muted values. The image bleeds past the container padding using a negative margin technique, making it feel cinematic and immersive rather than boxed in. The browse page also features rotating quotes from legendary directors and cinematographers, fading between them every five seconds, which gives the platform a sense of identity and culture beyond just being a file storage tool.

---

## Technical Stack

- **Python 3.9** — backend language
- **Flask 3.1** — web framework
- **Flask-Session** — server-side session management using the filesystem
- **CS50 SQL library** — database abstraction layer for SQLite
- **SQLite** — relational database for storing users, shots, and collections
- **Werkzeug** — password hashing (`pbkdf2:sha256`) and secure filename sanitization
- **Jinja2** — HTML templating
- **Inter + Playfair Display** — Google Fonts for typography

---

## File Structure

### `app.py`
The heart of the application. Contains all Flask routes and their logic. Each route follows a consistent pattern: validate input server-side, interact with the database, then either redirect or render a template. Key routes include:

- **`/register`** — Handles new user registration. Validates that all required fields are present, checks that passwords match, inserts the user into the database with a hashed password using `pbkdf2:sha256`, and sets the session.
- **`/login`** — Queries the database for the username, verifies the password hash using `check_password_hash`, clears any existing session, then sets `session["user_id"]` and `session["username"]`.
- **`/logout`** — Clears the session and redirects to the homepage.
- **`/upload`** — The most technically complex route. Receives both form data and a file upload. Uses `request.files.get()` for the image (not `request.form.get()`, which only handles text). Sanitizes the filename with `secure_filename()`, saves the file to `static/uploads/`, stores the path string in the database, and inserts all metadata fields.
- **`/browse`** — Queries all shots ordered by `RANDOM()` so the grid shuffles on every page load, keeping the experience fresh.
- **`/shot/<int:id>`** — Fetches a single shot by ID using a URL parameter. Flask automatically extracts the integer from the URL and passes it to the function. Handles the case where an ID does not exist by catching `IndexError` on an empty list.
- **`/profile/<username>`** — Fetches the user record and all their uploaded shots. Uses the username from the URL rather than the session, so any user can view any other user's profile.
- **`/collections`** — Shows all collections belonging to the logged-in user, queried via `session["user_id"]`.
- **`/collection/<id>`** — Uses a SQL JOIN across `shots` and `collections_shots` to retrieve all shots belonging to a specific collection.
- **`/`** — Simply redirects to `/browse`.

### `helpers.py`
Contains the `login_required` decorator. This is a Python function that wraps other functions — when applied to a route with `@login_required`, it checks whether `session["user_id"]` exists before allowing access. If the user is not logged in, they are redirected to `/login`. It uses `functools.wraps` to preserve the original function's identity and `*args, **kwargs` to pass through any URL parameters the original route expects.

### `cineref.db`
The SQLite database containing four tables:

- **`users`** — Stores username, hashed password, bio, career status, city, and country. Career status has five options: Student, First-jobber, Independent Filmmaker, Professional, and Enthusiast — chosen to reflect the real spectrum of the filmmaking community.
- **`shots`** — Stores all shot metadata including the image path, project name, director, cinematographer, year, work type, shot type, shot size, interior/exterior, time of day, aspect ratio, and description. The image itself is never stored in the database — only the file path, which points to `static/uploads/`.
- **`collections`** — Stores named collections belonging to a user, with a boolean `is_public` flag.
- **`collections_shots`** — A junction table implementing the many-to-many relationship between collections and shots. A shot can belong to multiple collections; a collection can contain multiple shots.

### `templates/`
All Jinja2 HTML templates. `layout.html` is the base template that all others extend. It contains the navigation bar, Google Fonts imports, global CSS, and the flash message loop. Child templates use `{% block main %}` to inject their content.

- **`register.html`** — Registration form with username, career status dropdown, country, password, and confirmation fields.
- **`login.html`** — Simple two-field login form.
- **`upload.html`** — The most complex form. Includes a file input with `accept="image/*"`, text inputs for project metadata, and six dropdown selectors for cinematic tags. The form uses `enctype="multipart/form-data"` to correctly encode the file upload.
- **`browse.html`** — Masonry layout grid with CSS columns and a JavaScript function that distributes cards into the shortest column to balance heights. Includes the rotating director quotes hero section with a JavaScript fade transition. Shot cards show film title and director on hover.
- **`shot.html`** — Full-bleed image with negative margin bleed, two-column metadata grid, and conditional description block.
- **`profile.html`** — User information section followed by a masonry grid of their uploaded shots.
- **`collections.html`** — Simple list of the user's collections as clickable links.
- **`collection.html`** — Masonry grid of shots inside a specific collection.

### `static/uploads/`
Where uploaded image files are stored on the filesystem. This directory is gitignored so that user uploads are not committed to version control.

### `.flaskenv`
Environment configuration file read by `python-dotenv`. Sets `FLASK_APP=app.py`, `FLASK_DEBUG=1`, and `FLASK_RUN_PORT=5001` so the development server runs consistently without manual environment variable exports.

---

## Key Design Decisions

**Why store the image path instead of the image in the database?**
Storing binary file data in a relational database is inefficient and creates bloated database files that are slow to query. The standard practice is to store files on the filesystem and keep only the path string in the database. This keeps the database lean and fast, and allows images to be served as static files directly by the web server.

**Why use `pbkdf2:sha256` instead of the default hashing method?**
The newer default hashing method in Werkzeug (`scrypt`) requires Python to be compiled with specific cryptographic support. Python 3.9 on macOS, compiled via Xcode Command Line Tools, does not include this support. Specifying `pbkdf2:sha256` explicitly ensures the application works regardless of the Python build environment, without sacrificing security.

**Why masonry layout instead of a fixed grid?**
Cinematic stills come in many aspect ratios — 1.85:1, 2.35:1, 4:3, 1:1, vertical. Forcing them into a fixed-height grid would require cropping, which distorts the composition and defeats the purpose of a cinematography reference tool. Masonry preserves the natural proportions of each frame, which is essential when the frames themselves are the content.

**Why `ORDER BY RANDOM()` on browse?**
A static sort order means users always see the same shots in the same sequence. Random ordering encourages discovery — every visit to the browse page feels different, surfacing shots that might otherwise stay buried at the bottom of a chronological list.

**Why separate `collections` and `collections_shots` tables?**
This implements a classic many-to-many relationship. A single `collections` table with a column listing shot IDs would violate database normalization and make querying extremely difficult. The junction table approach allows efficient SQL JOINs and makes the relationship easy to extend — adding or removing a shot from a collection is a single INSERT or DELETE on `collections_shots`.

---

## Challenges

The most significant technical challenge was understanding how file uploads differ from regular form data. Text inputs arrive via `request.form`, but files arrive via `request.files` — a separate object entirely. Missing this distinction causes the file to silently not arrive at the server. Related to this, the form itself requires `enctype="multipart/form-data"` or the browser will not encode the file correctly.

Another challenge was the Python virtual environment. The `.venv` was created but packages were never installed into it — they had been installed globally. This caused a split where Flask ran correctly (using global packages) but VS Code's Pylance analyzer showed errors (looking inside the empty venv). The fix required explicitly installing all packages into the venv using `.venv/bin/pip install` and configuring VS Code's interpreter path via `.vscode/settings.json`.

---

## Acknowledgements

CineRef was built as the final project for Harvard's CS50x: Introduction to Computer Science. The Flask application structure draws on patterns learned in Week 9 of the course. All cinematographic stills used for testing are from original short film productions.
