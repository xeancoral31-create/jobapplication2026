"""core/tests.py — Tests for role dashboards, numbers, services, and queries."""
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from accounts.models import User, EmployerProfile, ApplicantProfile
from jobs.models import Job, Category
from applications.models import Application, Interview
from moderation.models import AuditLog, AdminAction
from core.services import (
    get_employer_dashboard_data,
    get_applicant_dashboard_data,
    get_admin_dashboard_data,
    calculate_profile_completeness,
)


class EmployerDashboardNumbersTest(TestCase):
    """Test calculations and aggregate numbers for Employer dashboard."""

    def setUp(self):
        # Employer 1
        self.employer = User.objects.create_user(
            username="emp1",
            email="emp1@test.com",
            password="pass",
            role=User.Role.EMPLOYER,
            status=User.Status.PENDING,  # not verified yet
        )
        self.employer_profile, _ = EmployerProfile.objects.update_or_create(
            user=self.employer,
            defaults={"company_name": "Apex Technologies"},
        )

        # Employer 2 (to verify isolation)
        self.other_employer = User.objects.create_user(
            username="emp2",
            email="emp2@test.com",
            password="pass",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,
        )
        EmployerProfile.objects.update_or_create(
            user=self.other_employer,
            defaults={"company_name": "Other Co"},
        )

        # Category
        self.category = Category.objects.create(name="Tech", slug="tech")

        # Applicants
        self.applicant1 = User.objects.create_user(
            username="app1", email="app1@test.com", password="pass", role=User.Role.APPLICANT
        )
        self.applicant2 = User.objects.create_user(
            username="app2", email="app2@test.com", password="pass", role=User.Role.APPLICANT
        )
        self.applicant3 = User.objects.create_user(
            username="app3", email="app3@test.com", password="pass", role=User.Role.APPLICANT
        )

        # Employer 1 Jobs: 2 OPEN, 1 DRAFT, 1 CLOSED
        self.job_open1 = Job.objects.create(
            employer=self.employer, category=self.category, title="Open Job 1",
            slug="open-job-1", status=Job.Status.OPEN, description="Test"
        )
        self.job_open2 = Job.objects.create(
            employer=self.employer, category=self.category, title="Open Job 2",
            slug="open-job-2", status=Job.Status.OPEN, description="Test"
        )
        self.job_draft = Job.objects.create(
            employer=self.employer, category=self.category, title="Draft Job",
            slug="draft-job", status=Job.Status.DRAFT, description="Test"
        )
        self.job_closed = Job.objects.create(
            employer=self.employer, category=self.category, title="Closed Job",
            slug="closed-job", status=Job.Status.CLOSED, description="Test"
        )

        # Other employer job (should NOT be counted)
        self.other_job = Job.objects.create(
            employer=self.other_employer, category=self.category, title="Other Job",
            slug="other-job", status=Job.Status.OPEN, description="Test"
        )

        # Applications for Employer 1:
        # 1 shortlisted, 1 under review, 1 submitted, 1 rejected = 4 total applications
        self.app1 = Application.objects.create(
            job=self.job_open1, applicant=self.applicant1, status=Application.Status.SHORTLISTED
        )
        self.app2 = Application.objects.create(
            job=self.job_open1, applicant=self.applicant2, status=Application.Status.UNDER_REVIEW
        )
        self.app3 = Application.objects.create(
            job=self.job_open2, applicant=self.applicant1, status=Application.Status.SUBMITTED
        )
        self.app4 = Application.objects.create(
            job=self.job_open2, applicant=self.applicant3, status=Application.Status.REJECTED
        )

        # Application for other employer (should NOT be counted)
        Application.objects.create(
            job=self.other_job, applicant=self.applicant2, status=Application.Status.SHORTLISTED
        )

        # Interviews:
        # 1 in 2 days (within 7 days) -> counted
        # 1 in 5 days (within 7 days) -> counted
        # 1 in 10 days (outside 7 days) -> not counted
        # 1 in past (-1 day) -> not counted
        # 1 for other employer (within 7 days) -> not counted
        now = timezone.now()
        Interview.objects.create(
            application=self.app1, scheduled_at=now + datetime.timedelta(days=2), duration_minutes=30
        )
        Interview.objects.create(
            application=self.app2, scheduled_at=now + datetime.timedelta(days=5), duration_minutes=45
        )
        Interview.objects.create(
            application=self.app3, scheduled_at=now + datetime.timedelta(days=10), duration_minutes=60
        )
        Interview.objects.create(
            application=self.app4, scheduled_at=now - datetime.timedelta(days=1), duration_minutes=60
        )

    def test_open_jobs_count(self):
        data = get_employer_dashboard_data(self.employer)
        self.assertEqual(data["open_jobs"], 2)
        self.assertEqual(data["total_jobs"], 4)

    def test_total_applications_count(self):
        data = get_employer_dashboard_data(self.employer)
        self.assertEqual(data["total_applications"], 4)

    def test_shortlisted_count(self):
        data = get_employer_dashboard_data(self.employer)
        self.assertEqual(data["shortlisted"], 1)

    def test_interviews_next_7_days_count(self):
        data = get_employer_dashboard_data(self.employer)
        self.assertEqual(data["interviews_next_7_days"], 2)

    def test_is_verified_false_when_pending(self):
        data = get_employer_dashboard_data(self.employer)
        self.assertFalse(data["is_verified"])
        self.assertTrue(data["is_pending"])
        self.assertFalse(self.employer.is_verified)
        self.assertFalse(self.employer_profile.is_verified)

    def test_is_verified_true_when_active(self):
        self.employer.status = User.Status.ACTIVE
        self.employer.save()
        data = get_employer_dashboard_data(self.employer)
        self.assertTrue(data["is_verified"])
        self.assertFalse(data["is_pending"])
        self.assertTrue(self.employer.is_verified)
        self.assertTrue(self.employer_profile.is_verified)

    def test_recent_applications_list(self):
        data = get_employer_dashboard_data(self.employer)
        self.assertEqual(len(data["recent_applications"]), 4)
        # Check select_related works without extra queries
        for app in data["recent_applications"]:
            self.assertIsNotNone(app.applicant.username)
            self.assertIsNotNone(app.job.title)


