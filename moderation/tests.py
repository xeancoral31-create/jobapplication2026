"""
moderation/tests.py — Model tests for Flag and AuditLog.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from moderation.models import Flag, AuditLog
from jobs.models import Job

User = get_user_model()


class FlagModelTest(TestCase):

    def setUp(self):
        self.reporter = User.objects.create_user(
            username="reporter1", password="x", role=User.Role.APPLICANT
        )
        self.employer = User.objects.create_user(
            username="flagged_emp", password="x", role=User.Role.EMPLOYER
        )
        self.job = Job.objects.create(
            employer=self.employer,
            title="Flagged Job",
            slug="flagged-job",
            description="Suspicious listing",
            location="Unknown",
        )
        ct = ContentType.objects.get_for_model(Job)
        self.flag = Flag.objects.create(
            reporter=self.reporter,
            content_type=ct,
            object_id=self.job.pk,
            reason=Flag.Reason.SPAM,
            status=Flag.FlagStatus.OPEN,
            description="This looks like spam.",
        )

    def test_str(self):
        s = str(self.flag)
        self.assertIn("spam", s)
        self.assertIn("job", s.lower())

    def test_reason_choices(self):
        reasons = [r.value for r in Flag.Reason]
        for r in ["spam", "inappropriate", "misleading", "duplicate", "scam", "other"]:
            self.assertIn(r, reasons)

    def test_flag_status_choices(self):
        statuses = [s.value for s in Flag.FlagStatus]
        for s in ["open", "under_review", "resolved", "dismissed"]:
            self.assertIn(s, statuses)

    def test_default_status_open(self):
        ct = ContentType.objects.get_for_model(Job)
        flag = Flag.objects.create(
            reporter=self.reporter,
            content_type=ct,
            object_id=self.job.pk,
            reason=Flag.Reason.OTHER,
        )
        self.assertEqual(flag.status, Flag.FlagStatus.OPEN)

    def test_generic_relation(self):
        self.assertEqual(self.flag.content_object, self.job)

    def test_meta_ordering(self):
        ct = ContentType.objects.get_for_model(Job)
        flag2 = Flag.objects.create(
            reporter=self.reporter,
            content_type=ct,
            object_id=self.job.pk,
            reason=Flag.Reason.SCAM,
        )
        flags = list(Flag.objects.all())
        self.assertEqual(flags[0], flag2)  # newest first


class AuditLogModelTest(TestCase):

    def setUp(self):
        self.actor = User.objects.create_user(
            username="actor1", password="x", role=User.Role.ADMIN, is_staff=True
        )
        ct = ContentType.objects.get_for_model(User)
        self.log = AuditLog.objects.create(
            actor=self.actor,
            content_type=ct,
            object_id=self.actor.pk,
            object_repr=str(self.actor),
            action=AuditLog.Action.UPDATE,
            changes={"role": ["applicant", "admin"]},
            ip_address="127.0.0.1",
        )

    def test_str(self):
        s = str(self.log)
        self.assertIn("actor1", s)
        self.assertIn("update", s)

    def test_action_choices(self):
        actions = [a.value for a in AuditLog.Action]
        for a in ["create", "update", "delete", "approve", "reject", "ban", "restore"]:
            self.assertIn(a, actions)

    def test_changes_field_is_dict(self):
        self.assertIsInstance(self.log.changes, dict)
        self.assertEqual(self.log.changes["role"], ["applicant", "admin"])

    def test_meta_ordering(self):
        ct = ContentType.objects.get_for_model(User)
        log2 = AuditLog.objects.create(
            actor=self.actor,
            content_type=ct,
            object_id=self.actor.pk,
            object_repr="newer",
            action=AuditLog.Action.CREATE,
        )
        logs = list(AuditLog.objects.all())
        self.assertEqual(logs[0], log2)  # newest first


class AdminPanelAndModerationTest(TestCase):
    """
    Stage 6 Tests:
      - Each action writes an AdminAction (admin, target_type, target_id, action) through one helper.
      - Permissions per access_level (moderators cannot suspend users, superadmins can do everything).
      - Employer verification queue (approve/reject).
      - Job moderation (remove job).
      - User management (search by role/status, suspend/reactivate).
      - Audit log page filtered by admin, target_type, date.
    """

    def setUp(self):
        # 1. Superadmin user
        self.superadmin = User.objects.create_user(
            username="super_alice",
            email="alice@inkboard.dev",
            password="password123",
            role=User.Role.ADMIN,
            access_level=User.AccessLevel.SUPERADMIN,
            is_staff=True,
            is_superuser=True,
        )

        # 2. Moderator user
        self.moderator = User.objects.create_user(
            username="mod_bob",
            email="bob@inkboard.dev",
            password="password123",
            role=User.Role.ADMIN,
            access_level=User.AccessLevel.MODERATOR,
            is_staff=True,
            is_superuser=False,
        )

        # 3. Regular Applicant
        self.applicant = User.objects.create_user(
            username="charlie_app",
            email="charlie@test.com",
            password="password123",
            role=User.Role.APPLICANT,
            status=User.Status.ACTIVE,
        )

        # 4. Pending Employer
        self.pending_employer = User.objects.create_user(
            username="pending_emp",
            email="emp@startup.io",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.PENDING,
        )
        self.pending_employer.is_verified = False
        self.pending_employer.save()

        # 5. Active Employer & Job
        self.active_employer = User.objects.create_user(
            username="active_emp",
            email="corp@acme.com",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.ACTIVE,
        )
        self.active_employer.is_verified = True
        self.active_employer.save()

        self.job = Job.objects.create(
            employer=self.active_employer,
            title="Backend Architect",
            slug="backend-architect",
            description="Build scalable systems.",
            location="Remote",
            status=Job.Status.OPEN,
        )

    def test_log_admin_action_helper_writes_admin_action(self):
        """Helper correctly creates an AdminAction record with admin, target_type, target_id, action."""
        from moderation.services import log_admin_action
        from moderation.models import AdminAction

        action_entry = log_admin_action(
            admin=self.superadmin,
            target_type="user",
            target_id=self.applicant.pk,
            action="custom_audit",
            object_repr="Test User Representation",
            changes={"status": ["old", "new"]},
        )

        self.assertIsNotNone(action_entry.pk)
        self.assertEqual(action_entry.admin, self.superadmin)
        self.assertEqual(action_entry.actor, self.superadmin)
        self.assertEqual(action_entry.target_type, "user")
        self.assertEqual(action_entry.target_id, self.applicant.pk)
        self.assertEqual(action_entry.action, "custom_audit")
        self.assertEqual(action_entry.object_repr, "Test User Representation")

        # Verify queryable via AdminAction
        queried = AdminAction.objects.filter(admin=self.superadmin, target_type="user", target_id=self.applicant.pk).first()
        self.assertEqual(queried, action_entry)

    def test_superadmin_can_suspend_user_and_writes_admin_action(self):
        """Superadmin suspends user: status becomes suspended and AdminAction is written."""
        from moderation.services import suspend_user
        from moderation.models import AdminAction

        action = suspend_user(self.applicant, self.superadmin)

        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.status, User.Status.SUSPENDED)
        self.assertTrue(self.applicant.is_suspended)

        # Check AdminAction
        self.assertEqual(action.admin, self.superadmin)
        self.assertEqual(action.target_type, "user")
        self.assertEqual(action.target_id, self.applicant.pk)
        self.assertEqual(action.action, "suspend")

        db_action = AdminAction.objects.filter(target_type="user", target_id=self.applicant.pk, action="suspend").first()
        self.assertIsNotNone(db_action)
        self.assertEqual(db_action.admin, self.superadmin)

    def test_moderator_cannot_suspend_user_direct_and_view(self):
        """Moderators cannot suspend users (raises PermissionDenied / returns 403)."""
        from django.core.exceptions import PermissionDenied
        from moderation.services import suspend_user
        from django.urls import reverse

        # 1. Direct service call
        with self.assertRaises(PermissionDenied):
            suspend_user(self.applicant, self.moderator)

        # Verify applicant is NOT suspended
        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.status, User.Status.ACTIVE)

        # 2. View endpoint call
        self.client.login(username="mod_bob", password="password123")
        url = reverse("core:admin_user_suspend", kwargs={"pk": self.applicant.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)

        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.status, User.Status.ACTIVE)

    def test_moderator_and_superadmin_can_reactivate_user(self):
        """Both moderator and superadmin can reactivate suspended accounts and each writes an AdminAction."""
        from moderation.services import reactivate_user
        from moderation.models import AdminAction

        self.applicant.status = User.Status.SUSPENDED
        self.applicant.save()

        # Moderator reactivates
        action = reactivate_user(self.applicant, self.moderator)
        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.status, User.Status.ACTIVE)

        self.assertEqual(action.admin, self.moderator)
        self.assertEqual(action.target_type, "user")
        self.assertEqual(action.action, "reactivate")

        log = AdminAction.objects.filter(admin=self.moderator, target_id=self.applicant.pk, action="reactivate").first()
        self.assertIsNotNone(log)

    def test_employer_verification_approval_and_rejection(self):
        """Approve sets is_verified=True, status=active; Reject sets is_verified=False, status=suspended."""
        from moderation.services import approve_employer, reject_employer
        from moderation.models import AdminAction

        # Approve
        action_appr = approve_employer(self.pending_employer, self.moderator)
        self.pending_employer.refresh_from_db()
        self.assertTrue(self.pending_employer.is_verified)
        self.assertEqual(self.pending_employer.status, User.Status.ACTIVE)
        self.assertEqual(action_appr.action, "approve")
        self.assertEqual(action_appr.target_type, "employer")

        log_appr = AdminAction.objects.filter(target_id=self.pending_employer.pk, action="approve").first()
        self.assertIsNotNone(log_appr)
        self.assertEqual(log_appr.admin, self.moderator)

        # Reject another employer
        other_pending = User.objects.create_user(
            username="spam_emp",
            email="spam@fake.xyz",
            password="password123",
            role=User.Role.EMPLOYER,
            status=User.Status.PENDING,
        )
        other_pending.is_verified = False
        other_pending.save()

        action_rej = reject_employer(other_pending, self.superadmin)
        other_pending.refresh_from_db()
        self.assertFalse(other_pending.is_verified)
        self.assertEqual(other_pending.status, User.Status.SUSPENDED)
        self.assertEqual(action_rej.action, "reject")

        log_rej = AdminAction.objects.filter(target_id=other_pending.pk, action="reject").first()
        self.assertIsNotNone(log_rej)
        self.assertEqual(log_rej.admin, self.superadmin)

    def test_job_moderation_removes_job_and_writes_admin_action(self):
        """remove_job sets job.status=removed and writes AdminAction."""
        from moderation.services import remove_job
        from moderation.models import AdminAction

        action = remove_job(self.job, self.moderator)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.REMOVED)

        self.assertEqual(action.admin, self.moderator)
        self.assertEqual(action.target_type, "job")
        self.assertEqual(action.target_id, self.job.pk)
        self.assertEqual(action.action, "remove")

        log = AdminAction.objects.filter(target_type="job", target_id=self.job.pk, action="remove").first()
        self.assertIsNotNone(log)

    def test_audit_log_page_filtered_by_admin_target_type_and_date(self):
        """Audit log page filters properly by admin, target_type, and date."""
        from django.urls import reverse
        from moderation.services import log_admin_action
        from django.utils import timezone

        # Create varied admin actions
        log_admin_action(self.superadmin, "user", self.applicant.pk, "suspend")
        log_admin_action(self.moderator, "job", self.job.pk, "remove")
        log_admin_action(self.moderator, "employer", self.pending_employer.pk, "approve")

        self.client.login(username="super_alice", password="password123")
        base_url = reverse("core:admin_audit_log")

        # 1. Filter by admin
        resp = self.client.get(f"{base_url}?admin={self.moderator.pk}")
        self.assertEqual(resp.status_code, 200)
        logs = resp.context["logs"]
        self.assertEqual(len(logs), 2)
        for l in logs:
            self.assertEqual(l.admin, self.moderator)

        # 2. Filter by target_type
        resp = self.client.get(f"{base_url}?target_type=job")
        self.assertEqual(resp.status_code, 200)
        logs = resp.context["logs"]
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].target_type, "job")

        # 3. Filter by date
        today_str = timezone.now().strftime("%Y-%m-%d")
        resp = self.client.get(f"{base_url}?date={today_str}")
        self.assertEqual(resp.status_code, 200)
        logs = resp.context["logs"]
        self.assertEqual(len(logs), 3)

    def test_non_admin_cannot_access_admin_panel(self):
        """Applicants and Employers cannot access /admin-panel/ or its endpoints (403)."""
        from django.urls import reverse

        # Login as applicant
        self.client.login(username="charlie_app", password="password123")

        urls_to_test = [
            reverse("core:admin_panel"),
            reverse("core:admin_users"),
            reverse("core:admin_verifications"),
            reverse("core:admin_jobs"),
            reverse("core:admin_audit_log"),
            reverse("core:admin_user_suspend", kwargs={"pk": self.applicant.pk}),
            reverse("core:admin_employer_approve", kwargs={"pk": self.pending_employer.pk}),
            reverse("core:admin_job_remove", kwargs={"pk": self.job.pk}),
        ]

        for u in urls_to_test:
            # Try GET or POST
            resp = self.client.get(u)
            if resp.status_code != 403:
                resp = self.client.post(u)
            self.assertEqual(resp.status_code, 403, f"Expected 403 on {u} for applicant, got {resp.status_code}")

    def test_user_management_search_by_role_and_status(self):
        """User management page filters by search keyword, role, and status."""
        from django.urls import reverse

        self.client.login(username="super_alice", password="password123")
        url = reverse("core:admin_users")

        # Filter by role=applicant
        resp = self.client.get(f"{url}?role=applicant")
        self.assertEqual(resp.status_code, 200)
        users = resp.context["users"]
        self.assertTrue(all(u.role == User.Role.APPLICANT for u in users))

        # Filter by status=pending
        resp = self.client.get(f"{url}?status=pending")
        self.assertEqual(resp.status_code, 200)
        users = resp.context["users"]
        self.assertTrue(all(u.status == User.Status.PENDING for u in users))

        # Search keyword
        resp = self.client.get(f"{url}?q=charlie")
        self.assertEqual(resp.status_code, 200)
        users = resp.context["users"]
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, "charlie_app")

