"""
accounts/tests.py — Model tests for the accounts app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import EmployerProfile, ApplicantProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for the custom User model."""

    def setUp(self):
        self.employer = User.objects.create_user(
            username="emp1",
            email="emp1@test.com",
            password="testpass123",
            role=User.Role.EMPLOYER,
            first_name="Alice",
            last_name="Smith",
        )
        self.applicant = User.objects.create_user(
            username="app1",
            email="app1@test.com",
            password="testpass123",
            role=User.Role.APPLICANT,
            first_name="Bob",
            last_name="Jones",
        )
        self.admin = User.objects.create_user(
            username="adm1",
            email="adm1@test.com",
            password="testpass123",
            role=User.Role.ADMIN,
        )

    def test_str_with_full_name(self):
        self.assertEqual(str(self.employer), "Alice Smith (employer)")

    def test_str_with_username_fallback(self):
        u = User.objects.create_user(username="noname", password="x", role=User.Role.APPLICANT)
        self.assertIn("noname", str(u))

    def test_is_employer_property(self):
        self.assertTrue(self.employer.is_employer)
        self.assertFalse(self.applicant.is_employer)

    def test_is_applicant_property(self):
        self.assertTrue(self.applicant.is_applicant)
        self.assertFalse(self.employer.is_applicant)

    def test_is_admin_user_property(self):
        self.assertTrue(self.admin.is_admin_user)
        self.assertFalse(self.employer.is_admin_user)

    def test_default_role_is_applicant(self):
        u = User.objects.create_user(username="default_u", password="x")
        self.assertEqual(u.role, User.Role.APPLICANT)

    def test_role_choices_values(self):
        roles = [r.value for r in User.Role]
        self.assertIn("admin", roles)
        self.assertIn("employer", roles)
        self.assertIn("applicant", roles)

    def test_meta_ordering(self):
        """Users should be ordered by -date_joined."""
        users = list(User.objects.all())
        for i in range(len(users) - 1):
            self.assertGreaterEqual(users[i].date_joined, users[i + 1].date_joined)


class EmployerProfileTest(TestCase):
    """Tests for EmployerProfile."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="emp_profile",
            password="x",
            role=User.Role.EMPLOYER,
        )
        # Signal creates the profile on user save — update it with test data
        self.profile = EmployerProfile.objects.get(user=self.user)
        self.profile.company_name = "TestCo"
        self.profile.save()

    def test_str(self):
        self.assertEqual(str(self.profile), "TestCo")

    def test_profile_company_name(self):
        self.assertEqual(self.profile.company_name, "TestCo")

    def test_company_size_choices(self):
        sizes = [s.value for s in EmployerProfile.CompanySize]
        self.assertIn("1-10", sizes)
        self.assertIn("1000+", sizes)

    def test_one_to_one_relation(self):
        self.user.refresh_from_db()
        self.assertEqual(
            EmployerProfile.objects.get(user=self.user).company_name, "TestCo"
        )


class ApplicantProfileTest(TestCase):
    """Tests for ApplicantProfile."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="app_profile",
            password="x",
            role=User.Role.APPLICANT,
            first_name="Carol",
            last_name="White",
        )
        # Signal creates the profile on user save — update it with test data
        self.profile = ApplicantProfile.objects.get(user=self.user)
        self.profile.headline = "Python Developer"
        self.profile.skills = "Python, Django, REST"
        self.profile.save()

    def test_str(self):
        self.assertIn("Python Developer", str(self.profile))

    def test_skills_list(self):
        expected = ["Python", "Django", "REST"]
        self.assertEqual(self.profile.skills_list(), expected)

    def test_skills_list_empty(self):
        self.profile.skills = ""
        self.assertEqual(self.profile.skills_list(), [])

    def test_experience_level_choices(self):
        levels = [l.value for l in ApplicantProfile.ExperienceLevel]
        self.assertIn("entry", levels)
        self.assertIn("senior", levels)

    def test_one_to_one_relation(self):
        self.user.refresh_from_db()
        self.assertEqual(
            ApplicantProfile.objects.get(user=self.user).headline, "Python Developer"
        )


class UserSignalTest(TestCase):
    """Test that profile objects are auto-created via signals."""

    def test_employer_profile_created_on_user_save(self):
        u = User.objects.create_user(
            username="sig_emp", password="x", role=User.Role.EMPLOYER
        )
        self.assertTrue(EmployerProfile.objects.filter(user=u).exists())

    def test_applicant_profile_created_on_user_save(self):
        u = User.objects.create_user(
            username="sig_app", password="x", role=User.Role.APPLICANT
        )
        self.assertTrue(ApplicantProfile.objects.filter(user=u).exists())

    def test_admin_user_no_profile_created(self):
        u = User.objects.create_user(
            username="sig_adm", password="x", role=User.Role.ADMIN
        )
        self.assertFalse(EmployerProfile.objects.filter(user=u).exists())
        self.assertFalse(ApplicantProfile.objects.filter(user=u).exists())


