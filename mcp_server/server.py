"""
MCP server for the Abhindev Vijayan portfolio site.

This server doesn't talk to MySQL directly — it calls the Django app's
internal JSON API (see core/views.py), authenticated with a shared
X-MCP-Key header. That keeps all DB logic, validation, and model
definitions in one place (Django) while letting any MCP-aware client
(Claude, etc.) manage the live site's content: projects, skills, profile
info, and reading contact form submissions.

Run with:
    python server.py
or via the MCP CLI / your client's config (see README.md).
"""

import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

PORTFOLIO_BASE_URL = os.getenv("PORTFOLIO_BASE_URL", "http://127.0.0.1:8000")
MCP_API_KEY = os.getenv("MCP_API_KEY", "dev-mcp-key-change-me")

mcp = FastMCP("portfolio-manager")


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=PORTFOLIO_BASE_URL,
        headers={"X-MCP-Key": MCP_API_KEY, "Content-Type": "application/json"},
        timeout=15.0,
    )


# ---------- Projects ----------

@mcp.tool()
async def list_projects() -> dict:
    """List all projects on the portfolio site, published or not."""
    async with _client() as c:
        r = await c.get("/api/projects/")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def create_project(
    title: str,
    description: str,
    tags: str,
    status: str = "deployed",
    link: str = "",
    order: int = 0,
    is_published: bool = True,
) -> dict:
    """Create a new project entry.

    Args:
        title: Project name.
        description: Short description shown on the card.
        tags: Comma-separated tech/category tags, e.g. "AI/ML,Python".
        status: One of "online", "beta", "deployed", "archived".
        link: Optional URL the project card links to.
        order: Lower numbers show first.
        is_published: Whether it's visible on the live site.
    """
    payload = {
        "title": title, "description": description, "tags": tags,
        "status": status, "link": link, "order": order, "is_published": is_published,
    }
    async with _client() as c:
        r = await c.post("/api/projects/", json=payload)
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def update_project(project_id: int, fields: dict) -> dict:
    """Update an existing project. `fields` may include any of:
    title, description, tags (string or list), status, link, order, is_published.
    """
    async with _client() as c:
        r = await c.patch(f"/api/projects/{project_id}/", json=fields)
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def delete_project(project_id: int) -> dict:
    """Permanently delete a project by its ID."""
    async with _client() as c:
        r = await c.delete(f"/api/projects/{project_id}/")
        r.raise_for_status()
        return r.json()


# ---------- Skills ----------

@mcp.tool()
async def list_skills() -> dict:
    """List the technical skills shown on the site."""
    async with _client() as c:
        r = await c.get("/api/skills/")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def add_skill(name: str, icon: str = "code", order: int = 0) -> dict:
    """Add a new skill badge.

    Args:
        name: Skill label, e.g. "TypeScript".
        icon: Google Material Symbols icon name (e.g. "code", "javascript", "hub").
        order: Lower numbers show first.
    """
    async with _client() as c:
        r = await c.post("/api/skills/", json={"name": name, "icon": icon, "order": order})
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def delete_skill(skill_id: int) -> dict:
    """Remove a skill badge by ID."""
    async with _client() as c:
        r = await c.delete(f"/api/skills/{skill_id}/")
        r.raise_for_status()
        return r.json()


# ---------- Profile / hero / about ----------

@mcp.tool()
async def get_profile() -> dict:
    """Get the current hero/about section content (name, tagline, bio, links)."""
    async with _client() as c:
        r = await c.get("/api/profile/")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def update_profile(fields: dict) -> dict:
    """Update hero/about content. `fields` may include any of:
    name, tagline, status_label, about, role, focus_tags (string or list),
    status_message, resume_url, github_url, linkedin_url, email.
    """
    async with _client() as c:
        r = await c.patch("/api/profile/", json=fields)
        r.raise_for_status()
        return r.json()


# ---------- Contact messages ----------

@mcp.tool()
async def list_contact_messages() -> dict:
    """List all messages submitted through the site's contact form."""
    async with _client() as c:
        r = await c.get("/api/messages/")
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    mcp.run()
