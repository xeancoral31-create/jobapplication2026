# Script to update core/career_resources.py with rich Universal and multi-career ATS templates
import re

universal_text = """[YOUR FULL NAME]
[City, State / Region] | [Phone Number] | [Professional Email Address]
[LinkedIn Profile URL] | [Portfolio, Personal Website, or Work Samples URL]

──────────────────────────────────────────────────────────────────────────────
PROFESSIONAL SUMMARY
──────────────────────────────────────────────────────────────────────────────
[Job Title / Target Professional Role] with [Number]+ years of demonstrated experience in [Industry / Field of Specialization]. Proven track record of improving operational efficiency by [X]%, managing [Key Function / Account / Team Size], and delivering high-impact results under tight deadlines. Skilled in [Core Skill 1], [Core Skill 2], and cross-functional team collaboration. Adept at applying data-driven strategies and industry best practices to achieve organizational goals.

──────────────────────────────────────────────────────────────────────────────
CORE COMPETENCIES & PROFESSIONAL SKILLS
──────────────────────────────────────────────────────────────────────────────
• Domain Expertise: [Core Skill 1], [Core Skill 2], [Core Skill 3], [Core Skill 4]
• Tools & Systems: [Software / Tool 1], [Platform / ERP / CRM 2], [Technical Tool 3]
• Operations & Methodologies: [Process / Standard 1], [Compliance / Framework 2]
• Interpersonal & Leadership: Stakeholder Management, Team Leadership, Problem Resolution

──────────────────────────────────────────────────────────────────────────────
PROFESSIONAL EXPERIENCE
──────────────────────────────────────────────────────────────────────────────
[Job Title / Position] | [Company / Organization Name] — [City, State / Country]
[Start Month, Year] – Present
• Spearheaded [Initiative / Major Project], increasing [Key Metric: Revenue / Output / Patient Care / Productivity] by [X]% over [Timeframe].
• Implemented [Methodology / Process / Tool], reducing [Cost / Operational Downtime / Processing Time] by [Y]% ($[Amount Saved] annually).
• Led and mentored a cross-functional team of [Number] staff members, achieving a [Z]% on-time delivery rate across [Number] key milestones.
• Standardized operating documentation and quality assurance protocols, reducing error rates from [Old Number]% to [New Number]%.

[Previous Job Title] | [Previous Company / Organization Name] — [City, State / Country]
[Start Month, Year] – [End Month, Year]
• Coordinated day-to-day operations for [Department / Function], supporting [Client Count / Project Portfolio / Operations] valued at $[Value].
• Analyzed operational bottlenecks in [Specific Area] and designed an automated / revised workflow, cutting turnaround time by [X]%.
• Authored comprehensive reports and delivered strategic presentations to executive leadership, informing critical resource allocation.
• Commended by leadership / clients for [Specific Notable Accomplishment or Award Name].

──────────────────────────────────────────────────────────────────────────────
KEY PROJECTS & MAJOR ACCOMPLISHMENTS
──────────────────────────────────────────────────────────────────────────────
[Project Title or Key Strategic Initiative] | [Organization or Independent]
• Planned and delivered [Project Scope / Objective], resulting in [Concrete Quantifiable Outcome / Adoption / Recognition].
• Managed [Resource / Budget / Cross-functional team], completing deliverable [X] weeks ahead of target schedule.

──────────────────────────────────────────────────────────────────────────────
EDUCATION & PROFESSIONAL CREDENTIALS
──────────────────────────────────────────────────────────────────────────────
[Degree / Diploma / Certification] in [Field of Study / Discipline]
[University / College / Institution Name] — [Graduation Year]
• Academic Honors / Distinctions: [e.g., Magna Cum Laude, Dean's List, Top 5%] (Optional)
• Professional License / Certification: [Official License Title, Issuing Authority, Year]
• Continuing Professional Development: [Relevant Workshop, Seminar, or Specialized Training]
"""