class PasswordResetVerificationFlowTest(TestCase):
    """Integration test suite for verification code password reset flow."""

    def setUp(self):
        self.applicant = User.objects.create_user(
            username="testuser",
            email="resetuser@example.com",
            password="OriginalPassword123!",
            role=User.Role.APPLICANT,
            first_name="Jane",
            last_name="Doe",
        )
        self.employer = User.objects.create_user(
            username="employeruser",
            email="employer@example.com",
            password="EmployerPassword123!",
            role=User.Role.EMPLOYER,
            first_name="Acme",
            last_name="Corp",
        )

    def test_password_reset_request_valid_email(self):
        response = self.client.post("/accounts/password-reset/", {"email": "resetuser@example.com"})
        self.assertRedirects(response, "/accounts/password-reset/verify/")
        session = self.client.session
        self.assertEqual(session.get("reset_email"), "resetuser@example.com")
        self.assertEqual(session.get("reset_user_id"), self.applicant.id)
        self.assertTrue(len(str(session.get("reset_code"))) == 6)

    def test_password_reset_request_invalid_email(self):
        response = self.client.post("/accounts/password-reset/", {"email": "notfound@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No registered account was found")

    def test_password_reset_resend_code(self):
        # Initial request
        self.client.post("/accounts/password-reset/", {"email": "resetuser@example.com"})
        code1 = self.client.session.get("reset_code")

        # Resend code
        response = self.client.post("/accounts/password-reset/resend/")
        self.assertEqual(response.status_code, 200)
        code2 = self.client.session.get("reset_code")
        self.assertTrue(len(str(code2)) == 6)

    def test_verify_invalid_code_fails(self):
        self.client.post("/accounts/password-reset/", {"email": "resetuser@example.com"})
        response = self.client.post("/accounts/password-reset/verify/", {"code": "000000"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid verification code")
        self.assertFalse(self.client.session.get("reset_verified"))

    def test_verify_correct_code_success(self):
        self.client.post("/accounts/password-reset/", {"email": "resetuser@example.com"})
        correct_code = self.client.session.get("reset_code")
        response = self.client.post("/accounts/password-reset/verify/", {"code": correct_code})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.session.get("reset_verified"))

    def test_decision_no_keeps_password_and_redirects_to_dashboard(self):
        # Setup verified session
        self.client.post("/accounts/password-reset/", {"email": "resetuser@example.com"})
        correct_code = self.client.session.get("reset_code")
        self.client.post("/accounts/password-reset/verify/", {"code": correct_code})

        # User chooses 'No' (Keep existing password)
        response = self.client.post("/accounts/password-reset/decision/", {"decision": "no"})
        self.assertRedirects(response, "/applicant/")

        # Verify password is unchanged
        self.applicant.refresh_from_db()
        self.assertTrue(self.applicant.check_password("OriginalPassword123!"))

    def test_decision_no_for_employer_redirects_to_employer_dashboard(self):
        # Setup verified session for employer
        self.client.post("/accounts/password-reset/", {"email": "employer@example.com"})
        correct_code = self.client.session.get("reset_code")
        self.client.post("/accounts/password-reset/verify/", {"code": correct_code})

        # Employer chooses 'No'
        response = self.client.post("/accounts/password-reset/decision/", {"decision": "no"})
        self.assertRedirects(response, "/employer/")

    def test_decision_yes_navigates_to_change_password(self):
        self.client.post("/accounts/password-reset/", {"email": "resetuser@example.com"})
        correct_code = self.client.session.get("reset_code")
        self.client.post("/accounts/password-reset/verify/", {"code": correct_code})

        response = self.client.post("/accounts/password-reset/decision/", {"decision": "yes"})
        self.assertRedirects(response, "/accounts/password-reset/change/")

    def test_change_password_success_sets_permanent_password(self):
        # Setup verified session
        self.client.post("/accounts/password-reset/", {"email": "resetuser@example.com"})
        correct_code = self.client.session.get("reset_code")
        self.client.post("/accounts/password-reset/verify/", {"code": correct_code})

        # Submit new password
        response = self.client.post("/accounts/password-reset/change/", {
            "new_password1": "BrandNewSecurePassword2026!",
            "new_password2": "BrandNewSecurePassword2026!",
        })
        self.assertRedirects(response, "/applicant/")

        # Verify new password is set permanently
        self.applicant.refresh_from_db()
        self.assertTrue(self.applicant.check_password("BrandNewSecurePassword2026!"))
        self.assertFalse(self.applicant.check_password("OriginalPassword123!"))

        # Check that user can log in with new password
        login_res = self.client.post("/accounts/login/", {
            "username": "resetuser@example.com",
            "password": "BrandNewSecurePassword2026!",
        })
        self.assertRedirects(login_res, "/applicant/")

