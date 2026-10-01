"""
applications/tests.py — Model tests for Application, Interview, Offer.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError

from jobs.models import Category, Job
from applications.models import Application, Interview, Offer

User = get_user_model()


class ApplicationModelTest(TestCase):

    def setUp(self):
        self.employer = User.objects.create_user(
            username="emp_app",
            password="x",
            role=User.Role.EMPLOYER,
            first_name="Helen",
            last_name="Troy",
        )
        self.applicant = User.objects.create_user(
            username="app_app",
            password="x",
            role=User.Role.APPLICANT,
            first_name="Achilles",
            last_name="Pelides",
        )
        self.job = Job.objects.create(
            employer=self.employer,
            title="Python Developer",
            slug="python-dev-testco",
            description="Write great Python.",
            status=Job.Status.OPEN,
            location="Athens, GR",
        )
        self.application = Application.objects.create(
            applicant=self.applicant,
            job=self.job,
            cover_letter="I am the best candidate.",
            status=Application.Status.SUBMITTED,
        )

    def test_str(self):
        s = str(self.application)
        self.assertIn("Achilles Pelides", s)
        self.assertIn("Python Developer", s)
        self.assertIn("submitted", s)

    def test_status_choices(self):
        statuses = [s.value for s in Application.Status]
        for s in ["submitted", "under_review", "shortlisted", "hired", "rejected", "withdrawn"]:
            self.assertIn(s, statuses)

    def test_unique_constraint_applicant_job(self):
        """An applicant cannot apply to the same job twice."""
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                applicant=self.applicant,
                job=self.job,
                status=Application.Status.SUBMITTED,
            )

    def test_meta_ordering(self):
        """Applications ordered by -applied_at."""
        applicant2 = User.objects.create_user(
            username="app_app2", password="x", role=User.Role.APPLICANT
        )
        app2 = Application.objects.create(
            applicant=applicant2,
            job=self.job,
            status=Application.Status.SUBMITTED,
        )
        apps = list(Application.objects.all())
        self.assertEqual(apps[0], app2)  # newest first

    def test_default_status_is_submitted(self):
        applicant3 = User.objects.create_user(
            username="app_app3", password="x", role=User.Role.APPLICANT
        )
        job2 = Job.objects.create(
            employer=self.employer,
            title="Another Job",
            slug="another-job-test",
            description="x",
            location="Remote",
        )
        app = Application.objects.create(applicant=applicant3, job=job2)
        self.assertEqual(app.status, Application.Status.SUBMITTED)


class InterviewModelTest(TestCase):

    def setUp(self):
        employer = User.objects.create_user(username="emp_int", password="x", role=User.Role.EMPLOYER)
        applicant = User.objects.create_user(username="app_int", password="x", role=User.Role.APPLICANT)
        job = Job.objects.create(
            employer=employer,
            title="Int Job",
            slug="int-job",
            description="x",
            location="Remote",
        )
        self.application = Application.objects.create(applicant=applicant, job=job)
        self.interview = Interview.objects.create(
            application=self.application,
            scheduled_at=timezone.now() + timezone.timedelta(days=7),
            duration_minutes=60,
            format=Interview.Format.VIDEO,
            outcome=Interview.Outcome.PENDING,
        )

    def test_str_contains_format(self):
        self.assertIn("video", str(self.interview))

    def test_format_choices(self):
        formats = [f.value for f in Interview.Format]
        for f in ["phone", "video", "onsite", "technical", "panel"]:
            self.assertIn(f, formats)

    def test_outcome_choices(self):
        outcomes = [o.value for o in Interview.Outcome]
        for o in ["pending", "passed", "failed", "no_show", "rescheduled"]:
            self.assertIn(o, outcomes)

    def test_default_outcome_pending(self):
        self.assertEqual(self.interview.outcome, Interview.Outcome.PENDING)


class OfferModelTest(TestCase):

    def setUp(self):
        employer = User.objects.create_user(username="emp_off", password="x", role=User.Role.EMPLOYER)
        applicant = User.objects.create_user(username="app_off", password="x", role=User.Role.APPLICANT)
        job = Job.objects.create(
            employer=employer,
            title="Offer Job",
            slug="offer-job",
            description="x",
            location="Remote",
        )
        self.application = Application.objects.create(applicant=applicant, job=job)
        self.offer = Offer.objects.create(
            application=self.application,
            salary_offered=120_000,
            currency="USD",
            status=Offer.OfferStatus.PENDING,
        )

    def test_str(self):
        self.assertIn("Offer for", str(self.offer))
        self.assertIn("pending", str(self.offer))

    def test_offer_status_choices(self):
        statuses = [s.value for s in Offer.OfferStatus]
        for s in ["pending", "accepted", "declined", "expired", "negotiating"]:
            self.assertIn(s, statuses)

    def test_one_to_one_with_application(self):
        self.assertEqual(self.application.offer.salary_offered, 120_000)


class ApplicantJobBoardAndApplyTest(TestCase):
    """
    Comprehensive tests for Stage 4:
    1. Filter & search on job list (deadline not passed, status=open).
    2. Apply to open job (form submission with resume snapshot).
    3. No double apply (friendly already applied state from unique constraint).
    4. No applying to closed/removed/expired jobs.
    5. My applications page with stamp status and timeline.
    6. Applicant profile editing (full_name, phone, location, resume).
    """

    def setUp(self):
        import datetime
        self.client = Client()

        self.employer = User.objects.create_user(
            username="emp_board",
            email="emp_board@test.com",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,
        )
        self.applicant = User.objects.create_user(
            username="app_board",
            email="app_board@test.com",
            password="password123",
            role=User.Role.APPLICANT,
            first_name="Jane",
            last_name="Doe",
        )
        self.cat_design = Category.objects.create(name="Design", slug="design", icon="🎨")
        self.cat_dev = Category.objects.create(name="Development", slug="dev", icon="💻")

        today = timezone.now().date()
        future_date = today + datetime.timedelta(days=14)
        past_date = today - datetime.timedelta(days=2)

        # 1. Open active design job in San Francisco
        self.job_design = Job.objects.create(
            employer=self.employer,
            category=self.cat_design,
            title="Lead UX Designer",
            slug="lead-ux-designer",
            description="Design next-gen interfaces with Figma and user research.",
            location="San Francisco, CA",
            salary_min=100000,
            salary_max=140000,
            status=Job.Status.OPEN,
            deadline=future_date,
        )

        # 2. Open active remote dev job
        self.job_dev = Job.objects.create(
            employer=self.employer,
            category=self.cat_dev,
            title="Senior Backend Engineer",
            slug="senior-backend-engineer",
            description="Build scalable distributed APIs in Python and PostgreSQL.",
            location="Remote",
            is_remote=True,
            salary_min=150000,
            salary_max=190000,
            status=Job.Status.OPEN,
            deadline=future_date,
        )

        # 3. Expired job (deadline in past)
        self.job_expired = Job(
            employer=self.employer,
            category=self.cat_dev,
            title="Expired Python Role",
            slug="expired-python-role",
            description="Past deadline role.",
            location="Remote",
            status=Job.Status.OPEN,
            deadline=past_date,
        )
        self.job_expired.save()

        # 4. Closed job
        self.job_closed = Job.objects.create(
            employer=self.employer,
            category=self.cat_dev,
            title="Closed Systems Architect",
            slug="closed-systems-architect",
            description="This job has been closed.",
            location="Remote",
            status=Job.Status.CLOSED,
            deadline=future_date,
        )

        # 5. Removed (soft-deleted) job
        self.job_removed = Job.objects.create(
            employer=self.employer,
            category=self.cat_dev,
            title="Removed Data Engineer",
            slug="removed-data-engineer",
            description="This job was soft deleted.",
            location="Remote",
            status=Job.Status.REMOVED,
            deadline=future_date,
        )

    def test_job_list_filters_and_exclusions(self):
        """Job list only shows status=open with non-passed deadline, and respects filters."""
        res = self.client.get(reverse("jobs:list"))
        self.assertEqual(res.status_code, 200)

        # Visible active jobs
        jobs_in_context = list(res.context["jobs"])
        self.assertIn(self.job_design, jobs_in_context)
        self.assertIn(self.job_dev, jobs_in_context)

        # Inactive/expired jobs are excluded
        self.assertNotIn(self.job_expired, jobs_in_context)
        self.assertNotIn(self.job_closed, jobs_in_context)
        self.assertNotIn(self.job_removed, jobs_in_context)

        # Search query filter (matches title/skills)
        res_search = self.client.get(reverse("jobs:list"), {"q": "UX"})
        self.assertIn(self.job_design, list(res_search.context["jobs"]))
        self.assertNotIn(self.job_dev, list(res_search.context["jobs"]))

        # Category filter
        res_cat = self.client.get(reverse("jobs:list"), {"category": "dev"})
        self.assertIn(self.job_dev, list(res_cat.context["jobs"]))
        self.assertNotIn(self.job_design, list(res_cat.context["jobs"]))

        # Location filter
        res_loc = self.client.get(reverse("jobs:list"), {"location": "San Francisco"})
        self.assertIn(self.job_design, list(res_loc.context["jobs"]))
        self.assertNotIn(self.job_dev, list(res_loc.context["jobs"]))

        # Remote toggle filter
        res_remote = self.client.get(reverse("jobs:list"), {"is_remote": "1"})
        self.assertIn(self.job_dev, list(res_remote.context["jobs"]))
        self.assertNotIn(self.job_design, list(res_remote.context["jobs"]))

        # Salary filter
        res_salary = self.client.get(reverse("jobs:list"), {"min_salary": "150000"})
        self.assertIn(self.job_dev, list(res_salary.context["jobs"]))
        self.assertNotIn(self.job_design, list(res_salary.context["jobs"]))

        # HTMX partial check
        res_htmx = self.client.get(reverse("jobs:list"), HTTP_HX_REQUEST="true")
        self.assertEqual(res_htmx.status_code, 200)
        self.assertTemplateUsed(res_htmx, "jobs/partials/job_list_results.html")

    def test_apply_to_open_job_successfully(self):
        """Applicant can submit application with cover letter and resume."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username="app_board", password="password123")

        # GET apply form
        res_get = self.client.get(reverse("applications:apply", kwargs={"job_id": self.job_dev.pk}))
        self.assertEqual(res_get.status_code, 200)
        self.assertTemplateUsed(res_get, "applications/apply.html")

        # POST submission
        test_file = SimpleUploadedFile("resume.pdf", b"Dummy resume content", content_type="application/pdf")
        post_data = {
            "cover_letter": "I have 8 years of Python experience and would love to join.",
            "resume": test_file,
            "portfolio_url": "https://janedoe.dev",
        }
        res_post = self.client.post(
            reverse("applications:apply", kwargs={"job_id": self.job_dev.pk}),
            data=post_data,
        )
        self.assertEqual(res_post.status_code, 302)

        app = Application.objects.get(applicant=self.applicant, job=self.job_dev)
        self.assertEqual(app.status, Application.Status.SUBMITTED)
        self.assertIn("8 years of Python", app.cover_letter)
        self.assertTrue(bool(app.resume_snapshot))

    def test_no_double_apply(self):
        """Attempting to apply twice triggers the friendly already-applied state."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username="app_board", password="password123")

        # First application
        test_file = SimpleUploadedFile("resume.pdf", b"Resume content", content_type="application/pdf")
        self.client.post(
            reverse("applications:apply", kwargs={"job_id": self.job_design.pk}),
            data={"cover_letter": "First apply", "resume": test_file},
        )
        self.assertEqual(Application.objects.filter(applicant=self.applicant, job=self.job_design).count(), 1)

        # Second application attempt via GET: renders friendly already-applied template
        res_get_again = self.client.get(reverse("applications:apply", kwargs={"job_id": self.job_design.pk}))
        self.assertEqual(res_get_again.status_code, 200)
        self.assertTemplateUsed(res_get_again, "applications/already_applied.html")
        self.assertContains(res_get_again, "You Have Already Applied")

        # Second application attempt via POST: does not create duplicate row and shows already-applied
        test_file2 = SimpleUploadedFile("resume2.pdf", b"Resume content 2", content_type="application/pdf")
        res_post_again = self.client.post(
            reverse("applications:apply", kwargs={"job_id": self.job_design.pk}),
            data={"cover_letter": "Duplicate attempt", "resume": test_file2},
        )
        self.assertEqual(res_post_again.status_code, 200)
        self.assertTemplateUsed(res_post_again, "applications/already_applied.html")
        # Ensure count is still exactly 1
        self.assertEqual(Application.objects.filter(applicant=self.applicant, job=self.job_design).count(), 1)

    def test_no_applying_to_closed_or_removed_or_expired_jobs(self):
        """Cannot apply to closed, removed, or expired jobs."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username="app_board", password="password123")
        test_file = SimpleUploadedFile("r.pdf", b"pdf", content_type="application/pdf")

        # 1. Closed job
        res_closed = self.client.post(
            reverse("applications:apply", kwargs={"job_id": self.job_closed.pk}),
            data={"cover_letter": "Closed job attempt", "resume": test_file},
        )
        self.assertEqual(res_closed.status_code, 400)
        self.assertTemplateUsed(res_closed, "applications/job_closed.html")

        # 2. Removed job
        res_removed = self.client.post(
            reverse("applications:apply", kwargs={"job_id": self.job_removed.pk}),
            data={"cover_letter": "Removed job attempt", "resume": test_file},
        )
        self.assertEqual(res_removed.status_code, 400)
        self.assertTemplateUsed(res_removed, "applications/job_closed.html")

        # 3. Expired deadline job
        res_expired = self.client.post(
            reverse("applications:apply", kwargs={"job_id": self.job_expired.pk}),
            data={"cover_letter": "Expired job attempt", "resume": test_file},
        )
        self.assertEqual(res_expired.status_code, 400)
        self.assertTemplateUsed(res_expired, "applications/job_closed.html")

    def test_my_applications_page_and_timeline_view(self):
        """Applicant can view their application list, stamp chip, and progression timeline."""
        self.client.login(username="app_board", password="password123")

        app = Application.objects.create(
            applicant=self.applicant,
            job=self.job_design,
            cover_letter="Cover letter text",
            status=Application.Status.SUBMITTED,
        )

        # My applications list
        res_list = self.client.get(reverse("applications:list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertTemplateUsed(res_list, "applications/list.html")
        self.assertContains(res_list, "Lead UX Designer")
        self.assertContains(res_list, "stamp-chip--submitted")

        # Application detail with timeline
        res_detail = self.client.get(reverse("applications:detail", kwargs={"pk": app.pk}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertTemplateUsed(res_detail, "applications/detail.html")
        self.assertIn("timeline", res_detail.context)
        timeline_keys = [step["key"] for step in res_detail.context["timeline"]]
        self.assertIn("submitted", timeline_keys)
        self.assertIn("under_review", timeline_keys)

        # Applicant withdraws application
        res_withdraw = self.client.post(reverse("applications:withdraw", kwargs={"pk": app.pk}))
        self.assertEqual(res_withdraw.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.WITHDRAWN)
        self.assertIsNotNone(app.withdrawn_at)

    def test_applicant_profile_edit_and_default_resume(self):
        """Applicant can edit name, phone, location, and upload resume which defaults for applications."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username="app_board", password="password123")

        # GET profile page
        res_get = self.client.get(reverse("accounts:profile"))
        self.assertEqual(res_get.status_code, 200)
        self.assertTemplateUsed(res_get, "accounts/profile.html")

        # POST profile update
        profile_resume = SimpleUploadedFile("master_resume.pdf", b"Master CV", content_type="application/pdf")
        post_data = {
            "full_name": "Ada Lovelace",
            "phone": "+1 (555) 987-6543",
            "location": "London, UK",
            "resume": profile_resume,
        }
        res_post = self.client.post(reverse("accounts:profile"), data=post_data)
        self.assertEqual(res_post.status_code, 302)

        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.first_name, "Ada")
        self.assertEqual(self.applicant.last_name, "Lovelace")
        self.assertEqual(self.applicant.phone, "+1 (555) 987-6543")
        self.assertEqual(self.applicant.location, "London, UK")
        self.assertTrue(bool(self.applicant.applicant_profile.resume))

        # Now apply for a job without providing a new resume file
        # The form should allow it because profile resume is on file, and snapshot it!
        res_apply = self.client.post(
            reverse("applications:apply", kwargs={"job_id": self.job_dev.pk}),
            data={"cover_letter": "Using my profile resume!"},
        )
        self.assertEqual(res_apply.status_code, 302)
        app = Application.objects.get(applicant=self.applicant, job=self.job_dev)
        self.assertTrue(bool(app.resume_snapshot))
        self.assertEqual(app.status, Application.Status.SUBMITTED)


class JobPipelineAndReviewTest(TestCase):
    """
    Tests for Stage 5:
    1. Per-job board with columns and allowed status transitions enforced in single service function.
    2. Invalid transitions rejected.
    3. Only the job's employer can move cards (PermissionDenied for others).
    4. Application drawer with candidate info, resume, cover letter.
    5. Schedule interview moves application to 'interview' (interview_scheduled).
    6. Employer records interview result (outcome and notes).
    7. Applicant sees interviews on dashboard; console email sent on status change and interview schedule.
    """

    def setUp(self):
        import datetime
        from django.core import mail
        mail.outbox.clear()

        self.client = Client()

        # Job Owner Employer
        self.employer = User.objects.create_user(
            username="owner_emp",
            email="owner@testco.com",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,
        )

        # Another Employer (Intruder)
        self.intruder_employer = User.objects.create_user(
            username="other_emp",
            email="other@testco.com",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,
        )

        # Applicant
        self.applicant = User.objects.create_user(
            username="candidate_dan",
            email="dan@candidate.com",
            password="password123",
            role=User.Role.APPLICANT,
            first_name="Dan",
            last_name="Craftsman",
        )

        self.category = Category.objects.create(name="Tech", slug="tech")

        self.job = Job.objects.create(
            employer=self.employer,
            category=self.category,
            title="Senior Python Architect",
            slug="senior-python-architect",
            description="Leading system architecture.",
            location="Remote",
            status=Job.Status.OPEN,
        )

        self.application = Application.objects.create(
            applicant=self.applicant,
            job=self.job,
            cover_letter="Passionate about architecture.",
            status=Application.Status.SUBMITTED,
        )

    def test_valid_transitions_via_service_and_email(self):
        """Employer transitions application through allowed stages, sending emails."""
        from django.core import mail
        from applications.services import transition_application_status

        mail.outbox.clear()

        # 1. Move SUBMITTED -> UNDER_REVIEW
        app = transition_application_status(
            self.application,
            Application.Status.UNDER_REVIEW,
            self.employer,
        )
        self.assertEqual(app.status, Application.Status.UNDER_REVIEW)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Application Status Update", mail.outbox[0].subject)
        self.assertIn(self.applicant.email, mail.outbox[0].to)

        # 2. Move UNDER_REVIEW -> SHORTLISTED
        app = transition_application_status(
            app,
            Application.Status.SHORTLISTED,
            self.employer,
        )
        self.assertEqual(app.status, Application.Status.SHORTLISTED)
        self.assertEqual(len(mail.outbox), 2)

    def test_invalid_transitions_rejected(self):
        """Disallowed transitions raise ValidationError and return HTTP 400."""
        from django.core.exceptions import ValidationError
        from applications.services import transition_application_status

        # SUBMITTED cannot transition directly to HIRED
        with self.assertRaises(ValidationError):
            transition_application_status(
                self.application,
                Application.Status.HIRED,
                self.employer,
            )

        # SUBMITTED cannot transition directly to OFFER_EXTENDED
        with self.assertRaises(ValidationError):
            transition_application_status(
                self.application,
                Application.Status.OFFER_EXTENDED,
                self.employer,
            )

        # HTTP Endpoint check: POST invalid transition returns 400
        self.client.login(username="owner_emp", password="password123")
        res = self.client.post(
            reverse("applications:transition", kwargs={"pk": self.application.pk}),
            data={"new_status": Application.Status.HIRED},
        )
        self.assertEqual(res.status_code, 400)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.SUBMITTED)

        # Withdrawn applications cannot be moved (terminal)
        self.application.status = Application.Status.WITHDRAWN
        self.application.save()
        with self.assertRaises(ValidationError):
            transition_application_status(
                self.application,
                Application.Status.UNDER_REVIEW,
                self.employer,
            )

    def test_only_job_employer_can_move_cards(self):
        """Only the job's owning employer can move cards; others get PermissionDenied (403)."""
        from django.core.exceptions import PermissionDenied
        from applications.services import transition_application_status

        # 1. Other employer via service function
        with self.assertRaises(PermissionDenied):
            transition_application_status(
                self.application,
                Application.Status.UNDER_REVIEW,
                self.intruder_employer,
            )

        # 2. Applicant user via service function
        with self.assertRaises(PermissionDenied):
            transition_application_status(
                self.application,
                Application.Status.UNDER_REVIEW,
                self.applicant,
            )

        # 3. HTTP endpoint check with intruder login: returns 403
        self.client.login(username="other_emp", password="password123")
        res = self.client.post(
            reverse("applications:transition", kwargs={"pk": self.application.pk}),
            data={"new_status": Application.Status.UNDER_REVIEW},
        )
        self.assertEqual(res.status_code, 403)

        # Ensure database remained untouched
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.SUBMITTED)

        # 4. Legitimate owner moves card via HTTP endpoint: succeeds
        self.client.login(username="owner_emp", password="password123")
        res_owner = self.client.post(
            reverse("applications:transition", kwargs={"pk": self.application.pk}),
            data={"new_status": Application.Status.UNDER_REVIEW},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(res_owner.status_code, 200)
        self.assertTemplateUsed(res_owner, "jobs/partials/pipeline_board.html")
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.UNDER_REVIEW)

    def test_application_drawer_endpoint(self):
        """Employer can open the candidate review drawer; strangers get 403."""
        # Intruder gets 403
        self.client.login(username="other_emp", password="password123")
        res_intruder = self.client.get(
            reverse("applications:drawer", kwargs={"pk": self.application.pk})
        )
        self.assertEqual(res_intruder.status_code, 403)

        # Owner gets 200 with drawer partial
        self.client.login(username="owner_emp", password="password123")
        res_owner = self.client.get(
            reverse("applications:drawer", kwargs={"pk": self.application.pk})
        )
        self.assertEqual(res_owner.status_code, 200)
        self.assertTemplateUsed(res_owner, "applications/partials/drawer.html")
        self.assertContains(res_owner, "Dan Craftsman")
        self.assertContains(res_owner, "Passionate about architecture.")

    def test_schedule_interview_moves_to_interview_and_applicant_dashboard_reflects(self):
        """Scheduling an interview moves application to 'interview_scheduled' and shows on dashboard."""
        import datetime
        from django.core import mail
        from applications.services import schedule_interview
        from core.services import get_applicant_dashboard_data

        mail.outbox.clear()
        future_time = timezone.now() + datetime.timedelta(days=3, hours=2)

        # Schedule interview
        interview = schedule_interview(
            application=self.application,
            scheduled_at=future_time,
            mode=Interview.Format.VIDEO,
            user=self.employer,
            duration_minutes=45,
            meeting_link="https://meet.google.com/abc-xyz",
            notes="Technical system design discussion",
        )

        self.assertEqual(interview.format, Interview.Format.VIDEO)
        self.assertEqual(interview.outcome, Interview.Outcome.PENDING)

        # Check application status auto-moved to interview_scheduled
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.INTERVIEW_SCHEDULED)

        # Check notification email sent to applicant
        self.assertTrue(len(mail.outbox) >= 1)
        self.assertIn("Interview Scheduled", mail.outbox[-1].subject)
        self.assertIn("https://meet.google.com/abc-xyz", mail.outbox[-1].body)

        # Verify applicant sees it on their dashboard
        dashboard_data = get_applicant_dashboard_data(self.applicant)
        upcoming = list(dashboard_data["upcoming_interviews"])
        self.assertIn(interview, upcoming)

        # Verify through HTTP endpoint as well
        self.client.login(username="owner_emp", password="password123")
        future_str = (timezone.now() + datetime.timedelta(days=4)).strftime("%Y-%m-%dT%H:%M")
        res_post = self.client.post(
            reverse("applications:schedule_interview", kwargs={"pk": self.application.pk}),
            data={
                "scheduled_at": future_str,
                "mode": Interview.Format.TECHNICAL,
                "duration_minutes": "60",
                "notes": "Coding challenge session",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(res_post.status_code, 200)

    def test_employer_records_interview_result(self):
        """Employer records outcome (e.g. passed) and evaluation notes for an interview."""
        import datetime
        from applications.services import schedule_interview, record_interview_result

        future_time = timezone.now() + datetime.timedelta(days=1)
        interview = schedule_interview(
            application=self.application,
            scheduled_at=future_time,
            mode=Interview.Format.PHONE,
            user=self.employer,
        )

        # Record result
        updated = record_interview_result(
            interview=interview,
            outcome=Interview.Outcome.PASSED,
            notes="Candidate demonstrated deep Django ORM and architecture skills.",
            user=self.employer,
        )
        self.assertEqual(updated.outcome, Interview.Outcome.PASSED)
        self.assertIn("deep Django ORM", updated.notes)

        # Intruder cannot record result
        from django.core.exceptions import PermissionDenied
        with self.assertRaises(PermissionDenied):
            record_interview_result(
                interview=interview,
                outcome=Interview.Outcome.FAILED,
                notes="Intruder note",
                user=self.intruder_employer,
            )


