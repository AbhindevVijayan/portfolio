from django.db import models


class Profile(models.Model):
    """Singleton-ish hero/about content. Only one row is expected, but
    nothing enforces that at the DB level — manage it via the admin or MCP."""
    name = models.CharField(max_length=120, default="Abhindev Vijayan")
    tagline = models.CharField(max_length=200, default="Developer | enthusiastic")
    status_label = models.CharField(max_length=80, default="Ready to connect")
    about = models.TextField(
        default="A highly analytical software engineer equipped with a Master "
        "of Computer Application (MCA) and BSc in Computer Science."
    )
    role = models.CharField(max_length=120, default="Full Stack Eng")
    focus_tags = models.CharField(
        max_length=200, default="Backend,AI",
        help_text="Comma-separated, shown in the terminal hero panel"
    )
    status_message = models.CharField(max_length=80, default="Building...")
    resume_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def focus_list(self):
        return [t.strip() for t in self.focus_tags.split(",") if t.strip()]


class Education(models.Model):
    profile = models.ForeignKey(Profile, related_name="education", on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    period = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, default="school", help_text="Material Symbols icon name")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} ({self.period})"


class Skill(models.Model):
    profile = models.ForeignKey(Profile, related_name="skills", on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    icon = models.CharField(max_length=50, default="code", help_text="Material Symbols icon name")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ("online", "Online"),
        ("beta", "Beta"),
        ("deployed", "Deployed"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField()
    tags = models.CharField(max_length=200, help_text="Comma-separated, e.g. AI/ML,Python")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="deployed")
    link = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> @ {self.created_at:%Y-%m-%d %H:%M}"
