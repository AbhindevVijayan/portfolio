from django.contrib import admin
from .models import Profile, Education, Skill, Project, ContactMessage


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [EducationInline, SkillInline]
    list_display = ("name", "tagline", "updated_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "order", "is_published", "updated_at")
    list_filter = ("status", "is_published")
    search_fields = ("title", "description", "tags")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_read")
    list_filter = ("is_read",)
    readonly_fields = ("name", "email", "message", "created_at")
