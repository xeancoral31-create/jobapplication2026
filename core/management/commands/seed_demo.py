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
    {"name": "Information Technology", "icon": "laptop", "color": "#2563EB"},
    {"name": "Nursing & Healthcare",   "icon": "heart-pulse", "color": "#059669"},
    {"name": "Education",              "icon": "graduation-cap", "color": "#D97706"},
    {"name": "Engineering",            "icon": "settings", "color": "#4F46E5"},
    {"name": "Business & Finance",     "icon": "briefcase", "color": "#0D9488"},
    {"name": "Hospitality & Tourism",  "icon": "building", "color": "#E11D48"},
    {"name": "Government & Public Service", "icon": "landmark", "color": "#475569"},
    {"name": "Uniformed Personnel",    "icon": "shield-check", "color": "#0891B2"},
    {"name": "Other Professional Fields", "icon": "globe", "color": "#64748B"},
]

JOB_DEFINITIONS = [
    # Information Technology
    {
        "title": "Senior Cloud Infrastructure Engineer",
        "category": "Information Technology",
        "job_field": "information_technology",
        "department": "Infrastructure & DevOps",
        "job_type": "full_time",
        "experience_level": "senior",
        "location": "San Francisco, CA (Remote Friendly)",
        "is_remote": True,
        "salary_min": 140000,
        "salary_max": 185000,
        "tags": ["AWS", "Kubernetes", "Terraform", "Python"],
    },
    {
        "title": "Full Stack Developer",
        "category": "Information Technology",
        "job_field": "information_technology",
        "department": "Product Engineering",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Austin, TX",
        "is_remote": True,
        "salary_min": 95000,
        "salary_max": 130000,
        "tags": ["Python", "Django", "React", "PostgreSQL"],
    },
    {
        "title": "Cybersecurity Analyst",
        "category": "Information Technology",
        "job_field": "information_technology",
        "department": "Information Security",
        "job_type": "contractual",
        "experience_level": "mid",
        "location": "Washington, DC",
        "is_remote": False,
        "salary_min": 90000,
        "salary_max": 120000,
        "tags": ["SOC", "SIEM", "Incident Response", "Network Security"],
    },
    # Nursing and Healthcare
    {
        "title": "Registered Nurse (RN) - Intensive Care Unit",
        "category": "Nursing & Healthcare",
        "job_field": "nursing_healthcare",
        "department": "Critical Care Unit",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Boston, MA",
        "is_remote": False,
        "salary_min": 85000,
        "salary_max": 110000,
        "tags": ["Critical Care", "Patient Care", "BLS/ACLS", "ICU"],
    },
    {
        "title": "Pediatric Staff Nurse",
        "category": "Nursing & Healthcare",
        "job_field": "nursing_healthcare",
        "department": "Pediatrics Department",
        "job_type": "part_time",
        "experience_level": "entry",
        "location": "Chicago, IL",
        "is_remote": False,
        "salary_min": 45000,
        "salary_max": 62000,
        "tags": ["Pediatrics", "Patient Care", "Clinical Records"],
    },
    {
        "title": "Clinical Nurse Specialist",
        "category": "Nursing & Healthcare",
        "job_field": "nursing_healthcare",
        "department": "Nursing Education & Quality",
        "job_type": "contractual",
        "experience_level": "senior",
        "location": "New York, NY",
        "is_remote": False,
        "salary_min": 105000,
        "salary_max": 135000,
        "tags": ["Clinical Governance", "Staff Training", "Oncology"],
    },
    # Education
    {
        "title": "High School STEM Teacher",
        "category": "Education",
        "job_field": "education",
        "department": "Science & Mathematics Faculty",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Seattle, WA",
        "is_remote": False,
        "salary_min": 65000,
        "salary_max": 88000,
        "tags": ["Curriculum Design", "STEM", "Classroom Instruction"],
    },
    {
        "title": "University Academic Tutor",
        "category": "Education",
        "job_field": "education",
        "department": "Student Academic Support",
        "job_type": "part_time",
        "experience_level": "entry",
        "location": "Berkeley, CA",
        "is_remote": True,
        "salary_min": 32000,
        "salary_max": 48000,
        "tags": ["Tutoring", "Mentorship", "Higher Ed"],
    },
    {
        "title": "Instructional Design Intern",
        "category": "Education",
        "job_field": "education",
        "department": "E-Learning & Digital Pedagogy",
        "job_type": "internship",
        "experience_level": "entry",
        "location": "Remote",
        "is_remote": True,
        "salary_min": 25000,
        "salary_max": 35000,
        "tags": ["Canvas LMS", "Articulate 360", "Course Design"],
    },
    # Engineering
    {
        "title": "Senior Civil & Structural Engineer",
        "category": "Engineering",
        "job_field": "engineering",
        "department": "Infrastructure & Capital Projects",
        "job_type": "full_time",
        "experience_level": "senior",
        "location": "Denver, CO",
        "is_remote": False,
        "salary_min": 115000,
        "salary_max": 150000,
        "tags": ["AutoCAD", "Revit", "Structural Analysis", "PE License"],
    },
    {
        "title": "Mechanical Design Engineer",
        "category": "Engineering",
        "job_field": "engineering",
        "department": "Robotics & Hardware R&D",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Detroit, MI",
        "is_remote": False,
        "salary_min": 85000,
        "salary_max": 115000,
        "tags": ["SolidWorks", "Prototyping", "CAD/CAM", "Thermal Analysis"],
    },
    # Business & Finance
    {
        "title": "Senior Financial Analyst",
        "category": "Business & Finance",
        "job_field": "business_finance",
        "department": "Corporate FP&A",
        "job_type": "full_time",
        "experience_level": "senior",
        "location": "New York, NY",
        "is_remote": True,
        "salary_min": 110000,
        "salary_max": 145000,
        "tags": ["Financial Modeling", "Excel", "Budgeting", "Forecasting"],
    },
    {
        "title": "Accounting Specialist",
        "category": "Business & Finance",
        "job_field": "business_finance",
        "department": "General Ledger & Audit",
        "job_type": "temporary",
        "experience_level": "mid",
        "location": "Charlotte, NC",
        "is_remote": False,
        "salary_min": 60000,
        "salary_max": 78000,
        "tags": ["CPA", "QuickBooks", "Tax Compliance", "Reconciliation"],
    },
    {
        "title": "Finance Operations Intern",
        "category": "Business & Finance",
        "job_field": "business_finance",
        "department": "Treasury Operations",
        "job_type": "internship",
        "experience_level": "entry",
        "location": "Chicago, IL",
        "is_remote": False,
        "salary_min": 28000,
        "salary_max": 38000,
        "tags": ["Spreadsheets", "Financial Analysis", "Reporting"],
    },
    # Hospitality & Tourism
    {
        "title": "Front Desk & Guest Operations Manager",
        "category": "Hospitality & Tourism",
        "job_field": "hospitality_tourism",
        "department": "Front Office Operations",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Orlando, FL",
        "is_remote": False,
        "salary_min": 58000,
        "salary_max": 75000,
        "tags": ["Guest Relations", "Opera PMS", "Hospitality Management"],
    },
    {
        "title": "Event Coordinator & Banquets Specialist",
        "category": "Hospitality & Tourism",
        "job_field": "hospitality_tourism",
        "department": "Events & Catering",
        "job_type": "contractual",
        "experience_level": "mid",
        "location": "Las Vegas, NV",
        "is_remote": False,
        "salary_min": 52000,
        "salary_max": 68000,
        "tags": ["Event Planning", "Vendor Relations", "Catering"],
    },
    # Government & Public Service
    {
        "title": "Public Policy & Community Affairs Specialist",
        "category": "Government & Public Service",
        "job_field": "government_public_service",
        "department": "Community Engagement",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Sacramento, CA",
        "is_remote": False,
        "salary_min": 78000,
        "salary_max": 102000,
        "tags": ["Public Policy", "Community Outreach", "Government Relations"],
    },
    {
        "title": "Municipal Urban Planning Consultant",
        "category": "Government & Public Service",
        "job_field": "government_public_service",
        "department": "City Zoning & Development",
        "job_type": "contractual",
        "experience_level": "senior",
        "location": "Austin, TX",
        "is_remote": False,
        "salary_min": 92000,
        "salary_max": 125000,
        "tags": ["GIS", "Urban Planning", "Zoning Codes", "Public Hearings"],
    },
    # Uniformed Personnel - Army
    {
        "title": "Logistics & Supply Chain Specialist",
        "category": "Uniformed Personnel",
        "job_field": "uniformed_personnel",
        "uniformed_branch": "army",
        "department": "Quartermaster Corps / Army Logistics",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Fort Liberty, NC",
        "is_remote": False,
        "salary_min": 55000,
        "salary_max": 78000,
        "tags": ["Army", "Logistics", "Supply Chain", "Inventory Control"],
    },
    # Uniformed Personnel - Navy
    {
        "title": "Naval Electronics & Communications Technician",
        "category": "Uniformed Personnel",
        "job_field": "uniformed_personnel",
        "uniformed_branch": "navy",
        "department": "Naval Fleet Systems",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "San Diego, CA",
        "is_remote": False,
        "salary_min": 62000,
        "salary_max": 86000,
        "tags": ["Navy", "Telecommunications", "Avionics", "Radar"],
    },
    # Uniformed Personnel - Coast Guard
    {
        "title": "Maritime Safety & Search-and-Rescue Officer",
        "category": "Uniformed Personnel",
        "job_field": "uniformed_personnel",
        "uniformed_branch": "coast_guard",
        "department": "Maritime Safety & Rescue Wing",
        "job_type": "full_time",
        "experience_level": "mid",
        "location": "Miami, FL",
        "is_remote": False,
        "salary_min": 58000,
        "salary_max": 82000,
        "tags": ["Coast Guard", "Search and Rescue", "Maritime Law", "First Aid"],
    },
    # Uniformed Personnel - Police
    {
        "title": "Patrol Officer & Community Policing Liaison",
        "category": "Uniformed Personnel",
        "job_field": "uniformed_personnel",
        "uniformed_branch": "police",
        "department": "Patrol Division",
        "job_type": "full_time",
        "experience_level": "entry",
        "location": "Philadelphia, PA",
        "is_remote": False,
        "salary_min": 60000,
        "salary_max": 84000,
        "tags": ["Law Enforcement", "Community Outreach", "Public Safety", "Police"],
    },
    {
        "title": "Forensic Crime Scene Investigator",
        "category": "Uniformed Personnel",
        "job_field": "uniformed_personnel",
        "uniformed_branch": "police",
        "department": "Forensic Investigation Division",
        "job_type": "contractual",
        "experience_level": "senior",
        "location": "Atlanta, GA",
        "is_remote": False,
        "salary_min": 75000,
        "salary_max": 98000,
        "tags": ["Forensics", "Evidence Handling", "Criminalistics", "Police"],
    },
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
        import sys
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

        from accounts.models import EmployerProfile, ApplicantProfile
        from jobs.models import Category, Job, JobTag
        from applications.models import Application, Interview

        fake = Faker()
        Faker.seed(42)

        if options["flush"]:
            self.stdout.write(self.style.WARNING("Flushing existing demo data..."))
            Interview.objects.all().delete()
            Application.objects.all().delete()
            Job.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(username__startswith="demo_").delete()
            User.objects.filter(username__in=["admin", "employer1", "employer2", "employer3", "applicant1", "applicant2", "applicant3"]).delete()
            User.objects.filter(email__in=[
                "admin@workwise.dev",
                "employer1@workwise.dev",
                "employer2@workwise.dev",
                "employer3@workwise.dev",
                "applicant1@workwise.dev",
                "applicant2@workwise.dev",
                "applicant3@workwise.dev",
            ]).delete()

        self.stdout.write("Creating users...")

        # ── Admin ──────────────────────────────────────────────────
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@workwise.dev",
                "first_name": "Platform",
                "last_name": "Admin",
                "role": User.Role.ADMIN,
                "status": User.Status.ACTIVE,
                "is_staff": True,
                "is_superuser": True,
                "access_level": User.AccessLevel.SUPERADMIN,
            },
        )
        admin.email = "admin@workwise.dev"
        admin.first_name = "Platform"
        admin.last_name = "Admin"
        admin.role = User.Role.ADMIN
        admin.status = User.Status.ACTIVE
        admin.is_staff = True
        admin.is_superuser = True
        admin.access_level = User.AccessLevel.SUPERADMIN
        admin.set_password("admin1234")
        admin.save()
        self.stdout.write("  [+] admin (admin@workwise.dev / password: admin1234) -> /admin-panel/")

        # ── Employers ──────────────────────────────────────────────
        employers = []
        employer_data = [
            {
                "username": "employer1",
                "email": "employer1@workwise.dev",
                "first_name": "Elena",
                "last_name": "Vance",
                "password": "employer1234",
                "company_name": "Synapse Labs",
                "industry": "Technology & AI",
                "company_size": "201-500",
                "location": "San Francisco, CA",
            },
            {
                "username": "employer2",
                "email": "employer2@workwise.dev",
                "first_name": "Marcus",
                "last_name": "Webb",
                "password": "employer1234",
                "company_name": "Orbit Systems",
                "industry": "Aerospace & Defense",
                "company_size": "501-1000",
                "location": "Austin, TX",
            },
            {
                "username": "employer3",
                "email": "employer3@workwise.dev",
                "first_name": "Priya",
                "last_name": "Sharma",
                "password": "employer1234",
                "company_name": "Apex Global Services",
                "industry": "Finance & Healthcare",
                "company_size": "1000+",
                "location": "New York, NY",
            },
        ]
        for ed in employer_data:
            u, _ = User.objects.get_or_create(
                username=ed["username"],
                defaults={
                    "email": ed["email"],
                    "first_name": ed["first_name"],
                    "last_name": ed["last_name"],
                    "role": User.Role.EMPLOYER,
                    "status": User.Status.ACTIVE,
                    "location": ed["location"],
                    "bio": f"Hiring team at {ed['company_name']}.",
                },
            )
            u.role = User.Role.EMPLOYER
            u.status = User.Status.ACTIVE
            u.email = ed["email"]
            u.first_name = ed["first_name"]
            u.last_name = ed["last_name"]
            u.set_password(ed["password"])
            u.save()

            ep, _ = EmployerProfile.objects.get_or_create(user=u)
            ep.company_name = ed["company_name"]
            ep.industry = ed["industry"]
            ep.company_size = ed["company_size"]
            ep.company_description = f"{ed['company_name']} is an industry leader driving forward-thinking innovation and high-impact careers."
            ep.founded_year = 2018
            ep.save()
            u.employer_profile = ep

            self.stdout.write(f"  [+] {u.username} ({u.email} / {ed['company_name']} / password: {ed['password']}) -> /employer/")
            employers.append(u)

        # ── Applicants ─────────────────────────────────────────────
        applicants = []
        applicant_data = [
            {
                "username": "applicant1",
                "email": "applicant1@workwise.dev",
                "first_name": "Alex",
                "last_name": "Rivera",
                "password": "applicant1234",
                "headline": "Senior Cloud Infrastructure & Full Stack Engineer",
                "skills": "Python, Django, React, AWS, Docker, Kubernetes, PostgreSQL",
                "location": "San Francisco, CA",
            },
            {
                "username": "applicant2",
                "email": "applicant2@workwise.dev",
                "first_name": "Sam",
                "last_name": "Chen",
                "password": "applicant1234",
                "headline": "Registered Nurse (RN) & Critical Care Specialist",
                "skills": "Critical Care, BLS/ACLS, Patient Assessment, ICU, Emergency Care",
                "location": "Boston, MA",
            },
            {
                "username": "applicant3",
                "email": "applicant3@workwise.dev",
                "first_name": "David",
                "last_name": "Kim",
                "password": "applicant1234",
                "headline": "Senior Financial Analyst & Corporate FP&A Specialist",
                "skills": "Financial Modeling, Forecasting, Budgeting, Excel, SQL, Data Analysis",
                "location": "Chicago, IL",
            },
        ]
        for ad in applicant_data:
            u, _ = User.objects.get_or_create(
                username=ad["username"],
                defaults={
                    "email": ad["email"],
                    "first_name": ad["first_name"],
                    "last_name": ad["last_name"],
                    "role": User.Role.APPLICANT,
                    "status": User.Status.ACTIVE,
                    "location": ad["location"],
                    "bio": f"{ad['first_name']} {ad['last_name']} - {ad['headline']}",
                },
            )
            u.role = User.Role.APPLICANT
            u.status = User.Status.ACTIVE
            u.email = ad["email"]
            u.first_name = ad["first_name"]
            u.last_name = ad["last_name"]
            u.set_password(ad["password"])
            u.save()

            ap, _ = ApplicantProfile.objects.get_or_create(user=u)
            ap.headline = ad["headline"]
            ap.experience_level = "senior"
            ap.skills = ad["skills"]
            ap.available_from = datetime.date.today() + datetime.timedelta(days=14)
            ap.save()
            u.applicant_profile = ap

            self.stdout.write(f"  [+] {u.username} ({u.email} / {ad['first_name']} {ad['last_name']} / password: {ad['password']}) -> /applicant/")
            applicants.append(u)

        # ── Categories ─────────────────────────────────────────────
        self.stdout.write("Creating categories...")
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
                self.stdout.write(f"  [+] {cat.name}")

        # ── Jobs ────────────────────────────────────────────────────
        self.stdout.write("Creating jobs...")
        jobs = []
        for i, item in enumerate(JOB_DEFINITIONS):
            employer = employers[i % len(employers)]
            cat = cats.get(item["category"])
            title = item["title"]
            slug = slugify(f"{title}-{employer.employer_profile.company_name}")
            if Job.objects.filter(slug=slug).exists():
                slug = f"{slug}-{i}"

            job, created = Job.objects.get_or_create(
                slug=slug,
                defaults={
                    "employer": employer,
                    "category": cat,
                    "title": title,
                    "department": item.get("department", ""),
                    "job_field": item.get("job_field", "other"),
                    "uniformed_branch": item.get("uniformed_branch", "none"),
                    "description": f"{title} position at {employer.employer_profile.company_name}.\n\n" + "\n\n".join(fake.paragraphs(nb=3)),
                    "requirements": "\n".join([f"- {fake.sentence()}" for _ in range(5)]),
                    "responsibilities": "\n".join([f"- {fake.sentence()}" for _ in range(5)]),
                    "benefits": "\n".join(["- Comprehensive healthcare and retirement package", "- Professional development allowances", "- Generous paid time off"]),
                    "status": Job.Status.OPEN,
                    "job_type": item.get("job_type", Job.JobType.FULL_TIME),
                    "experience_level": item.get("experience_level", Job.ExperienceLevel.MID),
                    "location": item.get("location", fake.city() + ", USA"),
                    "is_remote": item.get("is_remote", False),
                    "salary_min": item.get("salary_min", 60000),
                    "salary_max": item.get("salary_max", 95000),
                    "salary_period": Job.SalaryPeriod.YEARLY,
                    "salary_currency": "USD",
                    "deadline": datetime.date.today() + datetime.timedelta(days=random.randint(30, 90)),
                },
            )
            if created:
                for tw in item.get("tags", []):
                    JobTag.objects.get_or_create(job=job, name=tw)
                self.stdout.write(f"  [+] [{job.get_job_type_display()}] {job.title} ({job.employer.employer_profile.company_name})")
            jobs.append(job)

        # ── Applications ────────────────────────────────────────────
        self.stdout.write("Creating applications...")
        applications = []

        # Applicant 1 (Alex Rivera) applied to multiple jobs across Synapse Labs & Orbit Systems
        alex = applicants[0]
        alex_jobs_and_statuses = [
            (jobs[0], Application.Status.SHORTLISTED),
            (jobs[1], Application.Status.UNDER_REVIEW),
            (jobs[2], Application.Status.SUBMITTED),
            (jobs[3], Application.Status.UNDER_REVIEW),
        ]
        for job, status in alex_jobs_and_statuses:
            app, created = Application.objects.get_or_create(
                applicant=alex,
                job=job,
                defaults={
                    "cover_letter": "I am excited to submit my application for this role. With extensive engineering experience in cloud architecture and resilient system design, I am confident in adding immediate value to your team.",
                    "status": status,
                    "portfolio_url": "https://alexrivera.dev",
                    "rating": 5,
                    "employer_notes": "Strong candidate portfolio with hands-on systems experience.",
                },
            )
            applications.append(app)
            if created:
                self.stdout.write(f"  [+] {alex.username} -> {job.title} [{status}]")

        # Applicant 2 (Sam Chen) candidate with scheduled interviews
        sam = applicants[1]
        sam_jobs_and_statuses = [
            (jobs[3], Application.Status.INTERVIEW_SCHEDULED),
            (jobs[4], Application.Status.INTERVIEW_SCHEDULED),
            (jobs[5], Application.Status.SHORTLISTED),
        ]
        for job, status in sam_jobs_and_statuses:
            app, created = Application.objects.get_or_create(
                applicant=sam,
                job=job,
                defaults={
                    "cover_letter": "I am passionate about high-quality clinical outcomes and compassionate patient care. My background in critical care and team collaboration aligns with your mission.",
                    "status": status,
                    "portfolio_url": "https://samchen-healthcare.dev",
                    "rating": 5,
                    "employer_notes": "Excellent clinical credentials and references.",
                },
            )
            applications.append(app)
            if created:
                self.stdout.write(f"  [+] {sam.username} -> {job.title} [{status}]")

        # Applicant 3 (David Kim)
        david = applicants[2]
        david_jobs_and_statuses = [
            (jobs[6], Application.Status.UNDER_REVIEW),
            (jobs[7], Application.Status.SUBMITTED),
        ]
        for job, status in david_jobs_and_statuses:
            app, created = Application.objects.get_or_create(
                applicant=david,
                job=job,
                defaults={
                    "cover_letter": "With a strong foundation in data-driven finance and operational analysis, I welcome the opportunity to contribute to your organization.",
                    "status": status,
                    "portfolio_url": "https://davidkim.finance",
                    "rating": 4,
                    "employer_notes": "Solid analytical skills and financial modeling.",
                },
            )
            applications.append(app)
            if created:
                self.stdout.write(f"  [+] {david.username} -> {job.title} [{status}]")

        # ── Interviews ──────────────────────────────────────────────
        self.stdout.write("Creating scheduled interviews for candidate pipeline...")
        # Schedule interviews for Sam Chen
        sam_interview_apps = [a for a in applications if a.applicant == sam and a.status == Application.Status.INTERVIEW_SCHEDULED]
        for i, app in enumerate(sam_interview_apps):
            if not app.interviews.exists():
                scheduled = timezone.now() + datetime.timedelta(days=i + 3, hours=i * 2 + 10)
                Interview.objects.create(
                    application=app,
                    scheduled_at=scheduled,
                    duration_minutes=60,
                    format=Interview.Format.VIDEO if i % 2 == 0 else Interview.Format.TECHNICAL,
                    meeting_link=f"https://meet.workwise.dev/interview-sam-{app.id}",
                    outcome=Interview.Outcome.PENDING,
                )
                self.stdout.write(f"  [+] Scheduled Interview for {sam.get_full_name()} ({sam.email}) @ {app.job.title} on {scheduled.strftime('%Y-%m-%d %H:%M')}")

        self.stdout.write(self.style.SUCCESS(
            "\n[OK] Seed complete! All accounts are active and functional:\n\n"
            "   [ADMIN] -> Redirects to /admin-panel/\n"
            "   * Username: admin | Email: admin@workwise.dev | Password: admin1234\n\n"
            "   [EMPLOYERS] -> Redirects to /employer/\n"
            "   * employer1 | employer1@workwise.dev (Synapse Labs) | Password: employer1234\n"
            "   * employer2 | employer2@workwise.dev (Orbit Systems) | Password: employer1234\n"
            "   * employer3 | employer3@workwise.dev (Apex Global Services) | Password: employer1234\n\n"
            "   [APPLICANTS] -> Redirects to /applicant/\n"
            "   * applicant1 | applicant1@workwise.dev (Alex Rivera) | Password: applicant1234\n"
            "   * applicant2 | applicant2@workwise.dev (Sam Chen - Scheduled Interviews) | Password: applicant1234\n"
            "   * applicant3 | applicant3@workwise.dev (David Kim) | Password: applicant1234\n\n"
            f"   Stats: {Category.objects.count()} Categories | {Job.objects.count()} Jobs | {Application.objects.count()} Applications | {Interview.objects.count()} Interviews\n"
        ))
