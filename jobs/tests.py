"""
jobs/tests.py — Model tests for Category, Job, and JobTag.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobs.models import Category, Job, JobTag

User = get_user_model()


class CategoryModelTest(TestCase):

    def setUp(self):
        self.cat = Category.objects.create(
            name="Engineering",
            slug="engineering",
            icon="💻",
            color="#6C63FF",
        )

    def test_str(self):
        self.assertEqual(str(self.cat), "Engineering")

    def test_unique_name(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Engineering", slug="engineering-2")

    def test_unique_slug(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Engineering 2", slug="engineering")

    def test_meta_ordering(self):
        Category.objects.create(name="Aardvark", slug="aardvark")
        cats = list(Category.objects.values_list("name", flat=True))
        self.assertEqual(cats, sorted(cats))


class JobModelTest(TestCase):

    def setUp(self):
        self.employer = User.objects.create_user(
            username="emp_job",
            password="x",
            role=User.Role.EMPLOYER,
            first_name="Eve",
            last_name="Turner",
        )
        self.cat = Category.objects.create(name="Data", slug="data")
        self.job = Job.objects.create(
            employer=self.employer,
            category=self.cat,
            title="Data Engineer",
            slug="data-engineer-testco",
            description="Build robust data pipelines.",
            status=Job.Status.OPEN,
            job_type=Job.JobType.FULL_TIME,
            experience_level=Job.ExperienceLevel.MID,
            location="Berlin, DE",
            is_remote=True,
            salary_min=80_000,
            salary_max=120_000,
            salary_period=Job.SalaryPeriod.YEARLY,
            salary_currency="EUR",
        )

    def test_str(self):
        self.assertEqual(str(self.job), "Data Engineer @ Eve Turner (employer)")

    def test_is_open_true(self):
        self.assertTrue(self.job.is_open())

    def test_is_open_false(self):
        self.job.status = Job.Status.CLOSED
        self.assertFalse(self.job.is_open())

    def test_salary_display(self):
        display = self.job.salary_display()
        self.assertIn("EUR", display)
        self.assertIn("80,000", display)
        self.assertIn("120,000", display)

    def test_salary_display_not_specified(self):
        self.job.salary_min = None
        self.job.salary_max = None
        self.assertEqual(self.job.salary_display(), "Salary not specified")

    def test_status_choices(self):
        statuses = [s.value for s in Job.Status]
        for s in ["draft", "open", "paused", "closed", "filled"]:
            self.assertIn(s, statuses)

    def test_job_type_choices(self):
        types = [t.value for t in Job.JobType]
        for t in ["full_time", "part_time", "contract", "freelance", "internship"]:
            self.assertIn(t, types)

    def test_meta_ordering(self):
        """Jobs should be ordered by -created_at (newest first)."""
        job2 = Job.objects.create(
            employer=self.employer,
            title="Job 2",
            slug="job-2-test",
            description="x",
            status=Job.Status.OPEN,
            location="NYC",
        )
        jobs = list(Job.objects.all())
        self.assertEqual(jobs[0], job2)  # newest first

    def test_unique_slug(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Job.objects.create(
                employer=self.employer,
                title="Duplicate",
                slug="data-engineer-testco",
                description="x",
                location="x",
            )


class JobTagModelTest(TestCase):

    def setUp(self):
        self.employer = User.objects.create_user(
            username="emp_tag",
            password="x",
            role=User.Role.EMPLOYER,
        )
        self.job = Job.objects.create(
            employer=self.employer,
            title="Tagged Job",
            slug="tagged-job",
            description="x",
            location="Remote",
        )

    def test_str(self):
        tag = JobTag.objects.create(job=self.job, name="Python")
        self.assertEqual(str(tag), "Python")

    def test_unique_together(self):
        from django.db import IntegrityError
        JobTag.objects.create(job=self.job, name="React")
        with self.assertRaises(IntegrityError):
            JobTag.objects.create(job=self.job, name="React")


class JobValidationTest(TestCase):
    """Test validations for salary range and deadline."""

    def setUp(self):
        self.employer = User.objects.create_user(
            username="val_emp", password="x", role=User.Role.EMPLOYER, status=User.Status.ACTIVE
        )
        self.category = Category.objects.create(name="Design", slug="design")

    def test_salary_min_greater_than_max_fails_model_clean(self):
        job = Job(
            employer=self.employer,
            category=self.category,
            title="Designer",
            location="Remote",
            salary_min=120000,
            salary_max=80000,
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError) as ctx:
            job.clean()
        self.assertIn("salary_min", ctx.exception.message_dict)

    def test_salary_min_greater_than_max_fails_form(self):
        from jobs.forms import JobForm
        data = {
            "title": "Designer",
            "category": self.category.pk,
            "job_type": Job.JobType.FULL_TIME,
            "experience_level": Job.ExperienceLevel.MID,
            "location": "Remote",
            "salary_min": 120000,
            "salary_max": 80000,
            "salary_period": Job.SalaryPeriod.YEARLY,
            "salary_currency": "USD",
            "description": "Valid description text.",
            "status": Job.Status.OPEN,
        }
        form = JobForm(data=data, employer=self.employer)
        self.assertFalse(form.is_valid())
        self.assertIn("salary_min", form.errors)

    def test_salary_min_less_or_equal_max_passes(self):
        from jobs.forms import JobForm
        data = {
            "title": "Designer",
            "category": self.category.pk,
            "job_type": Job.JobType.FULL_TIME,
            "experience_level": Job.ExperienceLevel.MID,
            "location": "Remote",
            "salary_min": 80000,
            "salary_max": 120000,
            "salary_period": Job.SalaryPeriod.YEARLY,
            "salary_currency": "USD",
            "description": "Valid description text.",
            "status": Job.Status.OPEN,
        }
        form = JobForm(data=data, employer=self.employer)
        self.assertTrue(form.is_valid(), form.errors)

    def test_deadline_in_past_fails_validation(self):
        import datetime
        from django.utils import timezone
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        job = Job(
            employer=self.employer,
            category=self.category,
            title="Designer",
            location="Remote",
            deadline=yesterday,
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError) as ctx:
            job.clean()
        self.assertIn("deadline", ctx.exception.message_dict)

    def test_deadline_today_or_future_passes(self):
        import datetime
        from django.utils import timezone
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        job = Job(
            employer=self.employer,
            category=self.category,
            title="Designer",
            location="Remote",
            deadline=tomorrow,
        )
        job.clean()  # should not raise


class JobVerificationRuleTest(TestCase):
    """Test verification rules: unverified employers can save drafts but not publish."""

    def setUp(self):
        self.unverified_employer = User.objects.create_user(
            username="unverified_emp",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.PENDING,  # is_verified is False
        )
        self.verified_employer = User.objects.create_user(
            username="verified_emp",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,  # is_verified is True
        )
        self.category = Category.objects.create(name="AI", slug="ai")
        self.client = Client()

    def test_unverified_employer_can_save_draft(self):
        from jobs.forms import JobForm
        data = {
            "title": "Draft ML Engineer",
            "category": self.category.pk,
            "job_type": Job.JobType.FULL_TIME,
            "experience_level": Job.ExperienceLevel.SENIOR,
            "location": "San Francisco, CA",
            "description": "Machine learning engineering role.",
            "status": Job.Status.DRAFT,
        }
        form = JobForm(data=data, employer=self.unverified_employer)
        self.assertTrue(form.is_valid(), form.errors)
        job = form.save(commit=False)
        job.employer = self.unverified_employer
        job.save()
        self.assertEqual(job.status, Job.Status.DRAFT)

    def test_unverified_employer_cannot_publish_open_job(self):
        from jobs.forms import JobForm
        data = {
            "title": "Open ML Engineer",
            "category": self.category.pk,
            "job_type": Job.JobType.FULL_TIME,
            "experience_level": Job.ExperienceLevel.SENIOR,
            "location": "San Francisco, CA",
            "description": "Machine learning engineering role.",
            "status": Job.Status.OPEN,
        }
        form = JobForm(data=data, employer=self.unverified_employer)
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_unverified_employer_cannot_reopen_closed_job(self):
        job = Job.objects.create(
            employer=self.unverified_employer,
            category=self.category,
            title="Closed Job",
            slug="closed-job-unverified",
            description="Test",
            status=Job.Status.CLOSED,
            location="Remote",
        )
        self.client.login(username="unverified_emp", password="password123")
        res = self.client.get(reverse("jobs:reopen", kwargs={"slug": job.slug}))
        self.assertEqual(res.status_code, 403)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.CLOSED)

    def test_verified_employer_can_publish_and_reopen_job(self):
        from jobs.forms import JobForm
        data = {
            "title": "Published ML Engineer",
            "category": self.category.pk,
            "job_type": Job.JobType.FULL_TIME,
            "experience_level": Job.ExperienceLevel.SENIOR,
            "location": "San Francisco, CA",
            "description": "Machine learning engineering role.",
            "status": Job.Status.OPEN,
        }
        form = JobForm(data=data, employer=self.verified_employer)
        self.assertTrue(form.is_valid(), form.errors)
        job = form.save(commit=False)
        job.employer = self.verified_employer
        job.save()
        self.assertEqual(job.status, Job.Status.OPEN)

        # Verified employer can close and reopen
        job.close()
        self.assertEqual(job.status, Job.Status.CLOSED)
        job.reopen()
        self.assertEqual(job.status, Job.Status.OPEN)


class JobOwnershipTest(TestCase):
    """Test ownership security: only the job owner can touch a job."""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username="owner_emp", email="owner@test.com", password="password123",
            role=User.Role.EMPLOYER, status=User.Status.ACTIVE
        )
        self.intruder = User.objects.create_user(
            username="intruder_emp", email="intruder@test.com", password="password123",
            role=User.Role.EMPLOYER, status=User.Status.ACTIVE
        )
        self.applicant = User.objects.create_user(
            username="applicant_user", email="cand@test.com", password="password123",
            role=User.Role.APPLICANT
        )
        self.category = Category.objects.create(name="DevOps", slug="devops")
        self.job = Job.objects.create(
            employer=self.owner,
            category=self.category,
            title="DevOps Lead",
            slug="devops-lead-owner",
            description="Manage infrastructure",
            status=Job.Status.OPEN,
            location="Remote",
        )

    def test_intruder_cannot_edit_job(self):
        self.client.login(username="intruder@test.com", password="password123")
        res = self.client.get(reverse("jobs:edit", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 403)

        res = self.client.post(reverse("jobs:edit", kwargs={"slug": self.job.slug}), {
            "title": "Hacked Title",
        })
        self.assertEqual(res.status_code, 403)
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, "DevOps Lead")

    def test_intruder_cannot_close_or_reopen_job(self):
        self.client.login(username="intruder@test.com", password="password123")
        res = self.client.post(reverse("jobs:close", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 403)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.OPEN)

    def test_intruder_cannot_delete_job(self):
        self.client.login(username="intruder@test.com", password="password123")
        res = self.client.post(reverse("jobs:delete", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 403)
        self.job.refresh_from_db()
        self.assertNotEqual(self.job.status, Job.Status.REMOVED)

    def test_applicant_cannot_access_employer_job_crud(self):
        self.client.login(username="cand@test.com", password="password123")
        res = self.client.get(reverse("jobs:manage_list"))
        self.assertEqual(res.status_code, 403)

        res = self.client.get(reverse("jobs:create"))
        self.assertEqual(res.status_code, 403)

        res = self.client.get(reverse("jobs:edit", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 403)

    def test_owner_can_edit_close_and_soft_delete_job(self):
        self.client.login(username="owner@test.com", password="password123")

        # Edit
        res = self.client.get(reverse("jobs:edit", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 200)

        # Close
        res = self.client.post(reverse("jobs:close", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.CLOSED)

        # Reopen
        res = self.client.post(reverse("jobs:reopen", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.OPEN)

        # Soft Delete (status=removed)
        res = self.client.post(reverse("jobs:delete", kwargs={"slug": self.job.slug}))
        self.assertEqual(res.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.REMOVED)


class JobCRUDAndTabsTest(TestCase):
    """Test manage list status tabs, soft delete filtering, pipeline links, and HTMX preview."""

    def setUp(self):
        self.client = Client()
        self.employer = User.objects.create_user(
            username="emp_tabs", email="emp_tabs@test.com", password="password123",
            role=User.Role.EMPLOYER, status=User.Status.ACTIVE
        )
        self.applicant = User.objects.create_user(
            username="cand_tabs", email="cand_tabs@test.com", password="password123",
            role=User.Role.APPLICANT
        )
        self.category = Category.objects.create(name="Security", slug="security")

        self.job_open = Job.objects.create(
            employer=self.employer, category=self.category, title="Open Sec Role",
            slug="open-sec-role", status=Job.Status.OPEN, description="X", location="NYC"
        )
        self.job_draft = Job.objects.create(
            employer=self.employer, category=self.category, title="Draft Sec Role",
            slug="draft-sec-role", status=Job.Status.DRAFT, description="X", location="NYC"
        )
        self.job_closed = Job.objects.create(
            employer=self.employer, category=self.category, title="Closed Sec Role",
            slug="closed-sec-role", status=Job.Status.CLOSED, description="X", location="NYC"
        )
        self.job_removed = Job.objects.create(
            employer=self.employer, category=self.category, title="Removed Role",
            slug="removed-role", status=Job.Status.REMOVED, description="X", location="NYC"
        )

        from applications.models import Application
        Application.objects.create(job=self.job_open, applicant=self.applicant)

    def test_manage_list_status_tabs_filtering(self):
        self.client.login(username="emp_tabs@test.com", password="password123")

        # All tab (excludes removed)
        res = self.client.get(reverse("jobs:manage_list"))
        self.assertEqual(res.status_code, 200)
        jobs_in_context = list(res.context["jobs"])
        self.assertEqual(len(jobs_in_context), 3)
        self.assertNotIn(self.job_removed, jobs_in_context)

        # Open tab
        res = self.client.get(reverse("jobs:manage_list") + "?status=open")
        jobs_open = list(res.context["jobs"])
        self.assertEqual(len(jobs_open), 1)
        self.assertEqual(jobs_open[0].pk, self.job_open.pk)

        # Draft tab
        res = self.client.get(reverse("jobs:manage_list") + "?status=draft")
        jobs_draft = list(res.context["jobs"])
        self.assertEqual(len(jobs_draft), 1)
        self.assertEqual(jobs_draft[0].pk, self.job_draft.pk)

        # Closed tab
        res = self.client.get(reverse("jobs:manage_list") + "?status=closed")
        jobs_closed = list(res.context["jobs"])
        self.assertEqual(len(jobs_closed), 1)
        self.assertEqual(jobs_closed[0].pk, self.job_closed.pk)

    def test_application_count_and_pipeline_link(self):
        self.client.login(username="emp_tabs@test.com", password="password123")
        res = self.client.get(reverse("jobs:manage_list"))
        self.assertContains(res, "1 applicant")
        pipeline_url = reverse("jobs:pipeline", kwargs={"slug": self.job_open.slug})
        self.assertContains(res, pipeline_url)

        # Pipeline view accessible
        res_pipe = self.client.get(pipeline_url)
        self.assertEqual(res_pipe.status_code, 200)
        self.assertContains(res_pipe, "Open Sec Role")
        self.assertContains(res_pipe, "cand_tabs")

    def test_htmx_preview_card_endpoint(self):
        self.client.login(username="emp_tabs@test.com", password="password123")
        res = self.client.post(reverse("jobs:preview_card"), {
            "title": "Staff Security Architect",
            "category": self.category.pk,
            "location": "Austin, TX",
            "is_remote": "on",
            "salary_min": "140000",
            "salary_max": "180000",
            "job_type": "full_time",
        })
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Staff Security Architect")
        self.assertContains(res, "Austin, TX")
        self.assertContains(res, "140,000")
        self.assertContains(res, "Security")
