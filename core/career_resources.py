"""core/career_resources.py — Real ATS Resume Templates & Interview Mastery Content."""
import io
import zipfile

RESUME_TEMPLATES = {'business': {'badge': 'Business & Finance',
              'description': 'ATS-optimized resume template engineered for Finance Analysts, Operations Managers, '
                             'Accountants, and Business Consultants.',
              'filename_prefix': 'WorkWise_2026_ATS_Business_Finance_Template',
              'id': 'business',
              'target_roles': ['Financial Analyst',
                               'Operations Manager',
                               'Accountant / CPA',
                               'Management Consultant',
                               'Business Development Lead'],
              'text_content': '[YOUR FULL NAME]\n'
                              '[City, State / Region] | [Phone Number] | [Professional Email Address]\n'
                              '[LinkedIn Profile URL] | [Personal Portfolio / Case Studies Website]\n'
                              '\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              'PROFESSIONAL SUMMARY\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              'Results-driven Business & Finance Professional with [Number]+ years of experience '
                              'leading strategic operations, financial planning & analysis (FP&A), and business '
                              'development. Proven record of managing $[Amount]M+ operating budgets, improving '
                              'operating margins by [X]%, and delivering data-driven forecasts that steer executive '
                              'decisions. Skilled in financial modeling, ERP implementation, cross-functional '
                              'stakeholder leadership, and market expansion.\n'
                              '\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              'CORE COMPETENCIES & TOOLS\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              '• Financial & Strategic: FP&A, Budget Forecasting, P&L Management, Cost Optimization, '
                              'Valuation, ROI Modeling\n'
                              '• Enterprise Systems: SAP, NetSuite, Oracle ERP, Salesforce CRM, QuickBooks Enterprise, '
                              'Workday\n'
                              '• Analytics & BI: Advanced Excel (VBA, Power Query), Microsoft Power BI, Tableau, SQL '
                              'basics\n'
                              '• Operations & Governance: SOX Compliance, GAAP/IFRS Standards, Internal Audit, '
                              'Contract Negotiation\n'
                              '\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              'PROFESSIONAL EXPERIENCE\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              'Senior Financial Analyst / Operations Manager | [Company Name] — [City, State]\n'
                              '[Start Month, Year] – Present\n'
                              '• Spearheaded annual operating budget of $24M across 4 business units, reducing '
                              'forecast variance from 8.5% to under 2.1%.\n'
                              '• Built dynamic multi-year scenario models for executive leadership, identifying $1.8M '
                              'in redundant vendor expenses and renegotiating contracts.\n'
                              '• Designed automated executive KPI dashboards in Power BI, cutting monthly financial '
                              'close reporting time by 4 business days.\n'
                              '• Led cross-departmental working group to evaluate M&A target, preparing comprehensive '
                              'discounted cash flow (DCF) valuation models.\n'
                              '\n'
                              'Financial Analyst / Business Operations Associate | [Previous Company] — [City, State]\n'
                              '[Start Month, Year] – [End Month, Year]\n'
                              '• Managed variance analysis and cost accounting for 12 operational cost centers, '
                              'presenting monthly commentary to department directors.\n'
                              '• Automated weekly revenue tracking spreadsheets with SQL queries and Excel macros, '
                              'saving 15 hours of manual data entry weekly.\n'
                              '• Partnered with Sales Operations to revamp pricing tier structure, boosting average '
                              'contract value (ACV) by 18%.\n'
                              '\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              'EDUCATION & CERTIFICATIONS\n'
                              '──────────────────────────────────────────────────────────────────────────────\n'
                              'Bachelor of Business Administration (BBA) in Finance / Accounting\n'
                              '[University / Business School Name] — [Graduation Year]\n'
                              '• Chartered Financial Analyst (CFA) Level II Candidate / Certified Public Accountant '
                              '(CPA)\n'
                              '• Financial Modeling & Valuation Analyst (FMVA)® — Corporate Finance Institute\n',
              'title': 'Business, Finance & Operations Blueprint'},
 'design': {'badge': 'Design & Product',
            'description': 'ATS-optimized resume template tailored for UI/UX, Product Designers, and UX Researchers.',
            'filename_prefix': 'WorkWise_2026_ATS_Product_Designer_Template',
            'id': 'design',
            'target_roles': ['Product Designer', 'Senior UI/UX Designer', 'Design Systems Lead', 'UX Researcher'],
            'text_content': 'MAYA SANTOS\n'
                            'New York, NY | (555) 876-5432 | maya.santos.design@email.com\n'
                            'portfolio.mayasantos.design | linkedin.com/in/mayasantos-ux | figma.com/@mayaux\n'
                            '\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'PROFESSIONAL SUMMARY\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'Strategic Senior Product Designer with 5+ years of experience leading end-to-end design '
                            'for\n'
                            'high-growth B2B and consumer web platforms. Specialized in design systems, '
                            'conversion-driven\n'
                            'interfaces, user research, and interactive prototyping. Increased checkout completion by '
                            '23%\n'
                            'and decreased task completion time by 35% through iterative usability testing and design '
                            'thinking.\n'
                            '\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'CORE COMPETENCIES & TOOLS\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            '• Design Disciplines: Product Design, UI/UX, User Research, Wireframing, Rapid '
                            'Prototyping, Design Systems\n'
                            '• Methodologies: Usability Testing, Information Architecture, Heuristic Evaluation, User '
                            'Journey Mapping\n'
                            '• Design Software: Figma, FigJam, Adobe Creative Cloud (Illustrator, Photoshop), '
                            'Principle, Miro\n'
                            '• Technical Literacy: HTML5, CSS3, Flexbox/Grid, Design Tokens, Git basics, WCAG 2.1 AA '
                            'Accessibility\n'
                            '\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'PROFESSIONAL EXPERIENCE\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'Senior Product Designer | Apex Creative Co. — New York, NY\n'
                            'January 2023 – Present\n'
                            '• Spearheaded the complete redesign of the core SaaS analytics platform, driving a 27% '
                            'increase in\n'
                            '  user engagement and reducing churn by 3.8% over 12 months.\n'
                            '• Built and documented the company-wide multi-brand Design System in Figma with 180+ '
                            'accessible components\n'
                            '  and design tokens, cutting front-end design handoff time by 40%.\n'
                            '• Conducted 45+ moderated user interviews and prototype usability tests to validate '
                            'product assumptions\n'
                            '  prior to engineering sprint kick-offs.\n'
                            '• Collaborated daily with engineering leads and product managers to ensure 100% WCAG 2.1 '
                            'AA compliance\n'
                            '  and pixel-perfect implementation.\n'
                            '\n'
                            'UI/UX Designer | NovaTech Solutions — Boston, MA\n'
                            'August 2020 – December 2022\n'
                            '• Designed end-to-end mobile and web onboarding experiences for 200,000+ active '
                            'enterprise professionals.\n'
                            '• Redesigned subscription billing and account management flows, elevating funnel '
                            'conversion by 19%.\n'
                            '• Created interactive high-fidelity prototypes for stakeholder presentations, securing '
                            '$1.5M in seed funding.\n'
                            '• Mentored 2 junior designers in typography, auto-layout architecture, and UX research '
                            'synthesis.\n'
                            '\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'SELECTED CASE STUDIES\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'FinTech Global Mobile Checkout Redesign\n'
                            '• Solved multi-currency transaction friction, leading to a 31% increase in international '
                            'payment completion.\n'
                            'Enterprise Design System (OmniUI)\n'
                            '• Open-source Figma library featuring dark/light modes, accessible color contrasts, and '
                            'auto-layout components.\n'
                            '\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'EDUCATION & CREDENTIALS\n'
                            '──────────────────────────────────────────────────────────────────────────────\n'
                            'Bachelor of Fine Arts in Interaction Design | Rhode Island School of Design (RISD)\n'
                            '• Nielsen Norman Group (NN/g) UX Master Certified\n'
                            '• Interaction Design Foundation (IDF) Accessibility Specialist\n',
            'title': 'UI/UX & Product Designer'},
 'healthcare': {'badge': 'Healthcare & Medical',
                'description': 'ATS-optimized resume template tailored for Registered Nurses (RN), Nurse '
                               'Practitioners, Medical Technologists, and Clinical Specialists.',
                'filename_prefix': 'WorkWise_2026_ATS_Healthcare_Nursing_Template',
                'id': 'healthcare',
                'target_roles': ['Registered Nurse (RN)',
                                 'Clinical Nurse Specialist',
                                 'Nurse Practitioner',
                                 'Medical Laboratory Technologist',
                                 'Physical Therapist'],
                'text_content': '[FULL NAME], RN, BSN / MD\n'
                                '[City, State / Region] | [Phone Number] | [Professional Email Address]\n'
                                '[LinkedIn Profile URL] | [State Board License # / Registry ID]\n'
                                '\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                'PROFESSIONAL SUMMARY\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                'Compassionate, board-certified [Nursing / Healthcare Professional Title] with '
                                '[Number]+ years of clinical experience in [Specialty: e.g., Critical Care, Emergency, '
                                'Telemetry, Pediatrics, Outpatient]. Demonstrated expertise in patient assessment, '
                                'medication administration, life support protocols, and multidisciplinary care '
                                'planning. Proven record of maintaining 98%+ patient satisfaction scores and '
                                'zero-incident medication error compliance. Dedicated to evidence-based practice and '
                                'compassionate patient advocacy.\n'
                                '\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                'CLINICAL COMPETENCIES & CERTIFICATIONS\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                '• Clinical Skills: Acute & Chronic Patient Care, Triage Assessment, IV Therapy, Wound '
                                'Care, Post-Op Monitoring\n'
                                '• Systems & EMR: Epic Systems, Cerner, Meditech, PointClickCare, Pyxis Automated '
                                'Medication Dispensing\n'
                                '• Certifications & Licenses: Registered Nurse (RN State License #), BLS, ACLS, PALS, '
                                'NIHSS Certified\n'
                                '• Quality & Compliance: HIPAA Compliance, Infection Control Protocols (CDC/JCAHO), '
                                'Patient Safety Initiatives\n'
                                '\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                'CLINICAL EXPERIENCE\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                '[Clinical Title, e.g., Staff Nurse - Intensive Care Unit] | [Hospital / Medical '
                                'Center] — [City, State]\n'
                                '[Start Month, Year] – Present\n'
                                '• Delivered direct, high-acuity care to [Number] critically ill patients daily, '
                                'executing physician orders and monitoring hemodynamic stability.\n'
                                '• Reduced ventilator-associated pneumonia (VAP) and catheter-related infections by '
                                '32% by championing evidence-based hygiene bundles.\n'
                                '• Managed rapid response interventions and emergency code scenarios, administering '
                                'vasoactive infusions and emergency medications with 100% protocol adherence.\n'
                                '• Supervised and precepted [Number] new graduate nurses and nursing students on unit '
                                'orientation and electronic charting.\n'
                                '\n'
                                '[Clinical Title, e.g., Medical-Surgical Staff Nurse] | [Previous Hospital / Clinic] — '
                                '[City, State]\n'
                                '[Start Month, Year] – [End Month, Year]\n'
                                '• Provided comprehensive pre- and post-operative nursing care for 5-7 adult surgical '
                                'patients per shift in a fast-paced 36-bed unit.\n'
                                '• Facilitated smooth patient admissions, multidisciplinary discharge planning, and '
                                'patient/family education, reducing 30-day readmissions by 14%.\n'
                                '• Collaborated closely with attending physicians, pharmacists, physical therapists, '
                                'and case managers to optimize care continuity.\n'
                                '\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                'EDUCATION & PROFESSIONAL CREDENTIALS\n'
                                '──────────────────────────────────────────────────────────────────────────────\n'
                                'Bachelor of Science in Nursing (BSN)\n'
                                '[University / College of Nursing] — [Graduation Year]\n'
                                '• Active State Board of Nursing License (RN # [License Number], Expiration: '
                                '[MM/YYYY])\n'
                                '• Basic Life Support (BLS) & Advanced Cardiovascular Life Support (ACLS) — American '
                                'Heart Association\n',
                'title': 'Healthcare & Nursing Clinical Blueprint'},
 'manager': {'badge': 'Leadership & Strategy',
             'description': 'ATS-tailored template highlighting people leadership, technical vision, and strategic '
                            'delivery.',
             'filename_prefix': 'WorkWise_2026_ATS_Engineering_Manager_Template',
             'id': 'manager',
             'target_roles': ['Engineering Manager', 'Technical Lead', 'Director of Engineering', 'VP of Technology'],
             'text_content': 'ELENA VARGAS\n'
                             'Seattle, WA | (555) 432-1098 | elena.vargas.tech@email.com\n'
                             'linkedin.com/in/elena-vargas-leader | github.com/evargas-exec\n'
                             '\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             'EXECUTIVE SUMMARY\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             'Engineering Leader with 9+ years in software engineering and 4+ years managing '
                             'high-performing,\n'
                             'distributed teams across North America and Europe. Track record of scaling engineering '
                             'headcount from\n'
                             '8 to 30+, maintaining 96% talent retention, and driving enterprise product deliveries '
                             'generating $18M+\n'
                             'ARR. Passionate about psychological safety, operational excellence, and clear technical '
                             'roadmaps.\n'
                             '\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             'LEADERSHIP & EXECUTIVE COMPETENCIES\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             '• People & Culture: Team Scaling & Hiring, 1-on-1 Mentorship, Performance Reviews, '
                             'Retention & DEI\n'
                             '• Engineering Operations: Agile/Scrum, OKR Alignment, CI/CD Automation, Incident '
                             'Management & Post-Mortems\n'
                             '• Technical Strategy: Distributed Architecture, Microservices, Cloud Modernization, Tech '
                             'Debt Reduction\n'
                             '• Business Alignment: Executive Stakeholder Management, Vendor Evaluation, Budget '
                             'Planning ($4M+ P&L)\n'
                             '\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             'PROFESSIONAL EXPERIENCE\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             'Engineering Manager | BrightWave Technologies — Seattle, WA\n'
                             'February 2022 – Present\n'
                             '• Scale and lead an engineering department of 24 engineers and 3 tech leads across '
                             'Infrastructure,\n'
                             '  Core Platform, and Mobile squads.\n'
                             '• Reduced sprint rollover rate by 34% through rigorous capacity planning, '
                             'retrospectives, and WIP limits.\n'
                             '• Partnered with VP of Product to establish annual technical roadmaps and OKRs, aligning '
                             'engineering\n'
                             '  deliverables with $22M enterprise company revenue targets.\n'
                             '• Instituted blameless post-mortem culture and automated SLA monitoring, cutting mean '
                             'time to recovery\n'
                             '  (MTTR) from 4.2 hours to 28 minutes.\n'
                             '• Achieved a 96% retention rate over a 24-month span by creating transparent engineering '
                             'career progression ladders.\n'
                             '\n'
                             'Technical Lead / Staff Engineer | CloudFrontier Systems — Denver, CO\n'
                             'June 2018 – January 2022\n'
                             '• Led architectural modernization from a legacy monolithic codebase to microservices '
                             'running on AWS EKS,\n'
                             '  improving service uptime to 99.99%.\n'
                             '• Managed a squad of 7 senior engineers while actively reviewing code, unblocking '
                             'technical deadlocks,\n'
                             '  and establishing code review guidelines.\n'
                             '• Directed technical vendor negotiations and AWS reserved instance commitments, saving '
                             '$120,000 annually.\n'
                             '\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             'EDUCATION & LEADERSHIP CERTIFICATIONS\n'
                             '──────────────────────────────────────────────────────────────────────────────\n'
                             'Master of Science in Software Engineering | University of Washington\n'
                             'Bachelor of Science in Information Systems | University of Colorado Boulder\n'
                             '• Certified ScrumMaster (CSM) | Scrum Alliance\n'
                             '• Executive Leadership Program | Stanford Graduate School of Business (Online)\n',
             'title': 'Engineering Manager & Tech Lead'},
 'tech': {'badge': 'Engineering & Tech',
          'description': 'ATS-scanned template optimized for Backend, Frontend, DevOps, and Full-Stack Developers.',
          'filename_prefix': 'WorkWise_2026_ATS_Software_Engineer_Template',
          'id': 'tech',
          'target_roles': ['Full Stack Engineer',
                           'Backend Developer',
                           'DevOps / Cloud Engineer',
                           'Frontend Specialist'],
          'text_content': 'ALEX RIVERA\n'
                          'San Francisco, CA | (555) 234-5678 | alex.rivera@email.com\n'
                          'linkedin.com/in/alex-rivera-dev | github.com/alexrivera-tech | portfolio.workwise.dev/alex\n'
                          '\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'PROFESSIONAL SUMMARY\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'Results-driven Senior Full-Stack Software Engineer with 6+ years of experience designing,\n'
                          'building, and scaling distributed cloud applications. Proven track record of improving\n'
                          'system throughput by 40%, reducing infrastructure costs by 28%, and delivering '
                          'mission-critical\n'
                          'microservices with 99.99% uptime. Expert in Python, Django, TypeScript, React, Docker, and '
                          'AWS.\n'
                          '\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'TECHNICAL SKILLS\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          '• Languages: Python, TypeScript, JavaScript, SQL, Go, HTML5/CSS3\n'
                          '• Frameworks & Libraries: Django, FastAPI, React, Next.js, Node.js, TailwindCSS\n'
                          '• Databases & Caching: PostgreSQL, Redis, MySQL, MongoDB, Elasticsearch\n'
                          '• Cloud & DevOps: AWS (EC2, S3, RDS, Lambda, ECS), Docker, Kubernetes, CI/CD (GitHub '
                          'Actions, Terraform)\n'
                          '• Architecture & Practices: RESTful APIs, GraphQL, Microservices, Event-Driven '
                          'Architecture, TDD, Agile/Scrum\n'
                          '\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'PROFESSIONAL EXPERIENCE\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'Senior Software Engineer | Synapse Labs — San Francisco, CA\n'
                          'March 2023 – Present\n'
                          '• Architected and deployed an event-driven data ingestion pipeline using Python, Kafka, and '
                          'PostgreSQL,\n'
                          '  processing 12M+ records daily with sub-200ms latency.\n'
                          '• Optimized PostgreSQL query performance and caching layers with Redis, resulting in a 42% '
                          'reduction\n'
                          '  in p99 API response times and $14,000 annual cloud hosting savings.\n'
                          '• Led a cross-functional team of 6 engineers across 8 two-week sprint cycles, achieving a '
                          '95% on-time\n'
                          '  feature delivery rate for the enterprise B2B SaaS dashboard.\n'
                          '• Authored comprehensive unit and integration test suites achieving 88% test coverage with '
                          'automated\n'
                          '  GitHub Actions CI/CD pipelines.\n'
                          '\n'
                          'Full Stack Developer | Orbit Systems — Austin, TX\n'
                          'July 2020 – February 2023\n'
                          '• Developed customer-facing web applications using React, TypeScript, and Django REST '
                          'Framework,\n'
                          '  serving over 450,000 monthly active users.\n'
                          '• Migrated monolithic billing engine to microservices with Stripe API integration, '
                          'processing $3.2M\n'
                          '  in annual recurring subscriptions with zero payment loss incidents.\n'
                          '• Built role-based access control (RBAC) and OAuth2/JWT authentication protocols adhering '
                          'to SOC2\n'
                          '  and GDPR compliance standards.\n'
                          '• Collaborated closely with Product and UI/UX designers to reduce user onboarding drop-off '
                          'by 18%.\n'
                          '\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'SELECTED PROJECTS\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'CloudScale Distributed Task Worker | Open Source\n'
                          '• Engineered a distributed task queue in Go and Redis with automatic retries and '
                          'exponential backoff,\n'
                          '  securing 1,200+ GitHub stars.\n'
                          '\n'
                          'Real-Time Candidate Pipeline Tracker | Personal Project\n'
                          '• Built a full-stack recruiting kanban dashboard with Django Channels and WebSockets '
                          'supporting live\n'
                          '  drag-and-drop state transitions.\n'
                          '\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'EDUCATION & CERTIFICATIONS\n'
                          '──────────────────────────────────────────────────────────────────────────────\n'
                          'Bachelor of Science in Computer Science | University of California, Berkeley (2020)\n'
                          '• AWS Certified Solutions Architect – Associate (Active)\n'
                          '• Certified Kubernetes Administrator (CKA, Active)\n',
          'title': 'Software Engineer & Cloud Architect'},
 'universal': {'badge': 'Universal • Any Career Field',
               'description': 'Field-agnostic ATS blueprint engineered for any profession (Healthcare, Business, '
                              'Education, Engineering, Tech, Public Service, Hospitality). Follows single-column '
                              'machine parsing standard with customizable placeholders.',
               'filename_prefix': 'WorkWise_2026_ATS_Universal_Any_Career_Blueprint',
               'id': 'universal',
               'target_roles': ['Any Professional Field',
                                'Career Changers',
                                'Recent Graduates',
                                'Managers & Specialists',
                                'Public & Private Sector'],
               'text_content': '[YOUR FULL NAME]\n'
                               '[City, State / Region] | [Phone Number] | [Professional Email Address]\n'
                               '[LinkedIn Profile URL] | [Portfolio, Personal Website, or Work Samples URL]\n'
                               '\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               'PROFESSIONAL SUMMARY\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               '[Job Title / Target Professional Role] with [Number]+ years of demonstrated experience '
                               'in [Industry / Field of Specialization]. Proven track record of improving operational '
                               'efficiency by [X]%, managing [Key Function / Account / Team Size], and delivering '
                               'high-impact results under tight deadlines. Skilled in [Core Skill 1], [Core Skill 2], '
                               'and cross-functional team collaboration. Adept at applying data-driven strategies and '
                               'industry best practices to achieve organizational goals.\n'
                               '\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               'CORE COMPETENCIES & PROFESSIONAL SKILLS\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               '• Domain Expertise: [Core Skill 1], [Core Skill 2], [Core Skill 3], [Core Skill 4]\n'
                               '• Tools & Systems: [Software / Tool 1], [Platform / ERP / CRM 2], [Technical Tool 3]\n'
                               '• Operations & Methodologies: [Process / Standard 1], [Compliance / Framework 2]\n'
                               '• Interpersonal & Leadership: Stakeholder Management, Team Leadership, Problem '
                               'Resolution\n'
                               '\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               'PROFESSIONAL EXPERIENCE\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               '[Job Title / Position] | [Company / Organization Name] — [City, State / Country]\n'
                               '[Start Month, Year] – Present\n'
                               '• Spearheaded [Initiative / Major Project], increasing [Key Metric: Revenue / Output / '
                               'Patient Care / Productivity] by [X]% over [Timeframe].\n'
                               '• Implemented [Methodology / Process / Tool], reducing [Cost / Operational Downtime / '
                               'Processing Time] by [Y]% ($[Amount Saved] annually).\n'
                               '• Led and mentored a cross-functional team of [Number] staff members, achieving a [Z]% '
                               'on-time delivery rate across [Number] key milestones.\n'
                               '• Standardized operating documentation and quality assurance protocols, reducing error '
                               'rates from [Old Number]% to [New Number]%.\n'
                               '\n'
                               '[Previous Job Title] | [Previous Company / Organization Name] — [City, State / '
                               'Country]\n'
                               '[Start Month, Year] – [End Month, Year]\n'
                               '• Coordinated day-to-day operations for [Department / Function], supporting [Client '
                               'Count / Project Portfolio / Operations] valued at $[Value].\n'
                               '• Analyzed operational bottlenecks in [Specific Area] and designed an automated / '
                               'revised workflow, cutting turnaround time by [X]%.\n'
                               '• Authored comprehensive reports and delivered strategic presentations to executive '
                               'leadership, informing critical resource allocation.\n'
                               '• Commended by leadership / clients for [Specific Notable Accomplishment or Award '
                               'Name].\n'
                               '\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               'KEY PROJECTS & MAJOR ACCOMPLISHMENTS\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               '[Project Title or Key Strategic Initiative] | [Organization or Independent]\n'
                               '• Planned and delivered [Project Scope / Objective], resulting in [Concrete '
                               'Quantifiable Outcome / Adoption / Recognition].\n'
                               '• Managed [Resource / Budget / Cross-functional team], completing deliverable [X] '
                               'weeks ahead of target schedule.\n'
                               '\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               'EDUCATION & PROFESSIONAL CREDENTIALS\n'
                               '──────────────────────────────────────────────────────────────────────────────\n'
                               '[Degree / Diploma / Certification] in [Field of Study / Discipline]\n'
                               '[University / College / Institution Name] — [Graduation Year]\n'
                               "• Academic Honors / Distinctions: [e.g., Magna Cum Laude, Dean's List, Top 5%] "
                               '(Optional)\n'
                               '• Professional License / Certification: [Official License Title, Issuing Authority, '
                               'Year]\n'
                               '• Continuing Professional Development: [Relevant Workshop, Seminar, or Specialized '
                               'Training]\n',
               'title': 'Universal All-Career ATS Blueprint'}}


