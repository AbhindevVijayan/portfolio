import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Profile, Project, Skill, Education, ContactMessage


# ---------- Public site ----------

def index(request):
    profile = Profile.objects.first()
    projects = Project.objects.filter(is_published=True)
    skills = Skill.objects.filter(profile=profile) if profile else []
    education = Education.objects.filter(profile=profile) if profile else []
    return render(request, "core/index.html", {
        "profile": profile,
        "projects": projects,
        "skills": skills,
        "education": education,
    })


@require_http_methods(["POST"])
def submit_contact(request):
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    message = request.POST.get("message", "").strip()

    if not (name and email and message):
        return JsonResponse({"ok": False, "error": "All fields are required."}, status=400)

    ContactMessage.objects.create(name=name, email=email, message=message)
    return JsonResponse({"ok": True})


# ---------- Internal JSON API (used by the MCP server) ----------

def _check_key(request):
    key = request.headers.get("X-MCP-Key")
    return key == settings.MCP_API_KEY


def _unauthorized():
    return JsonResponse({"ok": False, "error": "Invalid or missing X-MCP-Key header."}, status=401)


def _project_to_dict(p: Project):
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "tags": p.tag_list(),
        "status": p.status,
        "link": p.link,
        "order": p.order,
        "is_published": p.is_published,
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_projects(request):
    if not _check_key(request):
        return _unauthorized()

    if request.method == "GET":
        projects = Project.objects.all()
        return JsonResponse({"ok": True, "projects": [_project_to_dict(p) for p in projects]})

    # POST -> create
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    required = ["title", "description", "tags"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return JsonResponse({"ok": False, "error": f"Missing fields: {missing}"}, status=400)

    project = Project.objects.create(
        title=data["title"],
        description=data["description"],
        tags=",".join(data["tags"]) if isinstance(data["tags"], list) else data["tags"],
        status=data.get("status", "deployed"),
        link=data.get("link", ""),
        order=data.get("order", 0),
        is_published=data.get("is_published", True),
    )
    return JsonResponse({"ok": True, "project": _project_to_dict(project)}, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def api_project_detail(request, pk):
    if not _check_key(request):
        return _unauthorized()

    project = get_object_or_404(Project, pk=pk)

    if request.method == "GET":
        return JsonResponse({"ok": True, "project": _project_to_dict(project)})

    if request.method == "DELETE":
        project.delete()
        return JsonResponse({"ok": True, "deleted": pk})

    # PUT / PATCH -> update
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    for field in ["title", "description", "status", "link", "order", "is_published"]:
        if field in data:
            setattr(project, field, data[field])
    if "tags" in data:
        tags = data["tags"]
        project.tags = ",".join(tags) if isinstance(tags, list) else tags

    project.save()
    return JsonResponse({"ok": True, "project": _project_to_dict(project)})


def _skill_to_dict(s: Skill):
    return {"id": s.id, "name": s.name, "icon": s.icon, "order": s.order}


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_skills(request):
    if not _check_key(request):
        return _unauthorized()

    profile = Profile.objects.first()

    if request.method == "GET":
        skills = Skill.objects.filter(profile=profile) if profile else []
        return JsonResponse({"ok": True, "skills": [_skill_to_dict(s) for s in skills]})

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    if not profile:
        profile = Profile.objects.create()

    if not data.get("name"):
        return JsonResponse({"ok": False, "error": "Missing field: name"}, status=400)

    skill = Skill.objects.create(
        profile=profile,
        name=data["name"],
        icon=data.get("icon", "code"),
        order=data.get("order", 0),
    )
    return JsonResponse({"ok": True, "skill": _skill_to_dict(skill)}, status=201)


@csrf_exempt
@require_http_methods(["DELETE", "PATCH"])
def api_skill_detail(request, pk):
    if not _check_key(request):
        return _unauthorized()

    skill = get_object_or_404(Skill, pk=pk)

    if request.method == "DELETE":
        skill.delete()
        return JsonResponse({"ok": True, "deleted": pk})

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    for field in ["name", "icon", "order"]:
        if field in data:
            setattr(skill, field, data[field])
    skill.save()
    return JsonResponse({"ok": True, "skill": _skill_to_dict(skill)})


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH"])
def api_profile(request):
    if not _check_key(request):
        return _unauthorized()

    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create()

    if request.method == "GET":
        return JsonResponse({"ok": True, "profile": {
            "id": profile.id,
            "name": profile.name,
            "tagline": profile.tagline,
            "status_label": profile.status_label,
            "about": profile.about,
            "role": profile.role,
            "focus_tags": profile.focus_list(),
            "status_message": profile.status_message,
            "resume_url": profile.resume_url,
            "github_url": profile.github_url,
            "linkedin_url": profile.linkedin_url,
            "email": profile.email,
        }})

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    for field in ["name", "tagline", "status_label", "about", "role",
                  "status_message", "resume_url", "github_url", "linkedin_url", "email"]:
        if field in data:
            setattr(profile, field, data[field])
    if "focus_tags" in data:
        ft = data["focus_tags"]
        profile.focus_tags = ",".join(ft) if isinstance(ft, list) else ft

    profile.save()
    return JsonResponse({"ok": True, "id": profile.id})


@require_http_methods(["GET"])
def api_messages(request):
    if not _check_key(request):
        return _unauthorized()

    messages = ContactMessage.objects.all()
    return JsonResponse({"ok": True, "messages": [
        {
            "id": m.id, "name": m.name, "email": m.email, "message": m.message,
            "created_at": m.created_at.isoformat(), "is_read": m.is_read,
        } for m in messages
    ]})
