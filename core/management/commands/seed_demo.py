"""
core/management/commands/seed_demo.py

Usage:
    python manage.py seed_demo
    python manage.py seed_demo --flush   # wipes existing data first

Creates:
  • 1 admin user
  • 2 employer users + EmployerProfile
  • 3 applicant users + ApplicantProfile
  • 5 categories
  • 8 jobs (across categories / employers)
  • 9 applications (3 applicants × 3 jobs each, different combos)
  • 3 interviews
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

import random
import datetime

try:
    from faker import Faker
except ImportError:
    raise CommandError("Faker is not installed. Run: pip install Faker")

User = get_user_model()

CATEGORIES = [
    {"name": "Engineering", "icon": "💻", "color": "#6C63FF"},
    {"name": "Design",      "icon": "🎨", "color": "#FF6584"},
    {"name": "Data & AI",   "icon": "📊", "color": "#43B89C"},
    {"name": "Product",     "icon": "🗂️", "color": "#F7B731"},
    {"name": "Marketing",   "icon": "📣", "color": "#FC5C65"},
]

JOB_TITLES = [
    ("Senior Django Engineer",      "Engineering"),
    ("Frontend Developer (React)",  "Engineering"),
    ("Data Scientist — NLP",        "Data & AI"),
    ("Product Designer",            "Design"),
    ("Growth Marketing Manager",    "Marketing"),
    ("Product Manager, Core",       "Product"),
    ("Machine Learning Engineer",   "Data & AI"),
    ("Brand & Motion Designer",     "Design"),
]


class Command(BaseCommand):
    help = "Seed the database with demo users, jobs, and applications."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing seed data before creating new records.",
        )

    def handle(self, *args, **options):
        from accounts.models import EmployerProfile, ApplicantProfile
        from jobs.models import Category, Job, JobTag
        from applications.models import Application, Interview

        fake = Faker()
        Faker.seed(42)

        if options["flush"]:
            self.stdout.write(self.style.WARNING("Flushing existing demo data…"))
            Interview.objects.all().delete()
            Application.objects.all().delete()
            Job.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(username__startswith="demo_").delete()
            User.objects.filter(username="admin").delete()

        self.stdout.write("Creating users…")

        # ── Admin ──────────────────────────────────────────────────
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@inkboard.dev",
                "first_name": "Site",
                "last_name": "Admin",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin1234")
            admin.save()
            self.stdout.write(f"  ✓ admin  (password: admin1234)")
        else:
            self.stdout.write(f"  ~ admin already exists")

        # ── Employers ──────────────────────────────────────────────
        employers = []
        employer_data = [
            {
                "username": "demo_employer1",
                "email": "employer1@inkboard.dev",
                "first_name": "Priya",
                "last_name": "Sharma",
                "company_name": "Synapse Labs",
                "industry": "Artificial Intelligence",
                "company_size": "51-200",
            },
            {
                "username": "demo_employer2",
                "email": "employer2@inkboard.dev",
                "first_name": "Marcus",
                "last_name": "Webb",
                "company_name": "Orbit Systems",
                "industry": "Cloud Infrastructure",
                "company_size": "201-1000",
            },
        ]
        for ed in employer_data:
            u, created = User.objects.get_or_create(
                username=ed["username"],
                defaults={
                    "email": ed["email"],
                    "first_name": ed["first_name"],
                    "last_name": ed["last_name"],
                    "role": User.Role.EMPLOYER,
                    "location": fake.city(),
                    "bio": fake.sentence(nb_words=20),
                },
            )
            if created:
                u.set_password("password123")
                u.save()
                self.stdout.write(f"  ✓ {u.username}")
            ep, _ = EmployerProfile.objects.get_or_create(
                user=u,
                defaults={
                    "company_name": ed["company_name"],
                    "industry": ed["industry"],
                    "company_size": ed["company_size"],
                    "company_description": fake.paragraph(nb_sentences=4),
                    "founded_year": random.randint(2010, 2020),
                },
            )
            employers.append(u)

        # ── Applicants ─────────────────────────────────────────────
        applicants = []
        applicant_data = [
            {"username": "demo_applicant1", "email": "applicant1@inkboard.dev", "first_name": "Alex",    "last_name": "Chen",   "headline": "Full-stack Engineer | Django & React"},
            {"username": "demo_applicant2", "email": "applicant2@inkboard.dev", "first_name": "Fatima",  "last_name": "Nkosi",  "headline": "Data Scientist | Python, SQL, ML"},
            {"username": "demo_applicant3", "email": "applicant3@inkboard.dev", "first_name": "Jamie",   "last_name": "Rivera", "headline": "Senior Product Designer | Figma, Design Systems"},
        ]
        for ad in applicant_data:
            u, created = User.objects.get_or_create(
                username=ad["username"],
                defaults={
                    "email": ad["email"],
                    "first_name": ad["first_name"],
                    "last_name": ad["last_name"],
                    "role": User.Role.APPLICANT,
                    "location": fake.city(),
                    "bio": fake.sentence(nb_words=25),
                },
            )
            if created:
                u.set_password("password123")
                u.save()
                self.stdout.write(f"  ✓ {u.username}")
            ApplicantProfile.objects.get_or_create(
                user=u,
                defaults={
                    "headline": ad["headline"],
                    "experience_level": random.choice(["entry", "mid", "senior"]),
                    "skills": ", ".join(fake.words(nb=8)),
                    "available_from": datetime.date.today() + datetime.timedelta(days=random.randint(7, 60)),
                },
            )
            applicants.append(u)

        # ── Categories ─────────────────────────────────────────────
        self.stdout.write("Creating categories…")
        cats = {}
        for cd in CATEGORIES:
            slug = slugify(cd["name"])
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": cd["name"],
                    "icon": cd["icon"],
                    "color": cd["color"],
                    "description": fake.sentence(nb_words=12),
                },
            )
            cats[cd["name"]] = cat
            if created:
                self.stdout.write(f"  ✓ {cat.name}")

        # ── Jobs ────────────────────────────────────────────────────
        self.stdout.write("Creating jobs…")
        jobs = []
        for i, (title, cat_name) in enumerate(JOB_TITLES):
            employer = employers[i % len(employers)]
            cat = cats.get(cat_name)
            slug = slugify(f"{title}-{employer.employer_profile.company_name}")
            # Make slug unique if already exists
            if Job.objects.filter(slug=slug).exists():
                slug = f"{slug}-{i}"

            job, created = Job.objects.get_or_create(
                slug=slug,
                defaults={
                    "employer": employer,
                    "category": cat,
                    "title": title,
                    "description": "\n\n".join(fake.paragraphs(nb=3)),
                    "requirements": "\n".join([f"• {fake.sentence()}" for _ in range(5)]),
                    "responsibilities": "\n".join([f"• {fake.sentence()}" for _ in range(5)]),
                    "benefits": "\n".join([f"• {fake.sentence()}" for _ in range(4)]),
                    "status": Job.Status.OPEN,
                    "job_type": random.choice([
                        Job.JobType.FULL_TIME,
                        Job.JobType.CONTRACT,
                        Job.JobType.REMOTE if hasattr(Job.JobType, "REMOTE") else Job.JobType.FULL_TIME,
                    ]),
                    "experience_level": random.choice([
                        Job.ExperienceLevel.MID,
                        Job.ExperienceLevel.SENIOR,
                        Job.ExperienceLevel.ENTRY,
                    ]),
                    "location": fake.city() + ", " + fake.country_code(),
                    "is_remote": random.choice([True, False]),
                    "salary_min": random.choice([70_000, 90_000, 110_000, 130_000]),
                    "salary_max": random.choice([130_000, 160_000, 180_000, 210_000]),
                    "salary_period": Job.SalaryPeriod.YEARLY,
                    "salary_currency": "USD",
                    "deadline": datetime.date.today() + datetime.timedelta(days=random.randint(30, 90)),
                },
            )
            if created:
                # Add 3–5 tags
                tag_words = fake.words(nb=random.randint(3, 5))
                for tw in tag_words:
                    JobTag.objects.get_or_create(job=job, name=tw.capitalize())
                self.stdout.write(f"  ✓ {job.title} @ {employer.employer_profile.company_name}")
            jobs.append(job)

        # ── Applications ────────────────────────────────────────────
        self.stdout.write("Creating applications…")
        statuses = [
            Application.Status.SUBMITTED,
            Application.Status.UNDER_REVIEW,
            Application.Status.SHORTLISTED,
            Application.Status.INTERVIEW_SCHEDULED,
            Application.Status.REJECTED,
        ]
        applications = []
        # Each applicant applies to 3 distinct jobs
        job_pool = jobs[:6]
        for ai, applicant in enumerate(applicants):
            selected_jobs = job_pool[ai * 2 : ai * 2 + 3]
            for job in selected_jobs:
                app, created = Application.objects.get_or_create(
                    applicant=applicant,
                    job=job,
                    defaults={
                        "cover_letter": fake.paragraph(nb_sentences=5),
                        "status": random.choice(statuses),
                        "portfolio_url": f"https://portfolio.example.com/{applicant.username}",
                        "rating": random.randint(3, 5),
                        "employer_notes": fake.sentence(),
                    },
                )
                if created:
                    self.stdout.write(f"  ✓ {applicant.username} → {job.title}")
                applications.append(app)

        # ── Interviews ──────────────────────────────────────────────
        self.stdout.write("Creating interviews…")
        interview_apps = [a for a in applications if a.status in [
            Application.Status.SHORTLISTED,
            Application.Status.INTERVIEW_SCHEDULED,
        ]][:3]
        for app in interview_apps:
            if not app.interviews.exists():
                scheduled = timezone.now() + datetime.timedelta(days=random.randint(3, 14))
                Interview.objects.create(
                    application=app,
                    scheduled_at=scheduled,
                    duration_minutes=random.choice([45, 60, 90]),
                    format=random.choice([
                        Interview.Format.VIDEO,
                        Interview.Format.TECHNICAL,
                        Interview.Format.PHONE,
                    ]),
                    meeting_link="https://meet.example.com/inkboard-interview",
                    outcome=Interview.Outcome.PENDING,
                )
                self.stdout.write(f"  ✓ Interview for {app.applicant.username} @ {app.job.title}")

        self.stdout.write(self.style.SUCCESS(
            "\n✅  Seed complete!\n"
            f"   Admin:      admin / admin1234\n"
            f"   Employers:  demo_employer1, demo_employer2 / password123\n"
            f"   Applicants: demo_applicant1, demo_applicant2, demo_applicant3 / password123\n"
            f"   Categories: {Category.objects.count()}\n"
            f"   Jobs:       {Job.objects.count()}\n"
            f"   Apps:       {Application.objects.count()}\n"
            f"   Interviews: {Interview.objects.count()}\n"
        ))