INTERVIEW_CATEGORIES = [{'description': 'Master behavioral and situational questions using the '
                 'Situation, Task, Action, Result framework.',
  'icon': '',
  'id': 'behavioral',
  'name': 'Behavioral (STAR Method)',
  'questions': [{'assessor_lookout': 'Evaluates composure, systematic '
                                     'root-cause troubleshooting, clear '
                                     'stakeholder communication, and '
                                     'prevention mindset.',
                 'pro_tip': 'Never blame a teammate or vendor. Focus on '
                            'accountability, systemic improvements, and '
                            'quantitative business recovery metrics.',
                 'question': 'Tell me about a time you handled a high-stakes '
                             'production incident or critical bug under tight '
                             'deadlines.',
                 'star_breakdown': {'Action': 'I immediately triggered our '
                                              'incident protocol, instituted a '
                                              'rollback to the last verified '
                                              'stable release, and spun up '
                                              'hotfix worker pods. Using '
                                              'Datadog logs and PostgreSQL '
                                              'slow query traces, I isolated a '
                                              'dead-lock in our inventory '
                                              'table. I wrote an atomic query '
                                              'migration patch and verified it '
                                              'in staging before deploying.',
                                    'Result': 'Resolved the outage in 22 '
                                              'minutes, recovered $68,000 in '
                                              'queued orders without customer '
                                              'data loss, and implemented an '
                                              'automated database index check '
                                              'that prevented recurrence.',
                                    'Situation': 'During Black Friday peak '
                                                 'traffic at my previous '
                                                 'company, our payment '
                                                 'processing webhook failed, '
                                                 'blocking 15% of inbound '
                                                 'checkout transactions.',
                                    'Task': 'As the on-call engineer, I had to '
                                            'stop financial loss, diagnose the '
                                            'failure within our 30-minute SLA, '
                                            'and keep executive stakeholders '
                                            'updated.'},
                 'title': 'Resolving a Critical Production Outage Under '
                          'Pressure'},
                {'assessor_lookout': 'Tests emotional intelligence, '
                                     'data-driven negotiation, business focus '
                                     'over ego, and commitment once decisions '
                                     'are made.',
                 'pro_tip': 'Frame disagreements around customer impact, team '
                            'velocity, and system risk rather than personal '
                            'coding preferences.',
                 'question': 'Describe a situation where you had a major '
                             'disagreement with a team lead or product manager '
                             'regarding technical direction.',
                 'star_breakdown': {'Action': "Instead of saying 'no', I "
                                              'prepared a 1-page comparison '
                                              'matrix showing that embedding '
                                              'it in the monolith would risk '
                                              '99.9% uptime for core billing. '
                                              'I proposed using a managed '
                                              'pub/sub service '
                                              '(Stream/Firebase) for MVP '
                                              'validation, which satisfied '
                                              'both the timeline and system '
                                              'stability.',
                                    'Result': 'The product lead embraced the '
                                              'managed approach, launching 4 '
                                              'days ahead of schedule with '
                                              'zero operational overhead on '
                                              'our core backend '
                                              'infrastructure.',
                                    'Situation': 'A product lead requested '
                                                 'building a bespoke real-time '
                                                 'in-app chat using raw '
                                                 'WebSockets directly into our '
                                                 'core monolith to hit an '
                                                 'aggressive 3-week deadline.',
                                    'Task': 'I needed to voice serious '
                                            'architectural concerns regarding '
                                            'database connection pool '
                                            'exhaustion without being '
                                            'perceived as an impediment to '
                                            'product velocity.'},
                 'title': 'Constructive Disagreement on Technical '
                          'Architecture'},
                {'assessor_lookout': 'Checks humility, early risk '
                                     'communication, post-mortem methodology, '
                                     'and resilience.',
                 'pro_tip': 'Choose a real failure with genuine stakes, and '
                            'emphasize the systemic lesson that permanently '
                            'altered your engineering habits.',
                 'question': "Tell me about a project that didn't go as "
                             'planned or missed an important deadline, and '
                             'what you learned.',
                 'star_breakdown': {'Action': 'I immediately raised the '
                                              'blocker to our engineering '
                                              'director and product '
                                              'counterpart with 3 mitigation '
                                              'options rather than waiting '
                                              'until deadline day. We staged '
                                              'the release into Phase 1 (core '
                                              'metrics) and Phase 2 '
                                              '(historical exports), keeping '
                                              'the main customer promise '
                                              'intact while I restructured '
                                              'data partitioning.',
                                    'Result': 'Phase 1 launched on time, and '
                                              'Phase 2 followed 10 days later '
                                              'with 3x query speeds. The team '
                                              'adopted early load-testing '
                                              'benchmarks into our definition '
                                              'of done.',
                                    'Situation': 'We committed to delivering a '
                                                 'multi-tenant client '
                                                 'reporting dashboard by the '
                                                 'end of Q2. Two weeks before '
                                                 'launch, we discovered severe '
                                                 'query degradation with large '
                                                 'datasets.',
                                    'Task': 'I was responsible for the data '
                                            'aggregation backend and had to '
                                            'address the timeline gap '
                                            'transparently.'},
                 'title': 'Overcoming Project Failure or Missed Deadlines'}]},
 {'description': 'Architect scalable, fault-tolerant, and high-performance '
                 'cloud applications.',
  'icon': '',
  'id': 'system_design',
  'name': 'System Design & Architecture',
  'questions': [{'assessor_lookout': 'Assesses asynchronous message queues '
                                     '(Kafka, SQS), worker scaling, '
                                     'idempotency, failure retries, and '
                                     'multi-tenant rate limits.',
                 'pro_tip': 'Always clarify scale requirements first: read vs. '
                            'write ratios, acceptable delivery latency, and '
                            'idempotency guarantees.',
                 'question': 'How would you design a distributed notification '
                             'engine that sends push, email, and SMS '
                             'notifications at 10M messages per minute with '
                             'rate limiting?',
                 'star_breakdown': {'Architecture Blueprint': '1. API Gateway '
                                                              '/ Ingestion: '
                                                              'Lightweight '
                                                              'Go/FastAPI '
                                                              'endpoints '
                                                              'validating '
                                                              'payloads and '
                                                              'writing '
                                                              'immediately to '
                                                              'Apache Kafka '
                                                              'partitioned by '
                                                              'user ID.\n'
                                                              '2. Rate '
                                                              'Limiting & User '
                                                              'Preferences: '
                                                              'Redis token '
                                                              'bucket '
                                                              'algorithm '
                                                              'checking user '
                                                              'opt-outs and '
                                                              'channel quiet '
                                                              'hours.\n'
                                                              '3. Fan-out '
                                                              'Worker Pools: '
                                                              'Autoscaling '
                                                              'Celery/Go '
                                                              'workers pulling '
                                                              'from priority '
                                                              'topics (e.g. '
                                                              'Critical 2FA > '
                                                              'Marketing).\n'
                                                              '4. Vendor '
                                                              'Abstraction '
                                                              'Layer: '
                                                              'Multi-provider '
                                                              'failover '
                                                              '(Twilio, '
                                                              'SendGrid, APNS) '
                                                              'with circuit '
                                                              'breakers.\n'
                                                              '5. Idempotency '
                                                              '& '
                                                              'Deduplication: '
                                                              'SHA-256 hash of '
                                                              'payload stored '
                                                              'in Redis with '
                                                              '24-hour TTL.',
                                    'Key Trade-offs': 'Eventual consistency '
                                                      'over immediate '
                                                      'consistency; '
                                                      'prioritized queueing '
                                                      'ensures transactional '
                                                      'alerts are never '
                                                      'blocked by bulk '
                                                      'marketing campaigns.'},
                 'title': 'Designing a High-Throughput Notification Service '
                          '(10M/min)'},
                {'assessor_lookout': 'Evaluates command of EXPLAIN ANALYZE, '
                                     'indexing strategies, connection pooling, '
                                     'and locking behavior.',
                 'pro_tip': 'Mention caution when adding indexes in '
                            'production—remember that indexes speed up reads '
                            'but add write overhead on INSERT/UPDATE.',
                 'question': 'A production endpoint is timing out during peak '
                             'hours. How do you systematically identify and '
                             'fix the database bottleneck?',
                 'star_breakdown': {'Result Outcome': 'Transformed an '
                                                      '8.4-second full table '
                                                      'scan into an '
                                                      '18-millisecond index '
                                                      'seek, dropping database '
                                                      'CPU from 92% to 24%.',
                                    'Troubleshooting Protocol': '1. Telemetry: '
                                                                'Check APM '
                                                                'traces to '
                                                                'confirm '
                                                                'database '
                                                                'execution '
                                                                'time vs. '
                                                                'application '
                                                                'serialization '
                                                                'time.\n'
                                                                '2. Query '
                                                                'Analysis: Run '
                                                                'EXPLAIN '
                                                                '(ANALYZE, '
                                                                'BUFFERS) to '
                                                                'detect '
                                                                'sequential '
                                                                'table scans, '
                                                                'high shared '
                                                                'hit ratios, '
                                                                'and nested '
                                                                'loop joins on '
                                                                'unindexed '
                                                                'foreign '
                                                                'keys.\n'
                                                                '3. Index '
                                                                'Optimization: '
                                                                'Add '
                                                                'appropriate '
                                                                'composite or '
                                                                'partial '
                                                                'B-Tree '
                                                                'indexes '
                                                                'matching '
                                                                'filter & sort '
                                                                'clauses.\n'
                                                                '4. Connection '
                                                                'Health: '
                                                                'Inspect '
                                                                'pg_stat_activity '
                                                                'to check for '
                                                                'long-running '
                                                                'transactions '
                                                                'holding '
                                                                'row/table '
                                                                'locks.\n'
                                                                '5. '
                                                                'Architecture '
                                                                'Remediation: '
                                                                'Implement '
                                                                'Redis caching '
                                                                'for '
                                                                'read-heavy '
                                                                'static data '
                                                                'or route '
                                                                'reporting '
                                                                'queries to a '
                                                                'read '
                                                                'replica.'},
                 'title': 'Diagnosing and Resolving PostgreSQL Query '
                          'Bottlenecks'}]},
 {'description': 'Strategies for live coding, algorithms, clean code '
                 'principles, and whiteboard discussions.',
  'icon': '',
  'id': 'technical',
  'name': 'Live Technical & Problem Solving',
  'questions': [{'assessor_lookout': 'Assesses concurrency models: Optimistic '
                                     'Locking vs. Pessimistic Locking, atomic '
                                     'transactions, and distributed locks.',
                 'pro_tip': 'Explain the trade-offs: Pessimistic locking '
                            'guarantees safety but can bottleneck throughput; '
                            'optimistic locking scales reads but requires '
                            'retry logic.',
                 'question': 'How do you prevent double-spending or stock '
                             'overselling in concurrent e-commerce or booking '
                             'environments?',
                 'star_breakdown': {'Core Solution Patterns': '1. Database '
                                                              'Level '
                                                              '(Pessimistic): '
                                                              'SELECT ... FOR '
                                                              'UPDATE within '
                                                              'an explicit '
                                                              'database '
                                                              'transaction to '
                                                              'lock the exact '
                                                              'inventory row.\n'
                                                              '2. Optimistic '
                                                              'Locking: Use a '
                                                              'version column '
                                                              '(UPDATE item '
                                                              'SET stock = '
                                                              'stock - 1, '
                                                              'version = '
                                                              'version + 1 '
                                                              'WHERE id = ? '
                                                              'AND version = '
                                                              '?).\n'
                                                              '3. Atomic SQL '
                                                              'Expressions: '
                                                              'UPDATE items '
                                                              'SET stock = '
                                                              'stock - 1 WHERE '
                                                              'id = ? AND '
                                                              'stock >= 1; '
                                                              'check affected '
                                                              'rows.\n'
                                                              '4. Distributed '
                                                              'Locks: Use '
                                                              'Redis Redlock '
                                                              'for '
                                                              'cross-service '
                                                              'distributed '
                                                              'resource '
                                                              'synchronization.',
                                    'Recommended Strategy': 'For '
                                                            'high-concurrency '
                                                            'ticket/seat '
                                                            'reservation, '
                                                            'combine atomic '
                                                            'SQL updates with '
                                                            'a 10-minute Redis '
                                                            'reservation '
                                                            'lock.'},
                 'title': 'Handling Race Conditions in Financial & Inventory '
                          'Transactions'}]},
 {'description': 'Tactfully handle compensation discussions and ask '
                 'high-signal questions that impress executive interviewers.',
  'icon': '',
  'id': 'negotiation',
  'name': 'Salary Negotiation & Closing Questions',
  'questions': [{'assessor_lookout': 'Tests negotiation poise, market '
                                     'awareness, and ability to keep options '
                                     'open until the offer stage.',
                 'pro_tip': 'Never give a single fixed number; always provide '
                            'a data-backed range with a focus on total '
                            'compensation (base, bonus, equity, remote '
                            'stipend).',
                 'question': 'How do you respond when a recruiter asks for '
                             'your target number early in the interview '
                             'process?',
                 'star_breakdown': {'Model Response': "'I want to ensure the "
                                                      'compensation is aligned '
                                                      'with the market value '
                                                      'of the impact I will '
                                                      'deliver in this role. '
                                                      'Based on my research '
                                                      'for a Senior Engineer '
                                                      'in this market and the '
                                                      'tech stack, I '
                                                      'understand the range is '
                                                      'typically between '
                                                      '$130,000 and $160,000 '
                                                      'base, plus equity and '
                                                      'benefits. However, '
                                                      'finding the right '
                                                      'technical culture and '
                                                      'scope is my highest '
                                                      'priority. What is the '
                                                      'budgeted range for this '
                                                      "position?'",
                                    'Strategic Purpose': 'Anchors in market '
                                                         'data while turning '
                                                         'the question back to '
                                                         'the company to '
                                                         'reveal their '
                                                         'budgeted bracket.'},
                 'title': "Tactfully Answering: 'What are your salary "
                          "expectations?'"},
                {'assessor_lookout': 'Assesses intellectual curiosity, '
                                     'understanding of business priorities, '
                                     'and cultural alignment.',
                 'pro_tip': 'Avoid generic questions easily found on the '
                            'company website. Ask questions that reveal '
                            'day-to-day engineering culture and team autonomy.',
                 'question': 'What questions should you ask at the end of an '
                             'interview to stand out as a top candidate?',
                 'star_breakdown': {'Top 3 Questions': "1. 'What does success "
                                                       'look like for this '
                                                       'role in the first 90 '
                                                       'days, and what is the '
                                                       'biggest technical '
                                                       'blocker standing in '
                                                       "the way today?'\n"
                                                       "2. 'How does your "
                                                       'engineering team '
                                                       'manage the trade-off '
                                                       'between shipping new '
                                                       'product features and '
                                                       'addressing technical '
                                                       "debt?'\n"
                                                       "3. 'Can you walk me "
                                                       'through the most '
                                                       'recent incident or '
                                                       'failed release and how '
                                                       'the post-mortem was '
                                                       "conducted?'"},
                 'title': 'High-Signal Closing Questions to Ask the Hiring '
                          'Team'}]}]