healthcare_text = """[FULL NAME], RN, BSN / MD
[City, State / Region] | [Phone Number] | [Professional Email Address]
[LinkedIn Profile URL] | [State Board License # / Registry ID]

──────────────────────────────────────────────────────────────────────────────
PROFESSIONAL SUMMARY
──────────────────────────────────────────────────────────────────────────────
Compassionate, board-certified [Nursing / Healthcare Professional Title] with [Number]+ years of clinical experience in [Specialty: e.g., Critical Care, Emergency, Telemetry, Pediatrics, Outpatient]. Demonstrated expertise in patient assessment, medication administration, life support protocols, and multidisciplinary care planning. Proven record of maintaining 98%+ patient satisfaction scores and zero-incident medication error compliance. Dedicated to evidence-based practice and compassionate patient advocacy.

──────────────────────────────────────────────────────────────────────────────
CLINICAL COMPETENCIES & CERTIFICATIONS
──────────────────────────────────────────────────────────────────────────────
• Clinical Skills: Acute & Chronic Patient Care, Triage Assessment, IV Therapy, Wound Care, Post-Op Monitoring
• Systems & EMR: Epic Systems, Cerner, Meditech, PointClickCare, Pyxis Automated Medication Dispensing
• Certifications & Licenses: Registered Nurse (RN State License #), BLS, ACLS, PALS, NIHSS Certified
• Quality & Compliance: HIPAA Compliance, Infection Control Protocols (CDC/JCAHO), Patient Safety Initiatives

──────────────────────────────────────────────────────────────────────────────
CLINICAL EXPERIENCE
──────────────────────────────────────────────────────────────────────────────
[Clinical Title, e.g., Staff Nurse - Intensive Care Unit] | [Hospital / Medical Center] — [City, State]
[Start Month, Year] – Present
• Delivered direct, high-acuity care to [Number] critically ill patients daily, executing physician orders and monitoring hemodynamic stability.
• Reduced ventilator-associated pneumonia (VAP) and catheter-related infections by 32% by championing evidence-based hygiene bundles.
• Managed rapid response interventions and emergency code scenarios, administering vasoactive infusions and emergency medications with 100% protocol adherence.
• Supervised and precepted [Number] new graduate nurses and nursing students on unit orientation and electronic charting.

[Clinical Title, e.g., Medical-Surgical Staff Nurse] | [Previous Hospital / Clinic] — [City, State]
[Start Month, Year] – [End Month, Year]
• Provided comprehensive pre- and post-operative nursing care for 5-7 adult surgical patients per shift in a fast-paced 36-bed unit.
• Facilitated smooth patient admissions, multidisciplinary discharge planning, and patient/family education, reducing 30-day readmissions by 14%.
• Collaborated closely with attending physicians, pharmacists, physical therapists, and case managers to optimize care continuity.

──────────────────────────────────────────────────────────────────────────────
EDUCATION & PROFESSIONAL CREDENTIALS
──────────────────────────────────────────────────────────────────────────────
Bachelor of Science in Nursing (BSN)
[University / College of Nursing] — [Graduation Year]
• Active State Board of Nursing License (RN # [License Number], Expiration: [MM/YYYY])
• Basic Life Support (BLS) & Advanced Cardiovascular Life Support (ACLS) — American Heart Association
"""

