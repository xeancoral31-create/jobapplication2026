# WorkWise — Editorial Job Board Platform

**WorkWise** is a modern, editorial job-board web application built with Django, Vanilla CSS, HTMX, and SQLite/PostgreSQL. It connects high-growth companies with qualified candidates across diverse sectors—including Information Technology, Nursing & Healthcare, Education, Engineering, Uniformed Personnel (Army, Navy, Coast Guard, Police), and Public Service.

The platform is designed around strict role-based access control (RBAC), an interactive Kanban recruitment pipeline with enforced state transitions, candidate slide-over inspection drawers, server-side persistent notifications, and secure media access controls.

---

## Table of Contents
1. [System Architecture & Core Technologies](#system-architecture--core-technologies)
2. [User Roles & Permission Hierarchy](#user-roles--permission-hierarchy)
3. [End-to-End System Flows](#end-to-end-system-flows)
   - [A. Authentication & Onboarding Flow](#a-authentication--onboarding-flow)
   - [B. Applicant Discovery & Application Flow](#b-applicant-discovery--application-flow)
   - [C. Employer Job Lifecycle & Pipeline Flow](#c-employer-job-lifecycle--pipeline-flow)
   - [D. Interview Scheduling & Official Hire Flow](#d-interview-scheduling--official-hire-flow)
   - [E. Admin Moderation & Audit Flow](#e-admin-moderation--audit-flow)
4. [Recruitment Pipeline State Machine](#recruitment-pipeline-state-machine)
5. [Database Schema & Key Models](#database-schema--key-models)
6. [Complete System URL & Route Registry](#complete-system-url--route-registry)
7. [Career Acceleration Modules](#career-acceleration-modules)
8. [Security & Media Protection Architecture](#security--media-protection-architecture)
9. [Seed Demonstration Accounts](#seed-demonstration-accounts)
10. [Local Development & Quickstart](#local-development--quickstart)
11. [Testing & Verification](#testing--verification)

---

## System Architecture & Core Technologies

```
                     ┌─────────────────────────────────────────┐
                     │          WorkWise Web Interface         │
                     │    (Django Templates + HTMX + CSS)      │
                     └────────────────────┬────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     ┌────────────────────────┐                      ┌────────────────────────┐
     │   Public & Applicant   │                      │  Employer & Management │
     │  - Job Discovery       │                      │  - Job Postings & Live │
     │  - Apply Engine        │                      │    HTMX Previews       │
     │  - Status Timeline     │                      │  - Kanban Review Board │
     │  - Career Resources    │                      │  - Candidate Drawer    │
     │  - Live Notification   │                      │  - Interview Schedule  │
     └───────────┬────────────┘                      └───────────┬────────────┘
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                     ┌─────────────────────────────────────────┐
                     │          Business & Service Layer       │
                     │  - Role Routing & Permission Guards     │
                     │  - Pipeline State Machine Transitions   │
                     │  - Protected Media Security Proxy       │
                     │  - Persistent Notification Dispatcher   │
                     │  - EmailJS Verification Service         │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │          Database & Storage Layer       │
                     │     SQLite / PostgreSQL (dj-database-url)│
                     │       Local / Protected Media Storage   │
                     └─────────────────────────────────────────┘
```

- **Backend Framework**: Django 5/6 (modular settings split: `base.py`, `dev.py`, `prod.py`).
- **Dynamic Frontend**: HTMX 1.9+ for reactive live preview cards, Kanban updates, and slide-over drawers without heavy single-page application (SPA) overhead.
- **Styling**: Vanilla CSS design system with CSS custom properties (design tokens), accessible focus rings, and WCAG AA compliant color contrast.
- **Database**: SQLite (local development) / PostgreSQL (production via `dj-database-url`).
- **Media Security**: Custom authentication view (`core.media_views.protected_media_serve`) shielding candidate resumes from unauthorized public access.

---

## User Roles & Permission Hierarchy

| Role | Access Level / Status | Primary Dashboard | Key Permissions & System Capabilities |
|---|---|---|---|
| **Applicant** | `active` | `/applicant/` | Search and filter jobs, submit applications with resume snapshots, track application progress timeline, manage profile and stored resume, access career blueprints. |
| **Employer** | `pending` | `/employer/pending/` | Newly registered employer awaiting platform administrator verification. Read-only preview access; cannot publish live jobs. |
| **Employer** | `active` (verified) | `/employer/` | Create and manage jobs, inspect live HTMX preview cards, manage Kanban review pipeline, transition candidate stages, schedule interviews, execute official hires. |
| **Admin** | `moderator` | `/admin-panel/` | Review flagged content, inspect user listings, view verification queue, inspect jobs. |
| **Admin** | `superadmin` | `/admin-panel/` | Full platform control: approve/reject employers, suspend/reactivate users, remove infringing job listings, audit logs, access standard Django `/admin/`. |

---

## End-to-End System Flows

### A. Authentication & Onboarding Flow
1. **Registration (`/accounts/register/`)**:
   - The user selects either **Applicant** or **Employer** role.
   - Applicants are created with status `active` and redirected immediately to `/applicant/`.
   - Employers are created with status `pending` and routed to `/employer/pending/` until an administrator approves their organization in the Admin Verification Queue.
2. **Login & Dual-Identifier Authentication (`/accounts/login/`)**:
   - Authenticates using either **email address** or **username** via `EmailBackend`.
   - Rate limiting enforced: maximum of 5 failed attempts within 5 minutes per IP (returns `HTTP 429 Too Many Requests`).
   - Automatically directs the user to their respective role dashboard via `/accounts/redirect/` (`_role_redirect_url`).
3. **Password Reset Flow**:
   - Multi-step security verification: request code (`/accounts/password-reset/`), 6-digit verification code sent via console/EmailJS, code confirmation (`/verify/`), decision confirmation (`/decision/`), and password update (`/change/`).

### B. Applicant Discovery & Application Flow
1. **Browsing & Discovery (`/jobs/`, `/jobs/positions/`, `/jobs/category/<slug>/`)**:
   - Real-time search across job titles, descriptions, and tags.
   - Comprehensive filtering by:
     - **Career Fields**: Information Technology, Nursing & Healthcare, Education, Engineering, Business & Finance, Hospitality & Tourism, Government & Public Service, Uniformed Personnel.
     - **Uniformed Branches**: Army, Navy, Coast Guard, Police.
     - **Work Style**: Remote toggle, Employment Type (Full-Time, Part-Time, Contractual, Internship, Temporary), Location, Minimum Salary.
2. **Application Submission (`/applications/apply/<job_id>/`)**:
   - File validation strictly restricts resumes to `.pdf`, `.doc`, `.docx` up to 30 MB.
   - Applicants can either upload a dedicated resume or reuse their profile's master resume.
   - The application creates a point-in-time `resume_snapshot` ensuring that subsequent updates to the applicant's profile do not alter submitted applications.
   - Unique constraint (`unique_application_per_job`) prevents duplicate applications to the same listing.
3. **Tracking & Timeline (`/applications/`, `/applications/<pk>/`)**:
   - Interactive progress bar and status stamps reflecting real-time pipeline status:
     `Submitted` ➔ `Under Review` ➔ `Shortlisted` ➔ `Interview Scheduled` ➔ `Offer Extended` ➔ `Hired`.
   - Candidates can gracefully withdraw an application (`/applications/<pk>/withdraw/`).

### C. Employer Job Lifecycle & Pipeline Flow
1. **Job Creation & Live Preview (`/jobs/post/`, `/jobs/preview/`)**:
   - Input job title, department, career field, uniformed branch (if applicable), job type, salary range, and currency.
   - An HTMX endpoint renders an instantaneous live preview card of the listing exactly as applicants see it.
   - Validation ensures `salary_max` is strictly greater than or equal to `salary_min`.
2. **Job Management (`/jobs/manage/`)**:
   - Tabbed status navigation: Drafts, Active Open Listings, Closed, and Archived.
   - Quick action controls to edit (`/edit/`), close (`/close/`), reopen (`/reopen/`), or soft-delete (`/delete/`).
3. **Kanban Pipeline Board (`/jobs/<slug>/pipeline/`)**:
   - Dedicated multi-column board grouping candidates by status column.
   - Drag or click transitions with dynamic permission checks.
   - Slide-over Candidate Drawer (`/applications/<pk>/drawer/`) displaying candidate qualifications, cover letter, verified resume download, internal notes, and rating.

### D. Interview Scheduling & Official Hire Flow
1. **Interview Scheduling (`/applications/<pk>/schedule-interview/`)**:
   - Employers set scheduled date/time, duration, format (Phone, Video Call, On-site, Technical), and meeting links.
   - Generates interview ticket badges on applicant dashboards.
   - Outcome logging (`/applications/interviews/<pk>/record-result/`) with notes.
2. **Official Hire Workflow (`/applications/<pk>/transition/`)**:
   - When moving a candidate into the **Hired** stage, the employer specifies:
     - Confirmed official work start date (`start_date`).
     - Personalized welcome and onboarding message (`hire_message`).
   - The system transitions the job application to `hired`, records the timestamp, and immediately dispatches a persistent in-app notification (`create_hire_notification`) directly to the candidate's account.

### E. Admin Moderation & Audit Flow
1. **Platform Control Center (`/admin-panel/`)**:
   - Aggregated operational metrics: pending verifications, active listings, reported flags, and user breakdown.
2. **Employer Verification Queue (`/admin-panel/verifications/`)**:
   - Inspect applicant-facing employer details and approve (`/approve/`) or reject (`/reject/`) organizations.
3. **User Management (`/admin-panel/users/`)**:
   - Superadmins can suspend accounts (`/suspend/`) or restore access (`/reactivate/`).
4. **Job Moderation & Content Flags (`/admin-panel/jobs/`, `/moderation/flags/`)**:
   - Review reported listings flagged by users for spam, scams, or inaccurate data.
   - Take down non-compliant listings (`/remove/`).
5. **Immutable Audit Trail (`/admin-panel/audit-log/`)**:
   - System records actor, target model, action type (`approve`, `reject`, `suspend`, `remove`), IP, and timestamp.

---

## Recruitment Pipeline State Machine

Candidate status transitions are strictly governed by `applications/services.py` through `ALLOWED_TRANSITIONS`:

```
                ┌─────────────┐
                │  SUBMITTED  │
                └──────┬──────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
 ┌──────────────┐             ┌──────────────┐
 │ UNDER_REVIEW │             │   REJECTED   │◄─────────┐
 └──────┬───────┘             └──────┬───────┘          │
        │                            │ (reopen candidate)
        │                            ▼                  │
        │                     ┌──────────────┐          │
        │                     │ UNDER_REVIEW │          │
        │                     └──────────────┘          │
        │                                               │
        ├────────────────────────────┐                  │
        ▼                            ▼                  │
 ┌─────────────┐             ┌──────────────────┐       │
 │ SHORTLISTED │────────────►│INTERVIEW_SCHEDULE│       │
 └──────┬──────┘             └────────┬─────────┘       │
        │                             │                 │
        ├─────────────────────────────┤                 │
        ▼                             ▼                 │
 ┌──────────────┐             ┌──────────────┐          │
 │OFFER_EXTENDED│────────────►│    HIRED     │          │
 └──────┬───────┘             │  (Terminal)  │          │
        │                     └──────────────┘          │
        └───────────────────────────────────────────────┘
```

### Transition Table

| Starting Stage | Permitted Target Stages |
|---|---|
| `submitted` | `under_review`, `shortlisted`, `rejected` |
| `under_review` | `shortlisted`, `interview_scheduled`, `rejected` |
| `shortlisted` | `interview_scheduled`, `offer_extended`, `hired`, `rejected`, `under_review` |
| `interview_scheduled` | `offer_extended`, `hired`, `shortlisted`, `rejected` |
| `offer_extended` | `hired`, `rejected` |
| `hired` | *Terminal State* |
| `rejected` | `under_review` *(Allows re-opening a previously rejected candidate)* |
| `withdrawn` | *Terminal State* *(Candidate self-service)* |

---

## Database Schema & Key Models

- **`accounts.User`**: Custom user extending `AbstractUser`. Includes `role` (`applicant`, `employer`, `admin`), `status` (`active`, `pending`, `suspended`), `access_level` (`moderator`, `superadmin`), avatar, bio, phone, and location.
- **`accounts.EmployerProfile`**: Attached 1:1 to employer users. Stores `company_name`, `company_logo`, `company_size`, `industry`, `founded_year`, and social links.
- **`accounts.ApplicantProfile`**: Attached 1:1 to applicant users. Stores `headline`, default `resume`, `experience_level`, `skills` (comma-separated with helper `skills_list()`), and portfolio URLs.
- **`jobs.Category`**: Industry categories with SVG icons and color tags.
- **`jobs.Job`**: Job postings. Features `status` (`draft`, `open`, `paused`, `closed`, `filled`, `removed`), `job_field`, `uniformed_branch`, `department`, `job_type`, `experience_level`, salary figures (`salary_min`, `salary_max`, `salary_currency`, `salary_period`), and relational tags (`JobTag`).
- **`applications.Application`**: Candidate submissions with unique constraint per `(applicant, job)`. Stores `cover_letter`, `resume_snapshot`, `status`, `rating` (1–5), `employer_notes`, `start_date`, and `hire_message`.
- **`applications.Interview`**: Interview records containing `scheduled_at`, `duration_minutes`, `format` (`phone`, `video`, `onsite`, `technical`), `meeting_link`, and `outcome`.
- **`core.Notification`**: Server-side persistent user notifications with `is_read`, `read_at`, action URLs, badge chips, and category tags.
- **`moderation.Flag` & `moderation.AuditLog`**: Moderation reporting system and immutable administrator action log.

---

## Complete System URL & Route Registry

### Core & Platform Endpoints (`/`)
| Path | View / Handler | Description |
|---|---|---|
| `/` | `core.views.home` | Public homepage featuring search, featured jobs, and categories |
| `/dashboard/` | `core.views.dashboard` | Role-based redirector to respective role dashboard |
| `/applicant/` | `core.views.applicant_dashboard` | Applicant hub: status metrics, recent applications, interviews |
| `/employer/` | `core.views.employer_dashboard` | Employer dashboard: active jobs, candidate statistics |
| `/employer/pending/` | `core.views.employer_pending` | Status holding screen for newly registered employers |
| `/styleguide/` | `core.views.styleguide` | Living design system guide showcasing CSS components and tokens |
| `/resume-blueprint/` | `core.views.resume_blueprint` | ATS Resume templates and career downloads |
| `/resume-blueprint/interactive/` | `core.views.resume_blueprint_interactive` | Interactive in-browser editable Navy Blueprint resume |
| `/resume-blueprint/download/` | `core.views.download_resume_template` | Template bundle download endpoint (.doc, .txt, .zip) |
| `/interview-mastery/` | `core.views.interview_mastery` | Behavioral & STAR framework interview guide |
| `/interview-mastery/download/` | `core.views.download_interview_guide` | Full interview guide text export |
| `/notifications/state/` | `core.notifications.notifications_state` | HTMX endpoint for persistent unread notification counts |
| `/notifications/mark-all-read/` | `core.notifications.notifications_mark_all_read` | Batch mark all notifications read |
| `/notifications/<pk>/read/` | `core.notifications.notification_mark_read` | Mark individual notification read |

### Authentication & Account Endpoints (`/accounts/`)
| Path | View / Handler | Description |
|---|---|---|
| `/accounts/login/` | `accounts.views.LoginView` | Split-screen authentication with IP rate limiting |
| `/accounts/logout/` | `accounts.views.LogoutView` | Clears user session |
| `/accounts/register/` | `accounts.views.SignupView` | Dual-role registration (Applicant / Employer) |
| `/accounts/redirect/` | `accounts.views.role_redirect` | Post-login redirector based on user role |
| `/accounts/profile/` | `accounts.views.profile_view` | User profile, avatar, resume, and experience editor |
| `/accounts/password-reset/` | `accounts.views.WorkWisePasswordResetView` | Step 1: Request password reset verification code |
| `/accounts/password-reset/verify/` | `accounts.views.PasswordResetVerifyView` | Step 2: Validate 6-digit verification code |
| `/accounts/password-reset/decision/` | `accounts.views.PasswordResetDecisionView` | Step 3: Account recovery options |
| `/accounts/password-reset/change/` | `accounts.views.PasswordResetChangeView` | Step 4: Submit new password |
| `/accounts/change-password/` | `accounts.views.PasswordChangeSettingView` | In-app authenticated password change |

### Job Management Endpoints (`/jobs/`)
| Path | View / Handler | Description |
|---|---|---|
| `/jobs/` | `jobs.views.job_list` | Public searchable directory with filtering and pagination |
| `/jobs/positions/` | `jobs.views.positions_by_field` | Dynamic position suggestions by sector |
| `/jobs/category/<slug>/` | `jobs.views.category_detail` | Sector-specific job listings |
| `/jobs/manage/` | `jobs.views.employer_job_list` | Employer listing management console |
| `/jobs/post/` | `jobs.views.job_create` | Multi-field job posting editor |
| `/jobs/preview/` | `jobs.views.job_preview_card` | HTMX reactive preview card generator |
| `/jobs/<slug>/edit/` | `jobs.views.job_edit` | Edit existing job parameters |
| `/jobs/<slug>/close/` | `jobs.views.job_close` | Close job listing to new applicants |
| `/jobs/<slug>/reopen/` | `jobs.views.job_reopen` | Reopen a previously closed job listing |
| `/jobs/<slug>/delete/` | `jobs.views.job_delete` | Soft delete job (`status=removed`) |
| `/jobs/<slug>/pipeline/` | `jobs.views.job_pipeline` | Full Kanban applicant review board |
| `/jobs/<slug>/` | `jobs.views.job_detail` | Public job detail page with application CTA |

### Candidate Application Endpoints (`/applications/`)
| Path | View / Handler | Description |
|---|---|---|
| `/applications/apply/<job_id>/` | `applications.views.apply` | Submit application with cover letter & resume snapshot |
| `/applications/` | `applications.views.my_applications` | Applicant portal: view history and status progress |
| `/applications/<pk>/` | `applications.views.application_detail` | Detailed application progress and interview schedule |
| `/applications/<pk>/withdraw/` | `applications.views.withdraw` | Applicant voluntary application withdrawal |
| `/applications/<pk>/transition/` | `applications.views.application_transition` | Move candidate to a different pipeline stage |
| `/applications/<pk>/drawer/` | `applications.views.application_drawer` | Slide-over candidate inspection panel |
| `/applications/<pk>/schedule-interview/` | `applications.views.schedule_interview_view` | Schedule new interview slot |
| `/applications/interviews/<pk>/record-result/` | `applications.views.record_interview_result_view` | Record interview outcome and evaluations |
| `/applications/<pk>/resume/` | `applications.views.download_resume` | Download submitted candidate resume snapshot |

### Platform Administration Endpoints (`/admin-panel/`)
| Path | View / Handler | Description |
|---|---|---|
| `/admin-panel/` | `core.admin_panel_views.admin_panel_dashboard` | Executive overview and moderation statistics |
| `/admin-panel/verifications/` | `core.admin_panel_views.admin_verification_queue` | Employer organization review queue |
| `/admin-panel/verifications/<pk>/approve/` | `core.admin_panel_views.admin_employer_approve` | Approve employer organization |
| `/admin-panel/verifications/<pk>/reject/` | `core.admin_panel_views.admin_employer_reject` | Reject employer organization |
| `/admin-panel/users/` | `core.admin_panel_views.admin_user_list` | User registry and permission manager |
| `/admin-panel/users/<pk>/suspend/` | `core.admin_panel_views.admin_user_suspend` | Suspend user account |
| `/admin-panel/users/<pk>/reactivate/` | `core.admin_panel_views.admin_user_reactivate` | Reactivate suspended user |
| `/admin-panel/jobs/` | `core.admin_panel_views.admin_job_list` | Platform-wide job listing directory |
| `/admin-panel/jobs/<pk>/remove/` | `core.admin_panel_views.admin_job_remove` | Moderate or remove violating job |
| `/admin-panel/audit-log/` | `core.admin_panel_views.admin_audit_log` | Immutable platform activity audit log |
| `/moderation/flags/` | `moderation.views.flag_list` | User flag reports review |
| `/moderation/report/<type>/<id>/` | `moderation.views.report_content` | Submit content report |

---

## Career Acceleration Modules

1. **ATS Resume Blueprint (`/resume-blueprint/`)**:
   - Curated ATS-compliant resume templates tailored to career sectors (Engineering, Healthcare, Executive, Tech, and Universal).
   - In-browser interactive editable template with instant live styling (`/resume-blueprint/interactive/`).
   - One-click template downloads in `.doc` (Word-compatible) and plain text formats.
2. **Interview Mastery Handbook (`/interview-mastery/`)**:
   - Structured interview frameworks covering Behavioral (STAR method), Technical Assessments, Executive Leadership, and Case Interviews.
   - Complete handbook downloadable as a comprehensive study guide (`/interview-mastery/download/`).

---

## Security & Media Protection Architecture

### Protected Media Serving (`/media/<path:path>`)
Uploaded resumes contain sensitive personal contact data and must not be exposed to the public internet:
1. All requests to `/media/` are routed through `core.media_views.protected_media_serve`.
2. Public and unauthenticated visitors are denied (`HTTP 403 Forbidden`).
3. For candidate resumes (`/media/resumes/` or `/media/application_resumes/`):
   - Access is permitted strictly to:
     - The **applicant** who submitted the resume.
     - The **employer** who owns the job posting associated with the application.
     - Authenticated **platform administrators** (`is_staff` / `is_superuser`).
4. File type integrity: strictly verified at upload to allow only `.pdf`, `.doc`, `.docx` up to a maximum size of 30 MB.

---

## Seed Demonstration Accounts

The platform includes pre-configured demonstration accounts for immediate exploration across all roles.

### Primary Pre-Populated Database Accounts

| Role | Username / Login Identifier | Password | Associated Organization / Profile | Target Dashboard |
|---|---|---|---|---|
| **Superadmin** | `admin` (`admin@workwise.dev`) | `admin1234` | Platform Operations & Trust | `/admin-panel/` |
| **Employer** | `employer1` (`employer1@workwise.dev`) | `employer1234` | **Synapse Labs** (Verified Tech Employer) | `/employer/` |
| **Employer** | `employer2` (`employer2@workwise.dev`) | `employer1234` | **Orbit Systems** (Verified Systems Employer) | `/employer/` |
| **Employer** | `employer3` (`employer3@workwise.dev`) | `password123` | **Apex Global Services** | `/employer/` |
| **Applicant** | `applicant1` (`applicant1@workwise.dev`) | `applicant1234` | Alex Rivera (Cloud Engineer) | `/applicant/` |
| **Applicant** | `applicant2` (`applicant2@workwise.dev`) | `applicant1234` | Sam Chen (Critical Care Nurse) | `/applicant/` |
| **Applicant** | `applicant3` (`applicant3@workwise.dev`) | `applicant1234` | David Kim (Financial Analyst) | `/applicant/` |

> *Note: Both username and email address are accepted in the login form.*

### Seeding or Resetting Demo Data
To re-generate or reset demonstration data at any time:
```bash
# Seed demo categories, jobs, applicants, and pipeline data
python manage.py seed_demo

# Flush database first and re-seed clean demonstration state
python manage.py seed_demo --flush
```
*(Accounts created directly by `python manage.py seed_demo` use password `admin1234` for admin and `password123` for demo employers/applicants).*

---

## Local Development & Quickstart

### Prerequisites
- Python 3.11+
- Virtual environment (`venv`)

### 1. Installation
```bash
# Navigate to project workspace
cd "Job Appilication (test)"

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Migrations
```bash
python manage.py migrate
```

### 3. Run Development Server
```bash
python manage.py runserver
```
Open [http://localhost:8000/](http://localhost:8000/) in your web browser.

---

## Testing & Verification

Run the test suite across all modular Django applications:
```bash
# Run all unit and integration tests
python manage.py test

# Run tests by specific module
python manage.py test accounts
python manage.py test jobs
python manage.py test applications
python manage.py test moderation
python manage.py test core
```

---

## Technical Reference Sheet (PDF)
A companion printable documentation and system flow reference document is available in the project root:
- [`WorkWise_System_Flow_and_Architecture_Sheet.pdf`](./WorkWise_System_Flow_and_Architecture_Sheet.pdf)