def _escape_rtf(text: str) -> str:
    out = []
    for char in text:
        if char in r"\{}":
            out.append("\\" + char)
        elif ord(char) > 127:
            out.append(f"\\u{ord(char)}?")
        else:
            out.append(char)
    return "".join(out)


def _create_rtf_from_text(text: str) -> bytes:
    lines = text.split("\n")
    rtf_lines = [
        r"{\rtf1\ansi\deff0",
        r"{\fonttbl{\f0\fswiss\fcharset0 Arial;}{\f1\fmodern\fcharset0 Courier New;}}",
        r"{\colortbl ;\red15\green23\blue42;\red56\green189\blue248;\red100\green116\blue139;}",
        r"\margl1440\margr1440\margt1440\margb1440",
        r"\viewkind4\uc1\pard\f0\fs20",
    ]
    for line in lines:
        stripped = line.strip()
        if not stripped:
            rtf_lines.append(r"\par")
        elif stripped.isupper() and len(stripped) < 40 and not stripped.startswith("─"):
            rtf_lines.append(r"\par\b\fs26 " + _escape_rtf(stripped) + r"\b0\fs20\par")
        elif stripped.startswith("─"):
            rtf_lines.append(r"{\cf3 ──────────────────────────────────────────────────────────────}\par")
        elif " | " in stripped and not stripped.startswith("•"):
            rtf_lines.append(r"\b " + _escape_rtf(stripped) + r"\b0\par")
        elif stripped.startswith("•"):
            rtf_lines.append(r"\bullet  " + _escape_rtf(stripped[1:].strip()) + r"\par")
        else:
            rtf_lines.append(_escape_rtf(stripped) + r"\par")
    rtf_lines.append("}")
    return "\n".join(rtf_lines).encode("utf-8")


