from django.core.management.base import BaseCommand
from core.models import Profile, Education, Skill, Project


class Command(BaseCommand):
    help = "Seed the database with the original portfolio content."

    def handle(self, *args, **options):
        profile, _ = Profile.objects.get_or_create(
            name="Abhindev Vijayan",
            defaults=dict(
                tagline="Developer | enthusiastic",
                status_label="Ready to connect",
                about=(
                    "A highly analytical software engineer equipped with a Master of "
                    "Computer Application (MCA) and BSc in Computer Science. My focus lies "
                    "in developing robust, scalable applications that solve complex data "
                    "problems and integrate advanced AI functionalities seamlessly into the "
                    "user experience."
                ),
                role="Full Stack Eng",
                focus_tags="Backend,AI",
                status_message="Building...",
                resume_url="https://github.com/AbhindevVijayan/Resume/blob/main/Abhindev_Vijayan_Resume%20(1).pdf",
                github_url="https://github.com/AbhindevVijayan",
                linkedin_url="https://www.linkedin.com/in/abhindev-vijayan-516454245/",
                email="abhindevvijayan18@gmail.com",
            ),
        )

        if not profile.education.exists():
            Education.objects.create(profile=profile, title="Master of Computer Application", period="2023-25", icon="school", order=0)
            Education.objects.create(profile=profile, title="BSc Computer Science", period="2020-23", icon="science", order=1)

        if not profile.skills.exists():
            skills = [
                ("Python", "code"), ("Django", "terminal"), ("JavaScript", "javascript"),
                ("Node.js", "hub"), ("CSS", "css"), (".NET", "integration_instructions"),
            ]
            for i, (name, icon) in enumerate(skills):
                Skill.objects.create(profile=profile, name=name, icon=icon, order=i)

        if not Project.objects.exists():
            Project.objects.create(
                title="MindVaultAI",
                description=(
                    "An advanced article summarization platform integrated with a localized "
                    "chatbot. Designed to process dense technical texts and provide "
                    "instantaneous, context-aware conversational querying."
                ),
                tags="AI/ML,Python", status="online", order=0,
            )
            Project.objects.create(
                title="VocalAI",
                description=(
                    "A complex AI-driven audio manipulation tool featuring song matching, "
                    "real-time pitch correction, and automated karaoke track generation by "
                    "isolating vocal frequencies."
                ),
                tags="Audio Processing,Django", status="beta", order=1,
            )
            Project.objects.create(
                title="Migrant DBMS",
                description=(
                    "A highly secure and scalable Database Management System engineered to "
                    "track, manage, and analyze records for migrant populations, focusing on "
                    "data integrity and fast retrieval speeds."
                ),
                tags="Database,.NET", status="deployed", order=2,
            )

        self.stdout.write(self.style.SUCCESS("Seed data created."))