business_text = """[YOUR FULL NAME]
[City, State / Region] | [Phone Number] | [Professional Email Address]
[LinkedIn Profile URL] | [Personal Portfolio / Case Studies Website]

──────────────────────────────────────────────────────────────────────────────
PROFESSIONAL SUMMARY
──────────────────────────────────────────────────────────────────────────────
Results-driven Business & Finance Professional with [Number]+ years of experience leading strategic operations, financial planning & analysis (FP&A), and business development. Proven record of managing $[Amount]M+ operating budgets, improving operating margins by [X]%, and delivering data-driven forecasts that steer executive decisions. Skilled in financial modeling, ERP implementation, cross-functional stakeholder leadership, and market expansion.

──────────────────────────────────────────────────────────────────────────────
CORE COMPETENCIES & TOOLS
──────────────────────────────────────────────────────────────────────────────
• Financial & Strategic: FP&A, Budget Forecasting, P&L Management, Cost Optimization, Valuation, ROI Modeling
• Enterprise Systems: SAP, NetSuite, Oracle ERP, Salesforce CRM, QuickBooks Enterprise, Workday
• Analytics & BI: Advanced Excel (VBA, Power Query), Microsoft Power BI, Tableau, SQL basics
• Operations & Governance: SOX Compliance, GAAP/IFRS Standards, Internal Audit, Contract Negotiation

──────────────────────────────────────────────────────────────────────────────
PROFESSIONAL EXPERIENCE
──────────────────────────────────────────────────────────────────────────────
Senior Financial Analyst / Operations Manager | [Company Name] — [City, State]
[Start Month, Year] – Present
• Spearheaded annual operating budget of $24M across 4 business units, reducing forecast variance from 8.5% to under 2.1%.
• Built dynamic multi-year scenario models for executive leadership, identifying $1.8M in redundant vendor expenses and renegotiating contracts.
• Designed automated executive KPI dashboards in Power BI, cutting monthly financial close reporting time by 4 business days.
• Led cross-departmental working group to evaluate M&A target, preparing comprehensive discounted cash flow (DCF) valuation models.

Financial Analyst / Business Operations Associate | [Previous Company] — [City, State]
[Start Month, Year] – [End Month, Year]
• Managed variance analysis and cost accounting for 12 operational cost centers, presenting monthly commentary to department directors.
• Automated weekly revenue tracking spreadsheets with SQL queries and Excel macros, saving 15 hours of manual data entry weekly.
• Partnered with Sales Operations to revamp pricing tier structure, boosting average contract value (ACV) by 18%.

──────────────────────────────────────────────────────────────────────────────
EDUCATION & CERTIFICATIONS
──────────────────────────────────────────────────────────────────────────────
Bachelor of Business Administration (BBA) in Finance / Accounting
[University / Business School Name] — [Graduation Year]
• Chartered Financial Analyst (CFA) Level II Candidate / Certified Public Accountant (CPA)
• Financial Modeling & Valuation Analyst (FMVA)® — Corporate Finance Institute
"""

import sys
sys.path.insert(0, ".")
import core.career_resources as cr
import pprint

templates = {
    'universal': {
        'id': 'universal',
        'title': 'Universal All-Career ATS Blueprint',
        'badge': 'Universal • Any Career Field',
        'description': 'Field-agnostic ATS blueprint engineered for any profession (Healthcare, Business, Education, Engineering, Tech, Public Service, Hospitality). Follows single-column machine parsing standard with customizable placeholders.',
        'filename_prefix': 'WorkWise_2026_ATS_Universal_Any_Career_Blueprint',
        'target_roles': ['Any Professional Field', 'Career Changers', 'Recent Graduates', 'Managers & Specialists', 'Public & Private Sector'],
        'text_content': universal_text,
    },
    'tech': cr.RESUME_TEMPLATES['tech'],
    'healthcare': {
        'id': 'healthcare',
        'title': 'Healthcare & Nursing Clinical Blueprint',
        'badge': 'Healthcare & Medical',
        'description': 'ATS-optimized resume template tailored for Registered Nurses (RN), Nurse Practitioners, Medical Technologists, and Clinical Specialists.',
        'filename_prefix': 'WorkWise_2026_ATS_Healthcare_Nursing_Template',
        'target_roles': ['Registered Nurse (RN)', 'Clinical Nurse Specialist', 'Nurse Practitioner', 'Medical Laboratory Technologist', 'Physical Therapist'],
        'text_content': healthcare_text,
    },
    'business': {
        'id': 'business',
        'title': 'Business, Finance & Operations Blueprint',
        'badge': 'Business & Finance',
        'description': 'ATS-optimized resume template engineered for Finance Analysts, Operations Managers, Accountants, and Business Consultants.',
        'filename_prefix': 'WorkWise_2026_ATS_Business_Finance_Template',
        'target_roles': ['Financial Analyst', 'Operations Manager', 'Accountant / CPA', 'Management Consultant', 'Business Development Lead'],
        'text_content': business_text,
    },
    'design': cr.RESUME_TEMPLATES['design'],
    'manager': cr.RESUME_TEMPLATES['manager'],
}

with open("core/career_resources.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace RESUME_TEMPLATES definition
match = re.search(r"RESUME_TEMPLATES\s*=\s*\{.*?\}\}\n\nINTERVIEW_CATEGORIES", content, re.DOTALL)
if match:
    tpl_code = "RESUME_TEMPLATES = " + pprint.pformat(templates, width=120) + "\n\nINTERVIEW_CATEGORIES"
    new_content = content[:match.start()] + tpl_code + content[match.end() - len("\n\nINTERVIEW_CATEGORIES"):]
    with open("core/career_resources.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Updated core/career_resources.py successfully!")
else:
    print("Could not match RESUME_TEMPLATES pattern.")