def get_resume_download(template_id: str = "tech", file_format: str = "doc") -> tuple[bytes, str, str]:
    if template_id == "bundle":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            readme = (
                "WorkWise Career Hub — ATS Resume Blueprint 2026 Bundle\n"
                "====================================================\n\n"
                "Included Templates:\n"
                "1. Software Engineer & Cloud Architect (.rtf / Word & .txt)\n"
                "2. UI/UX & Product Designer (.rtf / Word & .txt)\n"
                "3. Engineering Manager & Tech Lead (.rtf / Word & .txt)\n\n"
                "ATS 2026 Golden Rules:\n"
                "- Keep margins between 0.5 and 1.0 inch.\n"
                "- Use standard font hierarchies (Arial, Calibri, Helvetica).\n"
                "- Avoid tables, multi-column text boxes, and complex graphics in parsing regions.\n"
                "- Use the Google formula for bullet points: Accomplished [X], measured by [Y], by doing [Z].\n"
            )
            zf.writestr("README_ATS_2026_GUIDE.txt", readme)
            for key, tpl in RESUME_TEMPLATES.items():
                rtf_bytes = _create_rtf_from_text(tpl["text_content"])
                zf.writestr(f"{tpl['filename_prefix']}.doc", rtf_bytes)
                zf.writestr(f"{tpl['filename_prefix']}.txt", tpl["text_content"].encode("utf-8"))
        buffer.seek(0)
        return (
            buffer.getvalue(),
            "WorkWise_2026_ATS_Resume_Blueprint_Complete_Bundle.zip",
            "application/zip",
        )

    template = RESUME_TEMPLATES.get(template_id, RESUME_TEMPLATES["tech"])
    if file_format == "txt":
        return (
            template["text_content"].encode("utf-8"),
            f"{template['filename_prefix']}.txt",
            "text/plain; charset=utf-8",
        )
    content = _create_rtf_from_text(template["text_content"])
    return (
        content,
        f"{template['filename_prefix']}.doc",
        "application/msword",
    )


