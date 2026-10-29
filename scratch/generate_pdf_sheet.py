"""
Script to generate WorkWise System Flow and Architecture Reference Sheet PDF using ReportLab.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(
                36,
                792 - 25,
                "WorkWise Platform — System Architecture & Flow Reference Sheet",
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 792 - 28, 612 - 36, 792 - 28)

        # Running footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 36, 20, page_text)
        self.drawString(
            36,
            20,
            "CONFIDENTIAL & PROPRIETARY — WorkWise Editorial Job Board Platform",
        )
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 30, 612 - 36, 30)

        self.restoreState()


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=38,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A")    # Deep Slate
    blue_accent = colors.HexColor("#2563EB")      # WorkWise Royal Blue
    teal_accent = colors.HexColor("#0D9488")      # Teal
    dark_gray = colors.HexColor("#334155")
    light_bg = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
    )
    h1_style = ParagraphStyle(
        "H1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=blue_accent,
        spaceBefore=6,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=dark_gray,
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2,
    )
    th_style = ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )
    td_style = ParagraphStyle(
        "TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=dark_gray,
    )
    td_code = ParagraphStyle(
        "TDCode",
        parent=td_style,
        fontName="Courier",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#1E293B"),
    )
    callout_style = ParagraphStyle(
        "Callout",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )

    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 1: TITLE, ARCHITECTURE & ROLE ACCESS
    # ══════════════════════════════════════════════════════════════════════════

    # Document Header Box
    header_content = [
        [
            Paragraph("<b>WORKWISE</b> &bull; PLATFORM SPECIFICATION", ParagraphStyle("MiniHeader", fontName="Helvetica-Bold", fontSize=8, textColor=blue_accent, leading=10)),
            Paragraph("REVISION 2026.1 &bull; PRODUCTION READY", ParagraphStyle("MiniHeaderR", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#64748B"), alignment=2, leading=10)),
        ],
        [
            Paragraph("System Architecture & Workflow Reference Sheet", title_style),
            Paragraph("Status: <b>Fully Connected</b>", ParagraphStyle("StatText", fontName="Helvetica", fontSize=9, textColor=teal_accent, alignment=2)),
        ],
        [
            Paragraph("Comprehensive architectural blueprint, end-to-end user workflows, recruitment pipeline state machine, and endpoint registry for the WorkWise Editorial Job Board.", subtitle_style),
            Paragraph("Django 5/6 &bull; HTMX &bull; SQLite/Postgres", ParagraphStyle("SubR", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#64748B"), alignment=2)),
        ]
    ]
    t_header = Table(header_content, colWidths=[380, 160])
    t_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=blue_accent, spaceBefore=2, spaceAfter=8))

    # Section 1: System Architecture & Technology Stack
    story.append(Paragraph("1. System Architecture & Component Mapping", h1_style))
    arch_intro = (
        "WorkWise utilizes a modular monolith architecture with specialized domain applications: "
        "<b>accounts</b> (authentication, dual-role profiles, security), <b>jobs</b> (listings, sector classification, preview generation), "
        "<b>applications</b> (submission snapshots, Kanban pipeline, interview engine), <b>moderation</b> (flags, audit logging), and "
        "<b>core</b> (routing, home, career acceleration resources, persistent notifications, protected media)."
    )
    story.append(Paragraph(arch_intro, body_style))
    story.append(Spacer(1, 5))

    # Component Table
    comp_data = [
        [Paragraph("Layer", th_style), Paragraph("Technologies", th_style), Paragraph("Architectural Responsibility & Flow Connection", th_style)],
        [
            Paragraph("<b>Presentation</b>", td_style),
            Paragraph("Django Templates, HTMX 1.9+, Vanilla CSS Design Tokens", td_style),
            Paragraph("Dynamic UI without full-page reloads. HTMX powers the real-time job preview card, Kanban column stage transitions, applicant drawer slide-over, and persistent notification polling.", td_style),
        ],
        [
            Paragraph("<b>Security & Proxy</b>", td_style),
            Paragraph("Protected Media View, Rate Limiting, RBAC Decorators", td_style),
            Paragraph("All resume downloads route through <code>core.media_views.protected_media_serve</code>. Access is strictly granted to the owning applicant, hiring employer, or superadmin. Rate limiting caps logins at 5 attempts / 5 mins (HTTP 429).", td_style),
        ],
        [
            Paragraph("<b>Service Layer</b>", td_style),
            Paragraph("applications.services, accounts.backends, core.notifications", td_style),
            Paragraph("Encapsulates business rules: enforced pipeline state transitions (<code>ALLOWED_TRANSITIONS</code>), interview scheduling, official hire notifications, and dual email/username authentication backend.", td_style),
        ],
        [
            Paragraph("<b>Data Layer</b>", td_style),
            Paragraph("SQLite (Dev) / PostgreSQL (Prod), WhiteNoise, Gunicorn", td_style),
            Paragraph("Database models with composite indexes (<code>status</code>, <code>job</code>, <code>applicant</code>), unique application constraints, point-in-time resume snapshotting, and transactional audits.", td_style),
        ],
    ]
    t_comp = Table(comp_data, colWidths=[90, 140, 310])
    t_comp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 8))

    # Section 2: Role-Based Access Control (RBAC) Matrix
    story.append(Paragraph("2. Role-Based Access Control (RBAC) & Permission Matrix", h1_style))
    rbac_data = [
        [Paragraph("Role / Persona", th_style), Paragraph("Status / Level", th_style), Paragraph("Primary URL", th_style), Paragraph("Authorized Capabilities & System Boundaries", th_style)],
        [
            Paragraph("<b>Applicant</b>", td_style),
            Paragraph("<code>active</code>", td_code),
            Paragraph("<code>/applicant/</code>", td_code),
            Paragraph("Browse sector directories, submit applications with resume snapshot, manage saved profile, track timeline, view interview invitations, download career blueprints.", td_style),
        ],
        [
            Paragraph("<b>Employer (Pending)</b>", td_style),
            Paragraph("<code>pending</code>", td_code),
            Paragraph("<code>/employer/pending/</code>", td_code),
            Paragraph("Newly registered organization awaiting administrative trust verification. Can view pending dashboard but cannot publish live jobs or view applicant submissions.", td_style),
        ],
        [
            Paragraph("<b>Employer (Verified)</b>", td_style),
            Paragraph("<code>active</code>", td_code),
            Paragraph("<code>/employer/</code>", td_code),
            Paragraph("Post/edit/close jobs, preview live cards via HTMX, manage candidate Kanban board, inspect candidate drawer, schedule interviews, log interview outcomes, execute official hires.", td_style),
        ],
        [
            Paragraph("<b>Staff Moderator</b>", td_style),
            Paragraph("<code>moderator</code>", td_code),
            Paragraph("<code>/admin-panel/</code>", td_code),
            Paragraph("Review user content flags (spam, scam, misleading), view reported jobs, monitor system audit trails, view pending employer verification queue.", td_style),
        ],
        [
            Paragraph("<b>Superadmin</b>", td_style),
            Paragraph("<code>superadmin</code>", td_code),
            Paragraph("<code>/admin-panel/</code><br/><code>/admin/</code>", td_code),
            Paragraph("Full platform sovereignty: approve/reject employers, suspend/reactivate users, remove infringing listings, inspect immutable audit logs, direct Django admin access.", td_style),
        ],
    ]
    t_rbac = Table(rbac_data, colWidths=[95, 75, 110, 260])
    t_rbac.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_rbac)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2: END-TO-END FLOWS & PIPELINE STATE MACHINE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("3. End-to-End System Workflows", h1_style))
    story.append(Paragraph("Step-by-step lifecycle tracking how actors interact with each subsystem.", body_style))
    story.append(Spacer(1, 4))

    # Flow Cards / Structured Blocks
    flow_boxes = [
        [
            Paragraph("<b>FLOW A: Dual-Role Authentication & Onboarding</b>", h2_style),
            Paragraph(
                "<b>1. Signup (<code>/accounts/register/</code>)</b>: User selects role. Applicants receive immediate <code>active</code> status. Employers receive <code>pending</code> status and are directed to <code>/employer/pending/</code>.<br/>"
                "<b>2. Login (<code>/accounts/login/</code>)</b>: Dual identifier lookup supports email or username via <code>EmailBackend</code>. Login attempt counter checks cache key <code>login_attempts_{IP}</code>. Rate limit triggers HTTP 429 after 5 failed attempts within 300s.<br/>"
                "<b>3. Post-Auth Routing (<code>/accounts/redirect/</code>)</b>: Evaluates <code>user.role</code> &bull; Employer ➔ <code>/employer/</code> &bull; Admin ➔ <code>/admin-panel/</code> &bull; Applicant ➔ <code>/applicant/</code>.<br/>"
                "<b>4. Password Reset & Verification</b>: 4-stage secure flow utilizing 6-digit verification tokens stored in session with expiry.",
                body_style
            ),
        ],
        [
            Paragraph("<b>FLOW B: Job Creation, Validation & Live HTMX Preview</b>", h2_style),
            Paragraph(
                "<b>1. Employer Job Creation (<code>/jobs/post/</code>)</b>: Employer inputs title, department, sector, job type, salary min/max, and currency. Form validates that salary max &ge; salary min.<br/>"
                "<b>2. Real-time Preview (<code>/jobs/preview/</code>)</b>: Form changes trigger an HTMX POST to <code>job_preview_card</code> which returns an uncommitted card rendering the listing exactly as candidates will see it.<br/>"
                "<b>3. Publication & Lifecycle</b>: Jobs default to <code>draft</code> or <code>open</code>. Employers can <code>close</code>, <code>reopen</code>, or soft-delete (<code>status=removed</code>) via <code>/jobs/manage/</code>.",
                body_style
            ),
        ],
        [
            Paragraph("<b>FLOW C: Applicant Discovery, Application & Timeline</b>", h2_style),
            Paragraph(
                "<b>1. Discovery (<code>/jobs/</code>)</b>: Paginated filtering by sector (IT, Healthcare, Education, Engineering, Uniformed Personnel, etc.), Uniformed Branch (Army, Navy, Coast Guard, Police), remote flag, and salary.<br/>"
                "<b>2. Application Submission (<code>/applications/apply/&lt;id&gt;/</code>)</b>: Validates resume format (.pdf, .doc, .docx &le; 30 MB). Copies file into <code>resume_snapshot</code>. Database constraint blocks duplicate applications.<br/>"
                "<b>3. Tracking (<code>/applications/</code>)</b>: Candidate dashboard renders live timeline chips reflecting the exact stage of their application.",
                body_style
            ),
        ],
        [
            Paragraph("<b>FLOW D: Kanban Pipeline, Candidate Drawer & Official Hire</b>", h2_style),
            Paragraph(
                "<b>1. Pipeline Board (<code>/jobs/&lt;slug&gt;/pipeline/</code>)</b>: Seven-column Kanban board grouping candidates by status. HTMX drag/click transitions enforce allowed transitions.<br/>"
                "<b>2. Slide-Over Candidate Drawer (<code>/applications/&lt;pk&gt;/drawer/</code>)</b>: Displays candidate profile, cover letter, verified resume download link, rating, and internal notes.<br/>"
                "<b>3. Interview Scheduling (<code>/applications/&lt;pk&gt;/schedule-interview/</code>)</b>: Creates <code>Interview</code> entity (Phone, Video, Onsite, Technical) and publishes ticket badge on candidate dashboard.<br/>"
                "<b>4. Official Hire Confirmation</b>: Employer specifies confirmed <code>start_date</code> and personalized <code>hire_message</code>. System updates status to <code>hired</code> and delivers an immediate notification to candidate.",
                body_style
            ),
        ],
        [
            Paragraph("<b>FLOW E: Administration, Trust Verification & Audit Logging</b>", h2_style),
            Paragraph(
                "<b>1. Verification Queue (<code>/admin-panel/verifications/</code>)</b>: Admin reviews pending employer profiles and clicks Approve (sets status <code>active</code>) or Reject.<br/>"
                "<b>2. Moderation & Content Flags (<code>/moderation/flags/</code>)</b>: Users flag suspicious listings; moderators investigate, resolve, or remove the listing.<br/>"
                "<b>3. User Suspension (<code>/admin-panel/users/&lt;pk&gt;/suspend/</code>)</b>: Superadmin suspends malicious accounts. Suspended users are locked out on login.<br/>"
                "<b>4. Immutable Audit Trail (<code>/admin-panel/audit-log/</code>)</b>: All administrative decisions are permanently written to <code>AuditLog</code> with actor, action, target, and timestamp.",
                body_style
            ),
        ],
    ]
    t_flow = Table(flow_boxes, colWidths=[540])
    t_flow.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_flow)
    story.append(Spacer(1, 8))

    # Section 4: Pipeline State Machine
    story.append(Paragraph("4. Recruitment Pipeline State Machine & Transition Rules", h1_style))
    state_intro = (
        "Candidate progression is strictly controlled in <code>applications.services.ALLOWED_TRANSITIONS</code>. "
        "Any transition outside this specification raises a <code>ValidationError</code> preventing state corruption."
    )
    story.append(Paragraph(state_intro, body_style))
    story.append(Spacer(1, 4))

    sm_data = [
        [Paragraph("Current Status", th_style), Paragraph("Allowed Target Transitions", th_style), Paragraph("Business Logic & Automation Triggered", th_style)],
        [
            Paragraph("<code>submitted</code>", td_code),
            Paragraph("<code>under_review</code>, <code>shortlisted</code>, <code>rejected</code>", td_code),
            Paragraph("Initial application state upon submission. Resume snapshot locked.", td_style),
        ],
        [
            Paragraph("<code>under_review</code>", td_code),
            Paragraph("<code>shortlisted</code>, <code>interview_scheduled</code>, <code>rejected</code>", td_code),
            Paragraph("Hiring committee reviewing candidate portfolio and resume.", td_style),
        ],
        [
            Paragraph("<code>shortlisted</code>", td_code),
            Paragraph("<code>interview_scheduled</code>, <code>offer_extended</code>, <code>hired</code>, <code>rejected</code>, <code>under_review</code>", td_code),
            Paragraph("Qualified candidate pool. Employer can revert to review if necessary.", td_style),
        ],
        [
            Paragraph("<code>interview_scheduled</code>", td_code),
            Paragraph("<code>offer_extended</code>, <code>hired</code>, <code>shortlisted</code>, <code>rejected</code>", td_code),
            Paragraph("Active interview slot scheduled. Displays meeting links to applicant.", td_style),
        ],
        [
            Paragraph("<code>offer_extended</code>", td_code),
            Paragraph("<code>hired</code>, <code>rejected</code>", td_code),
            Paragraph("Formal employment proposal presented to candidate.", td_style),
        ],
        [
            Paragraph("<code>hired</code>", td_code),
            Paragraph("<b>None (Terminal State)</b>", td_style),
            Paragraph("Requires <code>start_date</code> & <code>hire_message</code>. Dispatches celebratory in-app notification with onboarding schedule.", td_style),
        ],
        [
            Paragraph("<code>rejected</code>", td_code),
            Paragraph("<code>under_review</code> <i>(Re-open candidate)</i>", td_style),
            Paragraph("Candidate notified. Employer can optionally restore candidate back to review.", td_style),
        ],
        [
            Paragraph("<code>withdrawn</code>", td_code),
            Paragraph("<b>None (Terminal State)</b>", td_style),
            Paragraph("Self-service candidate action. Sets <code>withdrawn_at</code> timestamp.", td_style),
        ],
    ]
    t_sm = Table(sm_data, colWidths=[110, 180, 250])
    t_sm.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_sm)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 3: URL ROUTING MAP & NOTIFICATION ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("5. Master URL Routing & Endpoint Directory", h1_style))
    story.append(Paragraph("Comprehensive mapping of all registered system URLs across applications.", body_style))
    story.append(Spacer(1, 4))

    urls_data = [
        [Paragraph("Category", th_style), Paragraph("URL Pattern", th_style), Paragraph("View Handler", th_style), Paragraph("Description & Access Rule", th_style)],
        # Core & Public
        [Paragraph("<b>Core</b>", td_style), Paragraph("<code>/</code>", td_code), Paragraph("<code>core.views.home</code>", td_code), Paragraph("Public landing page with featured jobs, sectors & stats.", td_style)],
        [Paragraph("<b>Core</b>", td_style), Paragraph("<code>/dashboard/</code>", td_code), Paragraph("<code>core.views.dashboard</code>", td_code), Paragraph("Authenticated role router redirecting to role dashboard.", td_style)],
        [Paragraph("<b>Core</b>", td_style), Paragraph("<code>/applicant/</code>", td_code), Paragraph("<code>core.views.applicant_dashboard</code>", td_code), Paragraph("Applicant hub: application stats, upcoming interviews.", td_style)],
        [Paragraph("<b>Core</b>", td_style), Paragraph("<code>/employer/</code>", td_code), Paragraph("<code>core.views.employer_dashboard</code>", td_code), Paragraph("Employer overview: active jobs, applicant counts.", td_style)],
        [Paragraph("<b>Core</b>", td_style), Paragraph("<code>/employer/pending/</code>", td_code), Paragraph("<code>core.views.employer_pending</code>", td_code), Paragraph("Verification holding screen for unapproved employers.", td_style)],
        [Paragraph("<b>Core / Career</b>", td_style), Paragraph("<code>/resume-blueprint/</code>", td_code), Paragraph("<code>core.views.resume_blueprint</code>", td_code), Paragraph("ATS resume templates and downloadable industry formats.", td_style)],
        [Paragraph("<b>Core / Career</b>", td_style), Paragraph("<code>/resume-blueprint/interactive/</code>", td_code), Paragraph("<code>core.views.resume_blueprint_interactive</code>", td_code), Paragraph("Interactive in-browser editable Navy Blueprint resume.", td_style)],
        [Paragraph("<b>Core / Career</b>", td_style), Paragraph("<code>/interview-mastery/</code>", td_code), Paragraph("<code>core.views.interview_mastery</code>", td_code), Paragraph("STAR framework guide and interview preparation handbook.", td_style)],
        [Paragraph("<b>Core / Notif</b>", td_style), Paragraph("<code>/notifications/state/</code>", td_code), Paragraph("<code>core.notifications.notifications_state</code>", td_code), Paragraph("HTMX endpoint returning unread count and dropdown list.", td_style)],
        # Accounts
        [Paragraph("<b>Accounts</b>", td_style), Paragraph("<code>/accounts/login/</code>", td_code), Paragraph("<code>accounts.views.LoginView</code>", td_code), Paragraph("Authentication view with rate limiting (5 attempts/5 mins).", td_style)],
        [Paragraph("<b>Accounts</b>", td_style), Paragraph("<code>/accounts/register/</code>", td_code), Paragraph("<code>accounts.views.SignupView</code>", td_code), Paragraph("Dual-role registration toggle (Applicant / Employer).", td_style)],
        [Paragraph("<b>Accounts</b>", td_style), Paragraph("<code>/accounts/profile/</code>", td_code), Paragraph("<code>accounts.views.profile_view</code>", td_code), Paragraph("Manage avatar, bio, headline, skills, and master resume.", td_style)],
        [Paragraph("<b>Accounts</b>", td_style), Paragraph("<code>/accounts/password-reset/</code>", td_code), Paragraph("<code>accounts.views.WorkWisePasswordResetView</code>", td_code), Paragraph("4-stage verification code password reset process.", td_style)],
        # Jobs
        [Paragraph("<b>Jobs</b>", td_style), Paragraph("<code>/jobs/</code>", td_code), Paragraph("<code>jobs.views.job_list</code>", td_code), Paragraph("Searchable job board with sector, branch, salary filters.", td_style)],
        [Paragraph("<b>Jobs</b>", td_style), Paragraph("<code>/jobs/manage/</code>", td_code), Paragraph("<code>jobs.views.employer_job_list</code>", td_code), Paragraph("Employer listing manager (Draft, Open, Closed, Removed).", td_style)],
        [Paragraph("<b>Jobs</b>", td_style), Paragraph("<code>/jobs/post/</code>", td_code), Paragraph("<code>jobs.views.job_create</code>", td_code), Paragraph("Post new job with instant HTMX preview card support.", td_style)],
        [Paragraph("<b>Jobs</b>", td_style), Paragraph("<code>/jobs/preview/</code>", td_code), Paragraph("<code>jobs.views.job_preview_card</code>", td_code), Paragraph("HTMX live preview card partial generator.", td_style)],
        [Paragraph("<b>Jobs</b>", td_style), Paragraph("<code>/jobs/&lt;slug&gt;/pipeline/</code>", td_code), Paragraph("<code>jobs.views.job_pipeline</code>", td_code), Paragraph("Interactive Kanban applicant review board.", td_style)],
        # Applications
        [Paragraph("<b>Applications</b>", td_style), Paragraph("<code>/applications/apply/&lt;id&gt;/</code>", td_code), Paragraph("<code>applications.views.apply</code>", td_code), Paragraph("Application submit engine with point-in-time resume snapshot.", td_style)],
        [Paragraph("<b>Applications</b>", td_style), Paragraph("<code>/applications/</code>", td_code), Paragraph("<code>applications.views.my_applications</code>", td_code), Paragraph("Applicant submission history with stage chips.", td_style)],
        [Paragraph("<b>Applications</b>", td_style), Paragraph("<code>/applications/&lt;pk&gt;/drawer/</code>", td_code), Paragraph("<code>applications.views.application_drawer</code>", td_code), Paragraph("Slide-over candidate inspection panel.", td_style)],
        [Paragraph("<b>Applications</b>", td_style), Paragraph("<code>/applications/&lt;pk&gt;/transition/</code>", td_code), Paragraph("<code>applications.views.application_transition</code>", td_code), Paragraph("Enforce status change, official hire message & start date.", td_style)],
        [Paragraph("<b>Applications</b>", td_style), Paragraph("<code>/applications/&lt;pk&gt;/schedule-interview/</code>", td_code), Paragraph("<code>applications.views.schedule_interview_view</code>", td_code), Paragraph("Schedule interview slot and emit ticket.", td_style)],
        # Admin & Moderation
        [Paragraph("<b>Admin Panel</b>", td_style), Paragraph("<code>/admin-panel/</code>", td_code), Paragraph("<code>admin_panel_views.admin_panel_dashboard</code>", td_code), Paragraph("Platform operations dashboard and metric tiles.", td_style)],
        [Paragraph("<b>Admin Panel</b>", td_style), Paragraph("<code>/admin-panel/verifications/</code>", td_code), Paragraph("<code>admin_panel_views.admin_verification_queue</code>", td_code), Paragraph("Approve or reject pending employer registrations.", td_style)],
        [Paragraph("<b>Admin Panel</b>", td_style), Paragraph("<code>/admin-panel/users/&lt;pk&gt;/suspend/</code>", td_code), Paragraph("<code>admin_panel_views.admin_user_suspend</code>", td_code), Paragraph("Superadmin action to suspend offending users.", td_style)],
        [Paragraph("<b>Admin Panel</b>", td_style), Paragraph("<code>/admin-panel/audit-log/</code>", td_code), Paragraph("<code>admin_panel_views.admin_audit_log</code>", td_code), Paragraph("Immutable platform audit log of administrator actions.", td_style)],
        [Paragraph("<b>Security</b>", td_style), Paragraph("<code>/media/&lt;path&gt;</code>", td_code), Paragraph("<code>core.media_views.protected_media_serve</code>", td_code), Paragraph("Permission-gated file serving proxy for uploaded resumes.", td_style)],
    ]
    t_urls = Table(urls_data, colWidths=[70, 150, 160, 160])
    t_urls.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_urls)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 4: DATA MODELS, DEMO CREDENTIALS & QUICKSTART
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("6. Relational Data Models & Key Schema Architecture", h1_style))
    story.append(Paragraph("Core database entities and foreign-key relationships supporting platform operations.", body_style))
    story.append(Spacer(1, 4))

    schema_data = [
        [Paragraph("Model Entity", th_style), Paragraph("Application", th_style), Paragraph("Key Fields & Schema Attributes", th_style), Paragraph("Relational Connections & Constraints", th_style)],
        [
            Paragraph("<b>User</b>", td_style),
            Paragraph("<code>accounts</code>", td_code),
            Paragraph("<code>role</code> (applicant, employer, admin), <code>status</code> (active, pending, suspended), <code>access_level</code> (moderator, superadmin), avatar, bio, phone, location.", td_style),
            Paragraph("Extends <code>AbstractUser</code>. 1:1 with EmployerProfile or ApplicantProfile. Target of all audit logs and notifications.", td_style),
        ],
        [
            Paragraph("<b>EmployerProfile</b>", td_style),
            Paragraph("<code>accounts</code>", td_code),
            Paragraph("<code>company_name</code>, <code>company_size</code>, <code>industry</code>, <code>founded_year</code>, <code>linkedin_url</code>, <code>company_logo</code>.", td_style),
            Paragraph("OneToOneField to User (role='employer'). Verification status tied to user status.", td_style),
        ],
        [
            Paragraph("<b>ApplicantProfile</b>", td_style),
            Paragraph("<code>accounts</code>", td_code),
            Paragraph("<code>headline</code>, <code>resume</code> (master), <code>experience_level</code>, <code>skills</code> (CSV), <code>available_from</code>, portfolio/social links.", td_style),
            Paragraph("OneToOneField to User (role='applicant'). Master resume validated by <code>validate_resume_file</code>.", td_style),
        ],
        [
            Paragraph("<b>Job</b>", td_style),
            Paragraph("<code>jobs</code>", td_code),
            Paragraph("<code>title</code>, <code>slug</code>, <code>status</code> (draft, open, paused, closed, filled, removed), <code>job_field</code>, <code>uniformed_branch</code>, <code>department</code>, <code>job_type</code>, <code>salary_min</code>, <code>salary_max</code>.", td_style),
            Paragraph("FK to User (employer). FK to Category (null=True). Has many JobTag and Application entities.", td_style),
        ],
        [
            Paragraph("<b>Application</b>", td_style),
            Paragraph("<code>applications</code>", td_code),
            Paragraph("<code>status</code>, <code>cover_letter</code>, <code>resume_snapshot</code>, <code>rating</code> (1-5), <code>employer_notes</code>, <code>start_date</code>, <code>hire_message</code>, <code>applied_at</code>.", td_style),
            Paragraph("FK to User (applicant), FK to Job. <b>UniqueConstraint(applicant, job)</b>. Has many Interview records.", td_style),
        ],
        [
            Paragraph("<b>Interview</b>", td_style),
            Paragraph("<code>applications</code>", td_code),
            Paragraph("<code>scheduled_at</code>, <code>duration_minutes</code>, <code>format</code> (phone, video, onsite, technical), <code>meeting_link</code>, <code>outcome</code>.", td_style),
            Paragraph("FK to Application. Generates upcoming interview cards on applicant and employer dashboards.", td_style),
        ],
        [
            Paragraph("<b>Notification</b>", td_style),
            Paragraph("<code>core</code>", td_code),
            Paragraph("<code>kind</code>, <code>message</code>, <code>highlight</code>, <code>detail_title</code>, <code>description</code>, <code>is_read</code>, <code>read_at</code>, <code>pills</code>, <code>action_url</code>.", td_style),
            Paragraph("FK to User. Read state managed server-side. Polled or updated reactively via HTMX.", td_style),
        ],
        [
            Paragraph("<b>AuditLog</b>", td_style),
            Paragraph("<code>moderation</code>", td_code),
            Paragraph("<code>actor</code>, <code>action</code> (approve, reject, suspend, reactivate, remove), <code>target_type</code>, <code>target_id</code>, <code>ip_address</code>, <code>timestamp</code>.", td_style),
            Paragraph("Immutable compliance log tracking every significant moderation and administrative action.", td_style),
        ],
    ]
    t_schema = Table(schema_data, colWidths=[90, 65, 205, 180])
    t_schema.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 8))

    # Section 7: Seed Accounts & Developer Quickstart
    story.append(Paragraph("7. Demonstration Seed Accounts & Execution Reference", h1_style))
    story.append(Paragraph("Pre-configured testing accounts with specific roles, profiles, and initial test data.", body_style))
    story.append(Spacer(1, 4))

    cred_data = [
        [Paragraph("Role", th_style), Paragraph("Login Identifier", th_style), Paragraph("Password", th_style), Paragraph("Entity / Profile Name", th_style), Paragraph("Initial State / Target Dashboard", th_style)],
        [
            Paragraph("<b>Superadmin</b>", td_style),
            Paragraph("<code>admin@workwise.dev</code><br/><i>(or 'admin')</i>", td_code),
            Paragraph("<code>admin1234</code>", td_code),
            Paragraph("Platform Superadmin", td_style),
            Paragraph("Redirects to <code>/admin-panel/</code>. Full access to user management, verification, audit logs.", td_style),
        ],
        [
            Paragraph("<b>Employer 1</b>", td_style),
            Paragraph("<code>employer1@workwise.dev</code><br/><i>(or 'employer1')</i>", td_code),
            Paragraph("<code>employer1234</code>", td_code),
            Paragraph("<b>Synapse Labs</b><br/>(Metro Health & Tech)", td_style),
            Paragraph("Redirects to <code>/employer/</code>. Verified employer with open job postings & active candidate pipeline.", td_style),
        ],
        [
            Paragraph("<b>Employer 2</b>", td_style),
            Paragraph("<code>employer2@workwise.dev</code><br/><i>(or 'employer2')</i>", td_code),
            Paragraph("<code>employer1234</code>", td_code),
            Paragraph("<b>Orbit Systems</b><br/>(National Defense Agency)", td_style),
            Paragraph("Redirects to <code>/employer/</code>. Verified employer with candidate submissions under review.", td_style),
        ],
        [
            Paragraph("<b>Applicant 1</b>", td_style),
            Paragraph("<code>applicant1@workwise.dev</code><br/><i>(or 'applicant1')</i>", td_code),
            Paragraph("<code>applicant1234</code>", td_code),
            Paragraph("Alex Rivera / Chen<br/>(Cloud Infrastructure)", td_style),
            Paragraph("Redirects to <code>/applicant/</code>. Has submitted applications across multiple technical roles.", td_style),
        ],
        [
            Paragraph("<b>Applicant 2</b>", td_style),
            Paragraph("<code>applicant2@workwise.dev</code><br/><i>(or 'applicant2')</i>", td_code),
            Paragraph("<code>applicant1234</code>", td_code),
            Paragraph("Sam Chen / Sarah Johnson<br/>(Critical Care Nursing)", td_style),
            Paragraph("Redirects to <code>/applicant/</code>. Candidate with active interview schedule ticket.", td_style),
        ],
    ]
    t_cred = Table(cred_data, colWidths=[75, 120, 80, 125, 140])
    t_cred.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_cred)
    story.append(Spacer(1, 8))

    # CLI Quick Reference Box
    cli_content = [
        [
            Paragraph("<b>Developer Quick Commands Reference</b>", h2_style),
        ],
        [
            Paragraph(
                "&bull; <b>Run Dev Server:</b> <code>python manage.py runserver</code><br/>"
                "&bull; <b>Re-seed Demo Data:</b> <code>python manage.py seed_demo --flush</code> <i>(Admin: admin1234 / Others: password123)</i><br/>"
                "&bull; <b>Run Test Suite:</b> <code>python manage.py test</code> &bull; Specific app: <code>python manage.py test applications</code><br/>"
                "&bull; <b>Production Docker Build:</b> <code>docker build -t inkboard:latest . && docker run -p 8000:8000 inkboard:latest</code>",
                body_style
            ),
        ]
    ]
    t_cli = Table(cli_content, colWidths=[540])
    t_cli.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cli)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")


if __name__ == "__main__":
    output_filename = "WorkWise_System_Flow_and_Architecture_Sheet.pdf"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    build_pdf(output_filename)