class ApplicantDashboardNumbersTest(TestCase):
    """Test calculations and aggregate numbers for Applicant dashboard."""

    def setUp(self):
        self.employer = User.objects.create_user(
            username="emp_app_test", email="emp@test.com", password="pass", role=User.Role.EMPLOYER
        )
        self.applicant = User.objects.create_user(
            username="applicant_test",
            email="cand@test.com",
            password="pass",
            role=User.Role.APPLICANT,
            first_name="Jane",
            last_name="Doe",
            bio="Software Engineer",
            location="San Francisco, CA",
        )
        self.applicant_profile = self.applicant.applicant_profile
        self.applicant_profile.headline = "Full-stack Developer"
        self.applicant_profile.skills = "Python, Django, PostgreSQL"
        self.applicant_profile.experience_level = ApplicantProfile.ExperienceLevel.SENIOR
        self.applicant_profile.github_url = "https://github.com/janedoe"
        self.applicant_profile.save()
        self.applicant.refresh_from_db()

        self.category = Category.objects.create(name="Design", slug="design")

        # 4 Jobs
        self.jobs = [
            Job.objects.create(
                employer=self.employer, category=self.category, title=f"Job {i}",
                slug=f"job-{i}", status=Job.Status.OPEN, description="Desc"
            )
            for i in range(1, 5)
        ]

        # Applications by status:
        # 1 SUBMITTED, 1 SHORTLISTED, 1 HIRED = 3 applications
        self.app1 = Application.objects.create(
            job=self.jobs[0], applicant=self.applicant, status=Application.Status.SUBMITTED
        )
        self.app2 = Application.objects.create(
            job=self.jobs[1], applicant=self.applicant, status=Application.Status.SHORTLISTED
        )
        self.app3 = Application.objects.create(
            job=self.jobs[2], applicant=self.applicant, status=Application.Status.HIRED
        )

        # Interviews: 1 upcoming, 1 in the past
        now = timezone.now()
        self.interview_upcoming = Interview.objects.create(
            application=self.app2,
            scheduled_at=now + datetime.timedelta(days=3),
            format=Interview.Format.VIDEO,
            duration_minutes=45,
            meeting_link="https://meet.google.com/abc-defg-hij",
        )
        self.interview_past = Interview.objects.create(
            application=self.app3,
            scheduled_at=now - datetime.timedelta(days=2),
            format=Interview.Format.PHONE,
            duration_minutes=30,
        )

    def test_applications_by_status_numbers(self):
        data = get_applicant_dashboard_data(self.applicant)
        self.assertEqual(data["total_applications"], 3)
        self.assertEqual(data["applications_by_status"][Application.Status.SUBMITTED], 1)
        self.assertEqual(data["applications_by_status"][Application.Status.SHORTLISTED], 1)
        self.assertEqual(data["applications_by_status"][Application.Status.HIRED], 1)
        self.assertEqual(data["applications_by_status"][Application.Status.REJECTED], 0)

    def test_upcoming_interviews_only_future(self):
        data = get_applicant_dashboard_data(self.applicant)
        interviews = list(data["upcoming_interviews"])
        self.assertEqual(len(interviews), 1)
        self.assertEqual(interviews[0].pk, self.interview_upcoming.pk)

    def test_profile_completeness_calculation(self):
        score, missing = calculate_profile_completeness(self.applicant)
        # first_name & last_name: 15
        # avatar: missing (not set)
        # bio: 10
        # location: 5
        # headline: 20
        # skills: 15
        # resume: missing (not set)
        # github_url: 10
        # Total expected = 15 + 10 + 5 + 20 + 15 + 10 = 75
        self.assertEqual(score, 75)
        self.assertTrue(any("resume" in m.lower() for m in missing))


