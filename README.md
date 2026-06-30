# Abhindev Vijayan Portfolio — Django + MySQL + MCP

Two pieces:

1. **`portfolio_project/`** — Django app. Renders your portfolio page from
   the database (Profile, Education, Skill, Project, ContactMessage models),
   handles the contact form, and exposes a small internal JSON API
   (`/api/...`) protected by a shared key.
2. **`mcp_server/`** — An MCP server that wraps that JSON API as tools
   (`list_projects`, `create_project`, `update_profile`, `list_contact_messages`,
   etc.), so an MCP-aware client (Claude Desktop, Claude Code, etc.) can
   manage your live site's content without you touching the DB or admin panel.

The MCP server never touches MySQL directly — it just calls the Django API.
That keeps validation and model logic in one place.

## 1. Django + MySQL setup

```bash
cd portfolio_project
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env           # then edit DB credentials, secret key, MCP_API_KEY
```

Create the MySQL database and user (in `mysql` shell):

```sql
CREATE DATABASE portfolio_db CHARACTER SET utf8mb4;
CREATE USER 'portfolio_user'@'%' IDENTIFIED BY 'changeme';
GRANT ALL PRIVILEGES ON portfolio_db.* TO 'portfolio_user'@'%';
FLUSH PRIVILEGES;
```

Then:

```bash
python manage.py migrate
python manage.py createsuperuser     # for /admin/
python manage.py seed_portfolio      # loads your original projects/skills/about text
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the live site, `/admin/` to manage
content manually as a fallback.

> mysqlclient needs MySQL dev headers to build. On Ubuntu:
> `sudo apt install default-libmysqlclient-dev build-essential pkg-config`
> On Mac: `brew install mysql-client pkg-config` then export the pkg-config
> path as brew tells you to.

### Internal API (used by the MCP server)

All endpoints require header `X-MCP-Key: <MCP_API_KEY>` (set in `.env`).

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/api/projects/` | list / create |
| GET/PATCH/DELETE | `/api/projects/<id>/` | read / update / delete one |
| GET/POST | `/api/skills/` | list / create |
| PATCH/DELETE | `/api/skills/<id>/` | update / delete one |
| GET/PATCH | `/api/profile/` | hero/about content |
| GET | `/api/messages/` | contact form submissions |

The public contact form posts to `/contact/` (CSRF-protected, no key needed).

## 2. MCP server setup

```bash
cd mcp_server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # MCP_API_KEY here MUST match the Django .env value
```

Test it runs:

```bash
python server.py
```

\
