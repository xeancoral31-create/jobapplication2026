"""core/career_resources.py — Real ATS Resume Templates & Interview Mastery Content."""
import io
import zipfile

RESUME_TEMPLATES = {'design': {'badge': 'Design & Product',
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
          'title': 'Software Engineer & Cloud Architect'}}


INTERVIEW_CATEGORIES = [{'description': 'Master behavioral and situational questions using the Situation, Task, Action, Result framework.',
  'icon': '🎯',
  'id': 'behavioral',
  'name': 'Behavioral (STAR Method)',
  'questions': [{'assessor_lookout': 'Evaluates composure, systematic root-cause troubleshooting, clear stakeholder '
                                     'communication, and prevention mindset.',
                 'pro_tip': 'Never blame a teammate or vendor. Focus on accountability, systemic improvements, and '
                            'quantitative business recovery metrics.',
                 'question': 'Tell me about a time you handled a high-stakes production incident or critical bug under '
                             'tight deadlines.',
                 'star_breakdown': {'Action': 'I immediately triggered our incident protocol, instituted a rollback to '
                                              'the last verified stable release, and spun up hotfix worker pods. Using '
                                              'Datadog logs and PostgreSQL slow query traces, I isolated a dead-lock '
                                              'in our inventory table. I wrote an atomic query migration patch and '
                                              'verified it in staging before deploying.',
                                    'Result': 'Resolved the outage in 22 minutes, recovered $68,000 in queued orders '
                                              'without customer data loss, and implemented an automated database index '
                                              'check that prevented recurrence.',
                                    'Situation': 'During Black Friday peak traffic at my previous company, our payment '
                                                 'processing webhook failed, blocking 15% of inbound checkout '
                                                 'transactions.',
                                    'Task': 'As the on-call engineer, I had to stop financial loss, diagnose the '
                                            'failure within our 30-minute SLA, and keep executive stakeholders '
                                            'updated.'},
                 'title': 'Resolving a Critical Production Outage Under Pressure'},
                {'assessor_lookout': 'Tests emotional intelligence, data-driven negotiation, business focus over ego, '
                                     'and commitment once decisions are made.',
                 'pro_tip': 'Frame disagreements around customer impact, team velocity, and system risk rather than '
                            'personal coding preferences.',
                 'question': 'Describe a situation where you had a major disagreement with a team lead or product '
                             'manager regarding technical direction.',
                 'star_breakdown': {'Action': "Instead of saying 'no', I prepared a 1-page comparison matrix showing "
                                              'that embedding it in the monolith would risk 99.9% uptime for core '
                                              'billing. I proposed using a managed pub/sub service (Stream/Firebase) '
                                              'for MVP validation, which satisfied both the timeline and system '
                                              'stability.',
                                    'Result': 'The product lead embraced the managed approach, launching 4 days ahead '
                                              'of schedule with zero operational overhead on our core backend '
                                              'infrastructure.',
                                    'Situation': 'A product lead requested building a bespoke real-time in-app chat '
                                                 'using raw WebSockets directly into our core monolith to hit an '
                                                 'aggressive 3-week deadline.',
                                    'Task': 'I needed to voice serious architectural concerns regarding database '
                                            'connection pool exhaustion without being perceived as an impediment to '
                                            'product velocity.'},
                 'title': 'Constructive Disagreement on Technical Architecture'},
                {'assessor_lookout': 'Checks humility, early risk communication, post-mortem methodology, and '
                                     'resilience.',
                 'pro_tip': 'Choose a real failure with genuine stakes, and emphasize the systemic lesson that '
                            'permanently altered your engineering habits.',
                 'question': "Tell me about a project that didn't go as planned or missed an important deadline, and "
                             'what you learned.',
                 'star_breakdown': {'Action': 'I immediately raised the blocker to our engineering director and '
                                              'product counterpart with 3 mitigation options rather than waiting until '
                                              'deadline day. We staged the release into Phase 1 (core metrics) and '
                                              'Phase 2 (historical exports), keeping the main customer promise intact '
                                              'while I restructured data partitioning.',
                                    'Result': 'Phase 1 launched on time, and Phase 2 followed 10 days later with 3x '
                                              'query speeds. The team adopted early load-testing benchmarks into our '
                                              'definition of done.',
                                    'Situation': 'We committed to delivering a multi-tenant client reporting dashboard '
                                                 'by the end of Q2. Two weeks before launch, we discovered severe '
                                                 'query degradation with large datasets.',
                                    'Task': 'I was responsible for the data aggregation backend and had to address the '
                                            'timeline gap transparently.'},
                 'title': 'Overcoming Project Failure or Missed Deadlines'}]},
 {'description': 'Architect scalable, fault-tolerant, and high-performance cloud applications.',
  'icon': '🏗️',
  'id': 'system_design',
  'name': 'System Design & Architecture',
  'questions': [{'assessor_lookout': 'Assesses asynchronous message queues (Kafka, SQS), worker scaling, idempotency, '
                                     'failure retries, and multi-tenant rate limits.',
                 'pro_tip': 'Always clarify scale requirements first: read vs. write ratios, acceptable delivery '
                            'latency, and idempotency guarantees.',
                 'question': 'How would you design a distributed notification engine that sends push, email, and SMS '
                             'notifications at 10M messages per minute with rate limiting?',
                 'star_breakdown': {'Architecture Blueprint': '1. API Gateway / Ingestion: Lightweight Go/FastAPI '
                                                              'endpoints validating payloads and writing immediately '
                                                              'to Apache Kafka partitioned by user ID.\n'
                                                              '2. Rate Limiting & User Preferences: Redis token bucket '
                                                              'algorithm checking user opt-outs and channel quiet '
                                                              'hours.\n'
                                                              '3. Fan-out Worker Pools: Autoscaling Celery/Go workers '
                                                              'pulling from priority topics (e.g. Critical 2FA > '
                                                              'Marketing).\n'
                                                              '4. Vendor Abstraction Layer: Multi-provider failover '
                                                              '(Twilio, SendGrid, APNS) with circuit breakers.\n'
                                                              '5. Idempotency & Deduplication: SHA-256 hash of payload '
                                                              'stored in Redis with 24-hour TTL.',
                                    'Key Trade-offs': 'Eventual consistency over immediate consistency; prioritized '
                                                      'queueing ensures transactional alerts are never blocked by bulk '
                                                      'marketing campaigns.'},
                 'title': 'Designing a High-Throughput Notification Service (10M/min)'},
                {'assessor_lookout': 'Evaluates command of EXPLAIN ANALYZE, indexing strategies, connection pooling, '
                                     'and locking behavior.',
                 'pro_tip': 'Mention caution when adding indexes in production—remember that indexes speed up reads '
                            'but add write overhead on INSERT/UPDATE.',
                 'question': 'A production endpoint is timing out during peak hours. How do you systematically '
                             'identify and fix the database bottleneck?',
                 'star_breakdown': {'Result Outcome': 'Transformed an 8.4-second full table scan into an '
                                                      '18-millisecond index seek, dropping database CPU from 92% to '
                                                      '24%.',
                                    'Troubleshooting Protocol': '1. Telemetry: Check APM traces to confirm database '
                                                                'execution time vs. application serialization time.\n'
                                                                '2. Query Analysis: Run EXPLAIN (ANALYZE, BUFFERS) to '
                                                                'detect sequential table scans, high shared hit '
                                                                'ratios, and nested loop joins on unindexed foreign '
                                                                'keys.\n'
                                                                '3. Index Optimization: Add appropriate composite or '
                                                                'partial B-Tree indexes matching filter & sort '
                                                                'clauses.\n'
                                                                '4. Connection Health: Inspect pg_stat_activity to '
                                                                'check for long-running transactions holding row/table '
                                                                'locks.\n'
                                                                '5. Architecture Remediation: Implement Redis caching '
                                                                'for read-heavy static data or route reporting queries '
                                                                'to a read replica.'},
                 'title': 'Diagnosing and Resolving PostgreSQL Query Bottlenecks'}]},
 {'description': 'Strategies for live coding, algorithms, clean code principles, and whiteboard discussions.',
  'icon': '⚡',
  'id': 'technical',
  'name': 'Live Technical & Problem Solving',
  'questions': [{'assessor_lookout': 'Assesses concurrency models: Optimistic Locking vs. Pessimistic Locking, atomic '
                                     'transactions, and distributed locks.',
                 'pro_tip': 'Explain the trade-offs: Pessimistic locking guarantees safety but can bottleneck '
                            'throughput; optimistic locking scales reads but requires retry logic.',
                 'question': 'How do you prevent double-spending or stock overselling in concurrent e-commerce or '
                             'booking environments?',
                 'star_breakdown': {'Core Solution Patterns': '1. Database Level (Pessimistic): SELECT ... FOR UPDATE '
                                                              'within an explicit database transaction to lock the '
                                                              'exact inventory row.\n'
                                                              '2. Optimistic Locking: Use a version column (UPDATE '
                                                              'item SET stock = stock - 1, version = version + 1 WHERE '
                                                              'id = ? AND version = ?).\n'
                                                              '3. Atomic SQL Expressions: UPDATE items SET stock = '
                                                              'stock - 1 WHERE id = ? AND stock >= 1; check affected '
                                                              'rows.\n'
                                                              '4. Distributed Locks: Use Redis Redlock for '
                                                              'cross-service distributed resource synchronization.',
                                    'Recommended Strategy': 'For high-concurrency ticket/seat reservation, combine '
                                                            'atomic SQL updates with a 10-minute Redis reservation '
                                                            'lock.'},
                 'title': 'Handling Race Conditions in Financial & Inventory Transactions'}]},
 {'description': 'Tactfully handle compensation discussions and ask high-signal questions that impress executive '
                 'interviewers.',
  'icon': '💼',
  'id': 'negotiation',
  'name': 'Salary Negotiation & Closing Questions',
  'questions': [{'assessor_lookout': 'Tests negotiation poise, market awareness, and ability to keep options open '
                                     'until the offer stage.',
                 'pro_tip': 'Never give a single fixed number; always provide a data-backed range with a focus on '
                            'total compensation (base, bonus, equity, remote stipend).',
                 'question': 'How do you respond when a recruiter asks for your target number early in the interview '
                             'process?',
                 'star_breakdown': {'Model Response': "'I want to ensure the compensation is aligned with the market "
                                                      'value of the impact I will deliver in this role. Based on my '
                                                      'research for a Senior Engineer in this market and the tech '
                                                      'stack, I understand the range is typically between $130,000 and '
                                                      '$160,000 base, plus equity and benefits. However, finding the '
                                                      'right technical culture and scope is my highest priority. What '
                                                      "is the budgeted range for this position?'",
                                    'Strategic Purpose': 'Anchors in market data while turning the question back to '
                                                         'the company to reveal their budgeted bracket.'},
                 'title': "Tactfully Answering: 'What are your salary expectations?'"},
                {'assessor_lookout': 'Assesses intellectual curiosity, understanding of business priorities, and '
                                     'cultural alignment.',
                 'pro_tip': 'Avoid generic questions easily found on the company website. Ask questions that reveal '
                            'day-to-day engineering culture and team autonomy.',
                 'question': 'What questions should you ask at the end of an interview to stand out as a top '
                             'candidate?',
                 'star_breakdown': {'Top 3 Questions': "1. 'What does success look like for this role in the first 90 "
                                                       'days, and what is the biggest technical blocker standing in '
                                                       "the way today?'\n"
                                                       "2. 'How does your engineering team manage the trade-off "
                                                       'between shipping new product features and addressing technical '
                                                       "debt?'\n"
                                                       "3. 'Can you walk me through the most recent incident or failed "
                                                       "release and how the post-mortem was conducted?'"},
                 'title': 'High-Signal Closing Questions to Ask the Hiring Team'}]}]