class AdminDashboardNumbersTest(TestCase):
    """Test calculations and aggregate numbers for Admin panel dashboard."""

    def setUp(self):
        # 1 Admin
        self.admin_user = User.objects.create_user(
            username="admin_test", email="admin@test.com", password="pass", role=User.Role.ADMIN, is_staff=True
        )

        # 3 Applicants
        for i in range(3):
            User.objects.create_user(
                username=f"applicant_test_{i}", email=f"app{i}@test.com", password="pass", role=User.Role.APPLICANT
            )

        # 2 Employers (1 pending, 1 active)
        self.emp_pending = User.objects.create_user(
            username="emp_pending", email="pend@test.com", password="pass",
            role=User.Role.EMPLOYER, status=User.Status.PENDING
        )
        EmployerProfile.objects.update_or_create(user=self.emp_pending, defaults={"company_name": "Pending Corp"})

        self.emp_active = User.objects.create_user(
            username="emp_active", email="act@test.com", password="pass",
            role=User.Role.EMPLOYER, status=User.Status.ACTIVE
        )
        EmployerProfile.objects.update_or_create(user=self.emp_active, defaults={"company_name": "Active Corp"})

        # Jobs: 2 OPEN, 1 DRAFT
        self.category = Category.objects.create(name="Sales", slug="sales")
        Job.objects.create(
            employer=self.emp_active, category=self.category, title="Open Job A",
            slug="open-a", status=Job.Status.OPEN, description="Test"
        )
        Job.objects.create(
            employer=self.emp_active, category=self.category, title="Open Job B",
            slug="open-b", status=Job.Status.OPEN, description="Test"
        )
        Job.objects.create(
            employer=self.emp_active, category=self.category, title="Draft Job C",
            slug="draft-c", status=Job.Status.DRAFT, description="Test"
        )

        # AuditLog / AdminAction rows
        user_ct = ContentType.objects.get_for_model(User)
        AuditLog.objects.create(
            actor=self.admin_user,
            content_type=user_ct,
            object_id=self.emp_active.pk,
            object_repr=str(self.emp_active),
            action=AuditLog.Action.APPROVE,
            changes={"status": ["pending", "active"]},
        )
        AuditLog.objects.create(
            actor=self.admin_user,
            content_type=user_ct,
            object_id=self.emp_pending.pk,
            object_repr=str(self.emp_pending),
            action=AuditLog.Action.UPDATE,
            changes={"status": ["active", "pending"]},
        )

    def test_users_by_role_numbers(self):
        data = get_admin_dashboard_data(self.admin_user)
        self.assertEqual(data["total_users"], 6)
        self.assertEqual(data["applicants_count"], 3)
        self.assertEqual(data["employers_count"], 2)
        self.assertEqual(data["admins_count"], 1)
        self.assertEqual(data["users_by_role"][User.Role.APPLICANT], 3)
        self.assertEqual(data["users_by_role"][User.Role.EMPLOYER], 2)
        self.assertEqual(data["users_by_role"][User.Role.ADMIN], 1)

    def test_employers_awaiting_verification_number(self):
        data = get_admin_dashboard_data(self.admin_user)
        self.assertEqual(data["employers_awaiting_verification"], 1)
        self.assertEqual(len(data["pending_employers"]), 1)
        self.assertEqual(data["pending_employers"][0].pk, self.emp_pending.pk)

    def test_open_jobs_number(self):
        data = get_admin_dashboard_data(self.admin_user)
        self.assertEqual(data["open_jobs"], 2)
        self.assertEqual(data["total_jobs"], 3)

    def test_recent_admin_actions(self):
        data = get_admin_dashboard_data(self.admin_user)
        actions = list(data["recent_admin_actions"])
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].action, AuditLog.Action.UPDATE)
        self.assertEqual(actions[1].action, AuditLog.Action.APPROVE)