def get_interview_guide_download() -> tuple[bytes, str, str]:
    lines = [
        "=" * 80,
        "WORKWISE CAREER HUB — 2026 INTERVIEW MASTERY HANDBOOK",
        "Ace Behavioral, System Design, Live Technical & Negotiation Rounds",
        "=" * 80 + "\n",
    ]
    for cat in INTERVIEW_CATEGORIES:
        lines.append(f"\n{'=' * 80}")
        lines.append(f"SECTION: {cat['name'].upper()}")
        lines.append(f"Description: {cat['description']}")
        lines.append(f"{'=' * 80}\n")
        for idx, q in enumerate(cat["questions"], start=1):
            lines.append(f"Q{idx}. {q['title']}")
            lines.append(f'Prompt: "{q["question"]}"')
            lines.append(f"What Assessors Look For: {q['assessor_lookout']}\n")
            lines.append("MODEL ANSWER BREAKDOWN:")
            for step, detail in q["star_breakdown"].items():
                lines.append(f"  [{step}]:")
                for subline in detail.split("\n"):
                    lines.append(f"    {subline}")
            lines.append(f"\nPRO-TIP: {q['pro_tip']}")
            lines.append(f"\n{'-' * 80}\n")
    content = "\n".join(lines).encode("utf-8")
    return (
        content,
        "WorkWise_2026_Interview_Mastery_Complete_Guide.txt",
        "text/plain; charset=utf-8",
    )