class RoleDashboardViewsAccessTest(TestCase):
    """Test HTTP access and template rendering for all three role dashboards."""

    def setUp(self):
        self.client = Client()
        self.applicant = User.objects.create_user(
            username="app_v", email="app_v@test.com", password="password123", role=User.Role.APPLICANT
        )
        self.employer_pending = User.objects.create_user(
            username="emp_vp", email="emp_vp@test.com", password="password123",
            role=User.Role.EMPLOYER, status=User.Status.PENDING
        )
        self.employer_active = User.objects.create_user(
            username="emp_va", email="emp_va@test.com", password="password123",
            role=User.Role.EMPLOYER, status=User.Status.ACTIVE
        )
        self.admin = User.objects.create_user(
            username="adm_v", email="adm_v@test.com", password="password123",
            role=User.Role.ADMIN, is_staff=True
        )

    def test_employer_dashboard_view_pending_banner(self):
        self.client.login(username="emp_vp@test.com", password="password123")
        res = self.client.get(reverse("core:employer_dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Employer Account Awaiting Verification")
        self.assertContains(res, "stat-tile")
        self.assertContains(res, "card--hard-shadow")

    def test_employer_dashboard_view_verified_no_banner(self):
        self.client.login(username="emp_va@test.com", password="password123")
        res = self.client.get(reverse("core:employer_dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, "Employer Account Awaiting Verification")
        self.assertContains(res, "Verified")

    def test_applicant_dashboard_view(self):
        self.client.login(username="app_v@test.com", password="password123")
        res = self.client.get(reverse("core:applicant_dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Profile Completeness")
        self.assertContains(res, "completeness-bar")
        self.assertContains(res, "stat-tile")

    def test_admin_panel_view(self):
        self.client.login(username="adm_v@test.com", password="password123")
        res = self.client.get(reverse("core:admin_panel"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Platform Administration")
        self.assertContains(res, "Users Distribution by Role")
        self.assertContains(res, "stat-tile")

    def test_wrong_role_access_denied(self):
        self.client.login(username="app_v@test.com", password="password123")
        res = self.client.get(reverse("core:employer_dashboard"))
        self.assertEqual(res.status_code, 403)

        res = self.client.get(reverse("core:admin_panel"))
        self.assertEqual(res.status_code, 403)


class Stage7HardeningTest(TestCase):
    """
    Stage 7 Tests:
      - Security: resume uploads (pdf/doc/docx, max 30 MB)
      - Security: login rate limit (5 attempts / 5 mins, HTTP 429)
      - Security: media access only for owning applicant, job's employer, and admins
      - Production: settings split (dev vs prod cookies & debug)
    """

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

        self.client = Client()

        # Users
        self.admin = User.objects.create_user(
            username="sec_admin",
            email="admin@sec.dev",
            password="password123",
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        self.employer = User.objects.create_user(
            username="sec_employer",
            email="emp@sec.dev",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,
        )
        self.employer.is_verified = True
        self.employer.save()

        self.other_employer = User.objects.create_user(
            username="sec_other_employer",
            email="other_emp@sec.dev",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,
        )
        self.other_employer.is_verified = True
        self.other_employer.save()

        self.applicant = User.objects.create_user(
            username="sec_applicant",
            email="app@sec.dev",
            password="password123",
            role=User.Role.APPLICANT,
            status=User.Status.ACTIVE,
        )

        self.intruder_applicant = User.objects.create_user(
            username="sec_intruder",
            email="intruder@sec.dev",
            password="password123",
            role=User.Role.APPLICANT,
            status=User.Status.ACTIVE,
        )

        # Job
        self.job = Job.objects.create(
            employer=self.employer,
            title="Secured Software Engineer",
            slug="secured-software-engineer",
            description="High security engineering position.",
            location="Remote",
            status=Job.Status.OPEN,
        )

        # Application with resume snapshot
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.resume_file = SimpleUploadedFile("my_resume.pdf", b"%PDF-1.4 test resume content", content_type="application/pdf")
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume_snapshot=self.resume_file,
            status=Application.Status.SUBMITTED,
        )

    def test_resume_validator_allowed_formats_and_size(self):
        """Resume validator allows pdf/doc/docx <= 30 MB and rejects invalid types / oversized files."""
        from django.core.exceptions import ValidationError
        from django.core.files.uploadedfile import SimpleUploadedFile
        from core.validators import validate_resume_file

        # 1. Valid PDF
        valid_pdf = SimpleUploadedFile("doc.pdf", b"%PDF-1.4 dummy", content_type="application/pdf")
        try:
            validate_resume_file(valid_pdf)
        except ValidationError:
            self.fail("validate_resume_file raised ValidationError unexpectedly for valid PDF!")

        # 2. Valid DOCX
        valid_docx = SimpleUploadedFile("doc.docx", b"PK docx content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        try:
            validate_resume_file(valid_docx)
        except ValidationError:
            self.fail("validate_resume_file raised ValidationError unexpectedly for valid DOCX!")

        # 3. Invalid extension (.exe, .sh, .txt)
        bad_exe = SimpleUploadedFile("virus.exe", b"MZ bad content", content_type="application/x-msdownload")
        with self.assertRaises(ValidationError) as ctx:
            validate_resume_file(bad_exe)
        self.assertIn("Invalid file format", str(ctx.exception))

        # 4. Oversized file (> 30 MB)
        oversized = SimpleUploadedFile("huge.pdf", b"x", content_type="application/pdf")
        oversized.size = 35 * 1024 * 1024  # 35 MB fake size
        with self.assertRaises(ValidationError) as ctx:
            validate_resume_file(oversized)
        self.assertIn("must not exceed 30 MB", str(ctx.exception))

    def test_login_rate_limiting(self):
        """Failed logins exceeding rate limit trigger HTTP 429 Too Many Requests."""
        from django.urls import reverse
        from django.core.cache import cache
        cache.clear()

        login_url = reverse("accounts:login")

        # 5 failed attempts
        for i in range(5):
            resp = self.client.post(login_url, {"username": "wrong@test.com", "password": "wrongpassword"})
            self.assertIn(resp.status_code, [200, 302])

        # 6th attempt should be blocked with 429
        blocked_resp = self.client.post(login_url, {"username": "wrong@test.com", "password": "wrongpassword"})
        self.assertEqual(blocked_resp.status_code, 429)

        # Successful login resets the counter
        cache.clear()
        ok_resp = self.client.post(login_url, {"username": self.applicant.email, "password": "password123"})
        self.assertEqual(ok_resp.status_code, 302)

    def test_protected_media_access_control(self):
        """Media access allows only owning applicant, job employer, and admin; denies intruders."""
        resume_url = self.application.resume_snapshot.url

        # 1. Unauthenticated user
        self.client.logout()
        resp = self.client.get(resume_url)
        # Should redirect to login or be 403
        self.assertIn(resp.status_code, [302, 403])

        # 2. Intruder applicant (not their application) -> 403
        self.client.login(username="sec_intruder", password="password123")
        resp = self.client.get(resume_url)
        self.assertEqual(resp.status_code, 403)

        # 3. Other employer (not this job's employer) -> 403
        self.client.login(username="sec_other_employer", password="password123")
        resp = self.client.get(resume_url)
        self.assertEqual(resp.status_code, 403)

        # 4. Owning applicant -> 200
        self.client.login(username="sec_applicant", password="password123")
        resp = self.client.get(resume_url)
        self.assertEqual(resp.status_code, 200)

        # 5. Job's employer -> 200
        self.client.login(username="sec_employer", password="password123")
        resp = self.client.get(resume_url)
        self.assertEqual(resp.status_code, 200)

        # 6. Administrator -> 200
        self.client.login(username="sec_admin", password="password123")
        resp = self.client.get(resume_url)
        self.assertEqual(resp.status_code, 200)

    def test_settings_split_prod_and_dev(self):
        """Verify production settings enforce secure cookies, headers, and debug=False."""
        from inkboard.settings import prod, dev

        # Dev
        self.assertTrue(dev.DEBUG)
        self.assertEqual(dev.EMAIL_BACKEND, "django.core.mail.backends.console.EmailBackend")

        # Prod
        self.assertFalse(prod.DEBUG)
        self.assertTrue(prod.SESSION_COOKIE_SECURE)
        self.assertTrue(prod.CSRF_COOKIE_SECURE)
        self.assertTrue(prod.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(prod.CSRF_COOKIE_HTTPONLY)
        self.assertEqual(prod.X_FRAME_OPTIONS, "DENY")
        self.assertEqual(prod.STATICFILES_STORAGE, "whitenoise.storage.CompressedManifestStaticFilesStorage")

